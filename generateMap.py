import folium

def generateMap(location: list, zoom: int): 
    m = folium.Map(location=location, zoom_start=zoom)
    return m