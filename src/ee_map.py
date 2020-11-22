import ee
from typing import Optional
from src import utils
 
try:
    ee.Initialize()        
except Exception as e:
    print(e)
    return False    


def display(geoviz: Optional = None) -> str:
    """ Display a basic Earth Engine map
    Returns:
        str: earthengine tiles googleapis
    """
    if geoviz is None:
        geoviz = dict()
    image = ee.Image('CGIAR/SRTM90_V4')
    geoviz.update({'image':image})
    map_id = ee.data.getMapId(geoviz)
    map_tile = map_id["tile_fetcher"].url_format
    return map_tile


def position(x, y, zoom) -> bool:
    """Restart simple leaflet JS file (Remove EE tiles)
    Returns:
        bool: If the line was replaced will return True.
    """
    set_xyz = (y, x, zoom)
    basemap_addtext = "        var map = L.map('mapid').setView([%s, %s], %s);\n" % set_xyz
    utils.replace_line('templates/ee_map.html', 21, basemap_addtext)


def restart() -> bool:
    """Restart simple leaflet JS file (Remove EE tiles)
    Returns:
        bool: If the line was replaced will return True.
    """
    basemap_addtext = "        //earthengine_space;\n" 
    utils.replace_line('templates/ee_map.html', 24, basemap_addtext)
    return True
        
def addTile(geoviz: Optional = None) -> bool:
    basemap = display(geoviz)
    basemap_addtext = "        L.tileLayer('%s').addTo(map);\n" % basemap
    utils.replace_line('templates/ee_map.html', 24, basemap_addtext)
    return True
