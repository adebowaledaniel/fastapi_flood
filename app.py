from src.map_display import *
from src.init_ee import ee_Initialize 
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Init Earth Engine
ee_Initialize()

app = FastAPI()
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
    basemap_addtext = "        //earthengine_space;\n" 
    replace_line('templates/ee_map.html', 24, basemap_addtext)
    return templates.TemplateResponse("map_template.html", {"request": request})

@app.post('/map')
def form_post(request: Request):
    basemap = simple_eemap()
    basemap_addtext = "        L.tileLayer('%s').addTo(map);\n" % basemap
    replace_line('templates/ee_map.html', 24, basemap_addtext)
    return templates.TemplateResponse('map_template.html', {'request': request})

