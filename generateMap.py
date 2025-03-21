import folium
import requests
import json
import copy

def decode_polyline(polyline_str):
    index, lat, lng, coordinates = 0, 0, 0, []
    while index < len(polyline_str):
        shift, result = 0, 0
        while True:
            byte = ord(polyline_str[index]) - 63
            index += 1
            result |= (byte & 0x1F) << shift
            shift += 5
            if byte < 0x20:
                break
        lat += ~(result >> 1) if result & 1 else (result >> 1)

        shift, result = 0, 0
        while True:
            byte = ord(polyline_str[index]) - 63
            index += 1
            result |= (byte & 0x1F) << shift
            shift += 5
            if byte < 0x20:
                break
        lng += ~(result >> 1) if result & 1 else (result >> 1)

        coordinates.append((lat / 1e5, lng / 1e5))

    return coordinates

def calcRoute(pointA, pointB):
    body = {
        "coordinates": [pointA, pointB],
    }
    headers = {
        "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
        "Authorization": "5b3ce3597851110001cf624865218d6b2b804a69bde78e798286446f",
        "Content-Type": "application/json; charset=utf-8",
    }
    call = requests.post(
        "https://api.openrouteservice.org/v2/directions/driving-car/json",
        json=body,
        headers=headers,
    )
    if call.ok == False:
        print(call.text)
    j = json.loads(call.text)["routes"][0]
    return [j["summary"], decode_polyline(j["geometry"])]

def generateMap(location: list, zoom: int, baustellen: list, AufbereitungsWerk: list, Zentrale: list):
    indexedBaustellen = {}
    routes = {} #routes['AB'] = [distanz, polyline]

    for i,baustelle in enumerate(baustellen):
        indexedBaustellen[chr(ord('A') + i)] = baustelle
    for start in indexedBaustellen.keys():
        routes[start + "w"] = calcRoute([indexedBaustellen[start]["lon"], indexedBaustellen[start]["lat"]], AufbereitungsWerk[::-1])
        routes[start + "z"] = calcRoute([indexedBaustellen[start]["lon"], indexedBaustellen[start]["lat"]], Zentrale[::-1])
        umgedreht_w = copy.deepcopy(routes[start + "w"])
        umgedreht_w[1] = umgedreht_w[1][::-1]
        routes["w" + start] = umgedreht_w
        umgedreht_z = copy.deepcopy(routes[start + "z"])
        umgedreht_z[1] = umgedreht_z[1][::-1]
        routes["z" + start] = umgedreht_z
        for ziel in indexedBaustellen.keys():
            if start != ziel:
                if routes.get(start + ziel) == None and routes.get(ziel + start) == None:
                    routes[start + ziel] = calcRoute([indexedBaustellen[start]["lon"], indexedBaustellen[start]["lat"]], [indexedBaustellen[ziel]["lon"], indexedBaustellen[ziel]["lat"]])
                    routes[ziel + start] = routes[start + ziel]
    m = folium.Map(location=location, zoom_start=zoom)

    config = {}
    config["map_settings"] = {"location": location, "zoom": zoom}
    config["markers"] = []
    config["routes"] = {}
    config["distances"] = {}
    config["polylines"] = []
    config["baustellen"] = indexedBaustellen

    for char_label, baustelle in indexedBaustellen.items():
        marker = {
            "location": [baustelle["lat"], baustelle["lon"]],
            "popup": f"{char_label}: {baustelle['größe']}",
            "icon_color": "blue",
            "type": "baustelle",
            "label": char_label,
        }
        config["markers"].append(marker)
        folium.Marker(
            location=marker["location"],
            popup=marker["popup"],
            icon=folium.Icon(color="blue"),
        ).add_to(m)
        folium.Marker(
            location=[baustelle["lat"], baustelle["lon"]],
            popup=f"{char_label}: {baustelle['größe']}",  # Include label in popup
            icon=folium.Icon(color="blue"),
        ).add_to(m)

    marker_aw = {
        "location": AufbereitungsWerk,
        "popup": "Aufbereitungswerk",
        "icon_color": "red",
        "type": "AufbereitungsWerk",
        "label": "w"
    }
    config["markers"].append(marker_aw)
    
    marker_z = {
        "location": Zentrale,
        "popup": "Zentrale",
        "icon_color": "green",
        "type": "Zentrale",
        "label": "z"
    }
    config["markers"].append(marker_z)

    folium.Marker(
        location=AufbereitungsWerk,
        popup="Aufbereitungswerk",
        icon=folium.Icon(color="red"),
    ).add_to(m)
    folium.Marker(
        location=Zentrale,
        popup="Zentrale",
        icon=folium.Icon(color="green"),
    ).add_to(m)
    distances = {}

    for key in routes.keys():
        distance = routes[key][0]
        polyline = routes[key][1]
        config["routes"][key] = {"distance": distance, "polyline": polyline}
        config["distances"][key] = distance
        folium.PolyLine(polyline, color="green").add_to(m)

    print(distances)
    with open("map_config.json", "w") as file:
        json.dump(config, file, indent=4)
        
    return m