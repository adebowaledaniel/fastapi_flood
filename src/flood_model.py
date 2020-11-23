"""SAR-FLOOD MAPPING USING A CHANGE DETECTION APPROACH

  Within this script SAR Sentinel-1 is being used to generate a flood extent map. A change
  detection approach was chosen, where a before- and after-flood event image will be compared.
  Sentinel-1 GRD imagery is being used. Ground Range Detected imagery includes the following
  preprocessing steps: Thermal-Noise Removal, Radiometric calibration, Terrain-correction
  hence only a Speckle filter needs to be applied in the preprocessing.
"""
import ee

# Extract date from meta data
def dates(imgcol):
    range = imgcol.reduceColumns(ee.Reducer.minMax(), ["system:time_start"])
    ee_min = ee.Date(range.get('min')).format('YYYY-MM-dd').getInfo()
    ee_max = ee.Date(range.get('max')).format('YYYY-MM-dd').getInfo()
    printed = "from %s to %s" % (ee_min, ee_max)
    return printed


def db_creator(base_period , flood_period, geometry, polarization="VH",
               pass_direction="DESCENDING", quiet=False):

    # rename selected geometry feature
    aoi = ee.FeatureCollection(ee.Geometry.Polygon(geometry))

    # Load and filter Sentinel-1 GRD data by predefined parameters
    collection = ee.ImageCollection("COPERNICUS/S1_GRD")\
                  .filter(ee.Filter.eq("instrumentMode", "IW"))\
                  .filter(ee.Filter.listContains("transmitterReceiverPolarisation", polarization))\
                  .filter(ee.Filter.eq("orbitProperties_pass",pass_direction))\
                  .filter(ee.Filter.eq("resolution_meters",10)) \
                  .filterBounds(aoi)\
                  .select(polarization)
    # .filter(ee.Filter.eq('relativeOrbitNumber_start', relative_orbit)) \

    # Select images by predefined dates
    before_collection = collection.filterDate(base_period[0], base_period[1])
    after_collection = collection.filterDate(flood_period[0], flood_period[1])

    if quiet:
        # print dates of before images to console
        before_count = before_collection.size().getInfo()
        print("Tiles selected: Before Flood (%s) \n %s" % (before_count, dates(before_collection)))

        # print dates of after images to console
        after_count = before_collection.size().getInfo()
        print("Tiles selected: After Flood  (%s) \n %s" % (after_count, dates(after_collection)))

    # Create a mosaic of selected tiles and clip to study area
    before = before_collection.mosaic().clip(aoi)
    after = after_collection.mosaic().clip(aoi)

    # Apply reduce the radar speckle by smoothing
    smoothing_radius = 50
    before_filtered = before.focal_mean(smoothing_radius, "circle", "meters")
    after_filtered = after.focal_mean(smoothing_radius, "circle", "meters")
    dict_preprocessing = dict(before_flood=before_filtered,
                              after_flood=after_filtered,
                              base_period=base_period,
                              flood_period=flood_period,
                              aoi=aoi,
                              polarization=polarization)
    return dict_preprocessing


def flood_estimation(dict_db, difference_threshold=1.25, stats=True):

    before_filtered = dict_db["before_flood"]
    after_filtered = dict_db["after_flood"]
    polarization = dict_db["polarization"]
    aoi = dict_db["aoi"]

    # Calculate the difference between the before and after images
    difference = after_filtered.divide(before_filtered)

    # Apply the predefined difference-threshold and create the flood extent mask
    threshold = difference_threshold
    difference_binary = difference.gt(threshold)

    # Refine flood result using additional datasets
    #    Include JRC layer on surface water seasonality to mask flood pixels from areas
    #    of "permanent" water (where there is water > 10 months of the year)
    swater = ee.Image('JRC/GSW1_0/GlobalSurfaceWater').select('seasonality')
    swater_mask = swater.gte(10).updateMask(swater.gte(10))

    # Flooded layer where perennial water bodies (water > 10 mo/yr) is assigned a 0 value
    flooded_mask = difference_binary.where(swater_mask,0)
    # final flooded area without pixels in perennial waterbodies
    flooded = flooded_mask.updateMask(flooded_mask)

    # Compute connectivity of pixels to eliminate those connected to 8 or fewer neighbours
    # This operation reduces noise of the flood extent product
    connections = flooded.connectedPixelCount()
    flooded = flooded.updateMask(connections.gte(8))

    # Mask out areas with more than 5 percent slope using a Digital Elevation Model
    # TODO! >>>>>>>>>>>>>>>>>>>>>>><<
    DEM = ee.Image('WWF/HydroSHEDS/03VFDEM')
    terrain = ee.Algorithms.Terrain(DEM)
    slope = terrain.select('slope')
    flooded = flooded.updateMask(slope.lt(5))
    # >>>>>>>>>>>>>>>>>>>>>>><<
    dict_db.update({"flood_results": flooded}) # add flood mask results to the db

    if stats:
        # Calculate flood extent area
        # Create a raster layer containing the area information of each pixel
        flood_pixelarea = flooded.select(polarization).multiply(ee.Image.pixelArea())

        # Sum the areas of flooded pixels
        # default is set to 'bestEffort: true' in order to reduce compuation time, for a more
        # accurate result set bestEffort to false and increase 'maxPixels'.
        flood_stats = flood_pixelarea.reduceRegion(
          reducer=ee.Reducer.sum(),
          geometry=aoi,
          scale=10, # native resolution
          bestEffort=True
        )

        # Convert the flood extent to hectares (area calculations are originally given in meters)
        flood_area_ha = flood_stats\
          .getNumber(polarization)\
          .divide(10000)\
          .round() \
          .getInfo()
        dict_db.update({"flood_area_stats":flood_area_ha}) # add flood stats results to the db
    return dict_db

