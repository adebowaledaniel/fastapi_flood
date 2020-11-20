import ee

def simple_eemap():
    image = ee.Image('CGIAR/SRTM90_V4')
    map_id = ee.data.getMapId({'image':image})
    return map_id["tile_fetcher"].url_format

def replace_line(file_name, line_num, text):
    with open(file_name, 'r') as f:
        lines = f.readlines()
        lines[line_num] = text
    with open(file_name, 'w') as fw:    
        fw.writelines(lines)        