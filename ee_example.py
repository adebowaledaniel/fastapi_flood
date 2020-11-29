from src import  flood_model
import ee
ee.Initialize()

# base period
init_start = "2019-03-01"
init_last = "2019-03-10"
base_period = (init_start, init_last)

# Now set the same parameters for AFTER the flood.
flood_start = "2019-03-10"
flood_last = "2019-03-23"
flood_period = (flood_start, flood_last)

xmin = 12.923 
ymin = 47.819
xmax = 13.067
ymax = 47.875
geometry = ee.Geometry.Rectangle(xmin, ymin, xmax, ymax)
difference_threshold = 1.25

dict_db = flood_model.db_creator(base_period, flood_period, geometry)
flood_added = flood_model.flood_estimation(dict_db=dict_db)
pop_added = flood_model.population_exposed(flood_added)
cropland_added = flood_model.cropland_exposed(pop_added)
urban_added = flood_model.urban_exposed(cropland_added)

flood_model.display(image = urban_added["flood_results"])
