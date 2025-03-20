from flask import Flask, render_template, request
import folium
from folium.plugins import TimestampedGeoJson

from generateMap import generateMap
from sim import simulate
from collections import defaultdict
import re
import json
from folium import MacroElement
from jinja2 import Template
import datetime


app = Flask(__name__)


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/map")
def map():
    baustellen = defaultdict(dict)
    pattern = re.compile(r"baustellen\[(\d+)\]\[(\w+)\]")
    for key, value in request.args.items():
        match = pattern.match(key)
        if match:
            index = int(match.group(1))
            field = match.group(2)
            baustellen[index][field] = value
    baustellen = list(baustellen.values())
    coords = [
        [45.103130, 11.644913],
    ]
    baustellen = [
        {"lat": coords[0][0], "lon": coords[0][1], "größe": 100},
    ]
    AufbereitungsWerk = [45.142380, 11.783497]
    zoom = 12

    m = generateMap(AufbereitungsWerk, zoom, baustellen, AufbereitungsWerk)

    button_script = """
    <style>
        .custom-button {
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: white;
            border: 2px solid #ccc;
            padding: 8px 15px;
            font-size: 14px;
            cursor: pointer;
            z-index: 1000;
            border-radius: 5px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        }
        .custom-button:hover {
            background-color: #f0f0f0;
        }
    </style>

    <!-- The button that will redirect the page -->
    <button class="custom-button" onclick="redirectToNewRoute()">Click Me</button>

    <script>
        function redirectToNewRoute() {
            // Define your variables.
            var lat = 45.142380;
            var lon = 11.783497;
            var zoom = 12;
            
            // Construct the URL with query parameters.
            var url = "/sim"
            window.location.href = url;
        }
    </script>
    """

    return m.get_root().render() + button_script


@app.route("/sim")
def sim():
    import json
    import math
    import folium

    laster = 3

    # Load map configuration (which contains the polylines and possibly a location mapping)
    with open("map_config.json", "r") as f:
        map_config = json.load(f)

    baustellen = map_config["baustellen"]
    if len(baustellen.keys()) > 1:
        ValueError(
            "More than one baustelle detected. Please ensure there is one baustelle per map."
        )
    simErgebnis = simulate(
        laster, baustellen["A"]["größe"], map_config["distances"]["Aw"]["duration"]
    )
    open("ergebnisSim.json", "w").write(json.dumps(simErgebnis))
    # Set up the base map using map_config settings.
    base_location = map_config.get("map_settings", {}).get("location", [0, 0])
    zoom = map_config.get("map_settings", {}).get("zoom", 13)
    m = folium.Map(location=base_location, zoom_start=zoom)
    for k in map_config["routes"].keys():
        if k[0] == "w":
            m.add_child(
                folium.PolyLine(map_config["routes"][k]["polyline"], color="green")
            )
    for k in map_config["markers"]:
        m.add_child(folium.Marker(k["location"], popup=k["popup"]))

    routen = map_config["routes"]
    stateCoords = {}
    for k in map_config["markers"]:
        stateCoords[k["label"]] = k["location"]

    def get_movement_polyline(state):
        # Expecting route keys to match the movement state, e.g., "Aw" or "wA"
        route = map_config["routes"].get(state)
        if route is not None:
            return route["polyline"]  # Expecting a list of [lat, lon] pairs.
        return None

    # For waiting events, simply use the coordinate for that state.
    def get_coords(state):
        # For waiting events (state with a single letter) use stateCoords.
        if len(state) == 1:
            return stateCoords[state]
        # For movement events without a polyline fallback to the starting state's coordinate.
        return stateCoords[state[0]]

    # Prepare GeoJSON features.
    truck_events = simErgebnis  # List of trucks; here we animate the first truck.
    truck1 = truck_events[0]
    features = []
    base_time = datetime.datetime(2023, 1, 1)

    for event in truck1:
        state, start_time, stop_time = event
        if state in ["Aw", "wA"] and stop_time is not None:
            # Movement event: try to get the polyline for the route.
            polyline = get_movement_polyline(state)
            if polyline is not None and len(polyline) >= 2:
                duration = stop_time - start_time
                num_points = len(polyline)
                for i, coords in enumerate(polyline):
                    # Distribute timestamps evenly along the polyline.
                    time_offset = start_time + (duration * i / (num_points - 1))
                    event_time = base_time + datetime.timedelta(seconds=time_offset)
                    time_str = event_time.isoformat()
                    # GeoJSON requires [longitude, latitude]
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [coords[1], coords[0]],
                        },
                        "properties": {
                            "time": time_str,
                            "popup": f"State: {state} @ {round(time_offset,1)}s",
                        },
                    }
                    features.append(feature)
            else:
                # Fallback: if no polyline available, use single coordinate.
                coords = get_coords(state)
                event_time = base_time + datetime.timedelta(minutes=start_time)
                time_str = event_time.isoformat()
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [coords[1], coords[0]],
                    },
                    "properties": {
                        "time": time_str,
                        "popup": f"State: {state} @ {start_time}s",
                    },
                }
                features.append(feature)
        else:
            # Waiting event or movement with no stop_time: use single point.
            coords = get_coords(state)
            event_time = base_time + datetime.timedelta(minutes=start_time)
            time_str = event_time.isoformat()
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [coords[1], coords[0]],
                },
                "properties": {
                    "time": time_str,
                    "popup": f"State: {state} @ {start_time}s",
                },
            }
            features.append(feature)

    geojson_data = {"type": "FeatureCollection", "features": features}
    print(geojson_data)
    TimestampedGeoJson(
        data=geojson_data,
        period="PT1M",  # 1-second period increments
        duration="PT1M",
        add_last_point=False,
        auto_play=True,
        loop=False,
    ).add_to(m)

    return m.get_root().render()


if __name__ == "__main__":
    app.run(debug=True, host="172.31.98.182")
