from flask import Flask, render_template, request, jsonify
import folium
from generateMap import generateMap
from sim import simulate
from collections import defaultdict
import re
import json

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
    Zentrale = [45.172380, 11.713497]
    zoom = 12

    m = generateMap(AufbereitungsWerk, zoom, baustellen, AufbereitungsWerk, Zentrale)

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
            var url = "/sim";
            window.location.href = url;
        }
    </script>
    """

    return m.get_root().render() + button_script

@app.route("/sim")
def sim():
    laster = 3

    # Load configuration containing routes, markers, etc.
    with open("map_config.json", "r") as f:
        map_config = json.load(f)

    baustellen = map_config["baustellen"]
    if len(baustellen.keys()) > 1:
        raise ValueError(
            "More than one baustelle detected. Please ensure there is one baustelle per map."
        )

    # Run simulation (simErgebnis is a list of trucks, each a list of events [state_code, start, end])
    simErgebnis = simulate(
        laster, baustellen["A"]["größe"], map_config["distances"]["Aw"]["duration"]
    )
    with open("ergebnisSim.json", "w") as f:
        f.write(json.dumps(simErgebnis))

    # Set up the base map.
    base_location = map_config.get("map_settings", {}).get("location", [0, 0])
    zoom = map_config.get("map_settings", {}).get("zoom", 13)
    m = folium.Map(location=base_location, zoom_start=zoom)

    # Add polylines.
    for key in map_config["routes"]:
        if key[0] == "w":
            m.add_child(
                folium.PolyLine(map_config["routes"][key]["polyline"], color="green")
            )
        if key[0] == "z":
            m.add_child(
                folium.PolyLine(
                    map_config["routes"][key]["polyline"], color="red", opacity=0.5
                )
            )
    # Add markers.
    for marker in map_config["markers"]:
        m.add_child(folium.Marker(marker["location"], popup=marker["popup"]))

    # Build lookups for state coordinates and routes.
    stateCoords = {
        marker["label"]: marker["location"] for marker in map_config["markers"]
    }
    
    lines = {}
    
    
    
    
    return m.get_root().render()

@app.route("/data")
def data():
    return -1
    

if __name__ == "__main__":
    app.run(debug=True, host="172.31.98.182")