def population_exposed(dict_db):
    aoi = dict_db["aoi"]
    flooded = dict_db["flood_results"]

    # Load JRC Global Human Settlement Popluation Density layer
    # Resolution: 250. Number of people per cell is given.
    population_count = ee.Image('JRC/GHSL/P2016/POP_GPW_GLOBE_V1/2015').clip(aoi)

    # Calculate the amount of exposed population
    # get GHSL projection
    GHSLprojection = population_count.projection()

    # Reproject flood layer to GHSL scale
    flooded_res1 = flooded.reproject(crs=GHSLprojection)

    # Create a raster showing exposed population only using the resampled flood layer
    population_exposed = population_count.updateMask(flooded_res1) \
        .updateMask(population_count)

    # Sum pixel values of exposed population raster
    stats = population_exposed.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=aoi,
        scale=250,
        maxPixels=1e9
    )

    # get number of exposed people as integer
    number_pp_exposed = stats.getNumber('population_count').round().getInfo()
    dict_db.update({"population_exposed_stats": number_pp_exposed})
    return dict_db

def cropland_exposed(dict_db):
    after_end = dict_db["flood_period"][1]
    aoi = dict_db["aoi"]
    flooded = dict_db["flood_results"]
    polarization = dict_db["polarization"]

    # using MODIS Land Cover Type Yearly Global 500m
    # filter image collection by the most up-to-date MODIS Land Cover product
    LC = ee.ImageCollection('MODIS/006/MCD12Q1') \
        .filterDate('2014-01-01', after_end) \
        .sort('system:index', False) \
        .select("LC_Type1") \
        .first() \
        .clip(aoi)
    dict_db.update({"MODIS_landuse": LC})
    # Extract only cropland pixels using the classes cropland (>60%) and Cropland/Natural
    # Vegetation Mosaics: mosaics of small-scale cultivation 40-60% incl. natural vegetation
    cropmask = LC.eq(12).Or(LC.eq(14))
    cropland = LC.updateMask(cropmask)

    # get MODIS projection
    MODISprojection = LC.projection()

    # Reproject flood layer to MODIS scale
    flooded_res = flooded.reproject(crs=MODISprojection)
    dict_db.update({"flood_results_MODISprojection": flooded_res})

    # Calculate affected cropland using the resampled flood layer
    cropland_affected = flooded_res.updateMask(cropland)

    # get pixel area of affected cropland layer
    crop_pixelarea = cropland_affected.multiply(ee.Image.pixelArea())  # calcuate the area of each pixel

    # sum pixels of affected cropland layer
    crop_stats = crop_pixelarea.reduceRegion(
        reducer=ee.Reducer.sum(),  # sum all pixels with area information
        geometry=aoi,
        scale=500,
        maxPixels=1e9
    )

    # convert area to hectares
    crop_area_ha = crop_stats \
        .getNumber(polarization) \
        .divide(10000) \
        .round() \
        .getInfo()
    dict_db.update({'croparea_exposed_stats': crop_area_ha})
    return dict_db


def urban_exposed(dict_db):
    LC = dict_db["MODIS_landuse"]
    flooded_res = dict_db["flood_results_MODISprojection"]
    aoi = dict_db["aoi"]

    # Using the same MODIS Land Cover Product
    # Filter urban areas
    urbanmask = LC.eq(13)
    urban = LC.updateMask(urbanmask)

    # Calculate affected urban areas using the resampled flood layer
    urban_affected = urban.mask(flooded_res).updateMask(urban)

    # get pixel area of affected urban layer
    urban_pixelarea = urban_affected.multiply(ee.Image.pixelArea())  # calcuate the area of each pixel

    # sum pixels of affected cropland layer
    urban_stats = urban_pixelarea.reduceRegion(
        reducer=ee.Reducer.sum(),  # sum all pixels with area information
        geometry=aoi,
        scale=500,
        bestEffort=True
    )

    # convert area to hectares
    urban_area_ha = urban_stats \
        .getNumber('LC_Type1') \
        .divide(10000) \
        .round() \
        .getInfo()
    dict_db.update({"urban_area_exposed_stats": urban_area_ha})
    return dict_db
