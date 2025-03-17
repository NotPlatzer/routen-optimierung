import folium


def generateMap(location: list, zoom: int, baustellen: list, AufbereitungsWerk: list):
    m = folium.Map(location=location, zoom_start=zoom)
    for baustelle in baustellen:
        folium.Marker(
            location=[baustelle["lat"], baustelle["lon"]],
            popup=baustelle["größe"],
            icon=folium.Icon(color="blue"),
        ).add_to(m)
    folium.Marker(
        location=AufbereitungsWerk,
        popup="Aufbereitungswerk",
        icon=folium.Icon(color="red"),
    ).add_to(m)

    return m
