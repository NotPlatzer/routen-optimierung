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
    from folium import MacroElement
    from jinja2 import Template

    with open("ergebnisSim.json", "r") as f:
        sim_data = json.load(f)

    # Load map configuration (which contains the polylines and possibly a location mapping)
    with open("map_config.json", "r") as f:
        map_config = json.load(f)

    # Set up the base map using map_config settings.
    base_location = map_config.get("map_settings", {}).get("location", [0, 0])
    zoom = map_config.get("map_settings", {}).get("zoom", 13)
    m = folium.Map(location=base_location, zoom_start=zoom)

    for key, route in map_config.get("routes", {}).items():
        polyline = route.get("polyline")
        if polyline:
            folium.PolyLine(polyline, color="blue", weight=5, opacity=0.5).add_to(m)

    # Assume that your map_config may also define a mapping of location labels to coordinates.
    # For example: "locations": { "A": [lat, lon], "B": [lat, lon], ... }
    locations_mapping = map_config.get("markers", {})

    # --- Step 1: Process simulation steps ---
    # Determine the number of trucks from the first simulation step.
    if not sim_data.get("schritte"):
        return m.get_root().render()
    num_trucks = len(sim_data["schritte"][0].get("laster", []))
    # For each truck, extract its location over time (using the "location" field).
    trucks_movements = []
    for truck_index in range(num_trucks):
        truck_locations = []
        for step in sim_data["schritte"]:
            truck = step.get("laster", [])[truck_index]
            loc_label = truck.get("location")
            # Only add if it changes (to avoid duplicates)
            if not truck_locations or truck_locations[-1] != loc_label:
                truck_locations.append(loc_label)
        trucks_movements.append(truck_locations)
    print("trucks_movements", trucks_movements)
    # --- Step 2: Build routes and durations per truck ---
    # Helper: Haversine distance (meters) between two [lat, lon] points.
    def haversine(coord1, coord2):
        R = 6371000  # Earth's radius in meters
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    # For each truck, convert its sequence of location labels to a combined polyline and durations.
    truck_routes = []
    for truck_seq in trucks_movements:
        combined_polyline = []
        combined_durations = []
        # Process each movement transition.
        for i in range(len(truck_seq) - 1):
            start_loc = truck_seq[i]
            end_loc = truck_seq[i+1]
            # We assume that the corresponding route key is the concatenation of start and end,
            # for example "AB" for movement from A to B.
            route_key = f"{start_loc}{end_loc}"
            route_data = map_config.get("routes", {}).get(route_key)
            if not route_data:
                # Optionally try the reverse key.
                route_key = f"{end_loc}{start_loc}"
                route_data = map_config.get("routes", {}).get(route_key)
            if not route_data:
                # If no route is found, try to use direct coordinates from the locations mapping.
                start_coord = locations_mapping.get(start_loc)
                end_coord = locations_mapping.get(end_loc)
                if start_coord and end_coord:
                    segment_polyline = [start_coord, end_coord]
                    # Use a default duration of 3600 seconds (1 hour) if not provided.
                    real_duration = 3600  
                else:
                    continue
            else:
                segment_polyline = route_data.get("polyline", [])
                # Get the real duration (in seconds) for this segment; default to 3600 if missing.
                real_duration = route_data.get("distance", {}).get("duration", 3600)
            # Compute the animation time for this segment.
            # With 1 sec animation = 1 real hour, we have:
            anim_time_ms = (real_duration / 3600.0) * 1000

            # Break the segment's polyline into its smaller segments and compute proportional durations.
            segment_distances = []
            total_distance = 0
            for j in range(len(segment_polyline) - 1):
                d = haversine(segment_polyline[j], segment_polyline[j+1])
                segment_distances.append(d)
                total_distance += d
            if total_distance == 0 or len(segment_polyline) < 2:
                durations = [anim_time_ms]
            else:
                durations = [(d / total_distance) * anim_time_ms for d in segment_distances]

            # Append the polyline to the combined route.
            # Avoid duplicating points where segments meet.
            if combined_polyline and segment_polyline:
                if combined_polyline[-1] == segment_polyline[0]:
                    combined_polyline.extend(segment_polyline[1:])
                else:
                    combined_polyline.extend(segment_polyline)
            else:
                combined_polyline.extend(segment_polyline)
            # Append the durations.
            combined_durations.extend(durations)
        # Only add if we have a valid route.
        if combined_polyline and combined_durations:
            truck_routes.append({
                "route": combined_polyline,
                "durations": combined_durations
            })

    # --- Step 3: Inject JavaScript to animate all truck markers ---
    if truck_routes:
        class MultiTruckMovingMarkers(MacroElement):
            _template = Template(u"""
                {% macro script(this, kwargs) %}
                function addTruckMovingMarkers() {
                    var truckRoutes = {{ this.truck_routes }};
                    truckRoutes.forEach(function(truck, idx) {
                        // Create a moving marker for each truck.
                        // You can customize options (e.g. different icons) per truck if desired.
                        var marker = L.Marker.movingMarker(truck.route, truck.durations, {autostart: true});
                        marker.addTo({{ this._parent.get_name() }});
                    });
                }
                // Ensure the MovingMarker plugin is loaded.
                if (typeof L.Marker.movingMarker === 'undefined') {
                    var script = document.createElement('script');
                    script.type = 'text/javascript';
                    script.src = 'https://rawcdn.githack.com/ewoken/Leaflet.MovingMarker/master/MovingMarker.js';
                    script.onload = function() {
                        addTruckMovingMarkers();
                    };
                    document.getElementsByTagName('head')[0].appendChild(script);
                } else {
                    addTruckMovingMarkers();
                }
                {% endmacro %}
            """)
            def __init__(self, truck_routes):
                super(MultiTruckMovingMarkers, self).__init__()
                self._name = 'MultiTruckMovingMarkers'
                self.truck_routes = truck_routes

        m.add_child(MultiTruckMovingMarkers(truck_routes=truck_routes))

    return m.get_root().render()



if __name__ == "__main__":
    app.run(debug=True, host="172.31.98.182")
