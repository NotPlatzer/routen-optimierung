from flask import Flask, render_template, request
import folium
from generateMap import generateMap
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
        [45.145850, 11.825148],
        [45.201835, 11.598046],
        [45.070134, 11.977711],
    ]
    baustellen = [
        {"lat": coords[0][0], "lon": coords[0][1], "größe": 100},
        {"lat": coords[1][0], "lon": coords[1][1], "größe": 100},
        {"lat": coords[2][0], "lon": coords[2][1], "größe": 100},
        {"lat": coords[3][0], "lon": coords[3][1], "größe": 100},
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
    from folium import MacroElement
    from jinja2 import Template

    # Load configuration from file
    with open("map_config.json", "r") as file:
        config = json.load(file)

    # Base map settings
    location = config.get("map_settings", {}).get("location", [0, 0])
    zoom = config.get("map_settings", {}).get("zoom", 13)
    m = folium.Map(location=location, zoom_start=zoom)

    # Add static markers (if any)
    for marker in config.get("markers", []):
        icon_color = marker.get("icon_color", "blue")
        folium.Marker(
            location=marker.get("location"),
            popup=marker.get("popup"),
            icon=folium.Icon(color=icon_color),
        ).add_to(m)

    # Draw static routes for visual reference
    for key, route in config.get("routes", {}).items():
        polyline = route.get("polyline")
        if polyline:
            folium.PolyLine(polyline, color="green").add_to(m)

    # Function to compute the haversine distance between two [lat, lon] points.
    def haversine(coord1, coord2):
        R = 6371000  # Earth radius in meters
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    # Prepare animated routes data
    # For each route, compute durations for each segment proportionally.
    routes_data = []
    for key, route in config.get("routes", {}).items():
        polyline = route.get("polyline", [])
        if not polyline or len(polyline) < 2:
            continue

        # Get the real trip duration (in seconds) if provided.
        route_info = route.get("distance", {})
        real_duration = route_info.get("duration")
        if real_duration is not None:
            # Convert real duration (in seconds) to animation time (in seconds)
            # where 1 sec animation = 1 real hour.
            eineSekistStunden = 1/12
            total_anim_time_sec = real_duration / (eineSekistStunden*3600.0)
        else:
            # Fallback: assign 1 second per segment if no duration is provided.
            total_anim_time_sec = len(polyline) - 1

        # Total animation time in milliseconds for the plugin.
        total_anim_time_ms = total_anim_time_sec * 1000

        # Compute distances between consecutive points.
        segment_distances = []
        total_distance = 0
        for i in range(len(polyline) - 1):
            d = haversine(polyline[i], polyline[i + 1])
            segment_distances.append(d)
            total_distance += d

        # If total_distance is 0, fallback to equal segment durations.
        if total_distance == 0:
            durations = [total_anim_time_ms / (len(polyline) - 1)] * (len(polyline) - 1)
        else:
            durations = [
                (d / total_distance) * total_anim_time_ms for d in segment_distances
            ]

        routes_data.append({"route": polyline, "durations": durations})

    # If there are any animated routes, add them using a custom MacroElement.
    if routes_data:

        class MultiMovingMarkers(MacroElement):
            _template = Template(
                """
                {% macro script(this, kwargs) %}
                function addMovingMarkers() {
                    var routesData = {{ this.routes_data }};
                    routesData.forEach(function(item, index) {
                        var marker = L.Marker.movingMarker(item.route, item.durations, {autostart: true});
                        marker.addTo({{ this._parent.get_name() }});
                    });
                }
                // Load the MovingMarker plugin if it hasn't been loaded yet.
                if (typeof L.Marker.movingMarker === 'undefined') {
                    var script = document.createElement('script');
                    script.type = 'text/javascript';
                    script.src = 'https://rawcdn.githack.com/ewoken/Leaflet.MovingMarker/master/MovingMarker.js';
                    script.onload = function() {
                        addMovingMarkers();
                    };
                    document.getElementsByTagName('head')[0].appendChild(script);
                } else {
                    addMovingMarkers();
                }
                {% endmacro %}
            """
            )

            def __init__(self, routes_data):
                super(MultiMovingMarkers, self).__init__()
                self._name = "MultiMovingMarkers"
                self.routes_data = routes_data

        m.add_child(MultiMovingMarkers(routes_data=routes_data))

    return m.get_root().render()


if __name__ == "__main__":
    app.run(debug=True, host="172.31.98.182")
