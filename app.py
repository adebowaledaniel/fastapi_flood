from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from src import utils
from src.flood_model import *
import ee, os
import asyncio
import time

# Init Earth Engine
utils.load_credentials()
ee.Initialize()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000"
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "year":2020})

@app.get("/methodology")
async def methodology(request: Request):
    return templates.TemplateResponse("methodology.html", {"request": request, "year":2020})

@app.get("/map")
async def map(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})

@app.post("/map")
async def flood_model(
    request: Request,
    xmin:float = Form(...), 
    ymin:float = Form(...),
    xmax:float = Form(...),
    ymax:float = Form(...),
    init_start:str = Form(...),
    init_last:str = Form(...),
    flood_start:str = Form(...),
    flood_last:str = Form(...),
    action:str = Form(...),
    threshold:float = Form(...)
    ):
    
    xmean = (xmin + xmax)/2
    ymean = (ymin + ymax)/2
    
    # 1. Create geometry
    ee_rectangle = ee.Geometry.Rectangle(xmin, ymin, xmax, ymax)
    
    # 2. Create range dates
    base_period = (init_start, init_last)
    flood_period = (flood_start, flood_last)
    
    # 3. Run the flood model    
    dict_db = db_creator(base_period, flood_period, ee_rectangle)
    flood_added = flood_estimation(dict_db, difference_threshold=threshold)
    
    if action == "display":
        pop_added = population_exposed(flood_added)
        cropland_added = cropland_exposed(pop_added)
        urban_added = urban_exposed(cropland_added)
        
        # 4. Upload gee tileid
        tileids = display(urban_added)
    
        return templates.TemplateResponse(
            "map.html", 
            {
                "request": request,
                "flood_extent": urban_added["flood_area_stats"],
                "people_exposed": urban_added["population_exposed_stats"],
                "cropland_exposed": urban_added["croparea_exposed_stats"],
                "urband_exposed": urban_added["urban_area_exposed_stats"],
                "before_waterlog": tileids["before_flood"],
                "after_waterlog": tileids["after_flood"],
                "waterlog_results": tileids["s1_fresults_id"],
                "xmin": xmin,
                "ymin": ymin,
                "ymax": ymax,
                "xmax": xmax,
                "xmean": xmean,                            
                "ymean": ymean,
                "init_start":init_start,
                "init_last":init_last,
                "flood_start":flood_start,
                "flood_last":flood_last
            }
        )
    elif action == "download":
        # Remove previous zipfiles
        zip_files = searching_all_files(pattern="\.zip")
        [os.remove(zip_file) for zip_file in zip_files]
        
        # 1. Create a shapefile        
        geo_file = "waterlog_area_%s.shp" % (time.strftime("%Y%m%d%H%M%S", time.gmtime()))
        geo_file_search = "waterlog_area_%s" % (time.strftime("%Y%m%d%H%M%S", time.gmtime()))
        geo_file_zip = 'waterlog_area_%s.zip' % (time.strftime("%Y%m%d%H%M%S", time.gmtime()))
        final_flood_area = raster_to_vector(flood_added["flood_results"], ee_rectangle)
        final_flood_area_gpd = gpd.GeoDataFrame.from_features(final_flood_area["features"])    
        final_flood_area_gpd.to_file(geo_file)
        # 2. Create a zip file and delete shapefile
        shapefile_to_zip = searching_all_files(pattern=geo_file_search)
        with ZipFile(geo_file_zip, 'w') as zipObj2:
            for item in shapefile_to_zip:
                zipObj2.write(os.path.basename(item))
                os.remove(item)
        time.sleep(1)
        return FileResponse(geo_file_zip, media_type="application/zip", filename=geo_file_zip)
    
