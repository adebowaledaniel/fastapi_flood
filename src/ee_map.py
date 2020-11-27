import ee
from typing import Optional
from src import utils

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