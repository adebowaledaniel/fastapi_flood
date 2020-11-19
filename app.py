from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "year":2020})

@app.get("/methodology", response_class=HTMLResponse)
async def methodology(request: Request):
    return templates.TemplateResponse("methodology.html", {"request": request, "year":2020})

@app.get("/flood_map", response_class=HTMLResponse)
async def flood_map(request: Request):
    return "hi"
