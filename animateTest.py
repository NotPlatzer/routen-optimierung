import json
from sim import simulate
with open("map_config.json", "r") as f:
    map_config = json.load(f)

laster = 3

baustellen = map_config["baustellen"]
if len(baustellen.keys()) > 1:
    raise ValueError(
        "More than one baustelle detected. Please ensure there is one baustelle per map."
    )

# Run simulation (simErgebnis is a list of trucks, each a list of events [state_code, start, end])
simErgebnis = simulate(
    laster, baustellen["A"]["größe"], map_config["distances"]["Aw"]["duration"]
)

locations = {marker["label"]: marker["location"] for marker in map_config["markers"]}

polylines = {}
for k in map_config["routes"].keys():
    polylines[k] = map_config["routes"][k]["polyline"]


def process_truck_route(route, start_time=0):
    """
    Given a truck route (a list of [code, duration] segments) and a starting time,
    returns a list of tuples (time, (lat, lon)) for each minute.
    """
    timeline = []
    current_time = start_time

    for segment in route:
        code, duration = segment
        # Duration is in minutes
        if len(code) == 1:
            # Stationary: Get the coordinate for that location.
            coord = locations[code]
            # Append the same coordinate for each minute
            for minute in range(int(duration)):
                timeline.append((current_time + minute, coord))
            current_time += duration

        else:
            # Moving along a polyline: Get the list of coordinates.
            polyline = polylines[code]
            num_points = len(polyline)
            if num_points < 2:
                # If the polyline has one coordinate, just treat it as stationary.
                for minute in range(int(duration)):
                    timeline.append((current_time + minute, polyline[0]))
                current_time += duration
            else:
                # Interpolate: each interval takes duration/(num_points - 1) minutes.
                time_interval = duration / (num_points - 1)
                for i, coord in enumerate(polyline):
                    timeline.append((current_time + i * time_interval, coord))
                current_time += duration
    return timeline


# Suppose trucks_data is your list of truck routes (each is a list of segments).
# Process each truck route to get its timeline (list of (time, (lat,lon)) tuples)
truck_timelines = [process_truck_route(route) for route in simErgebnis]
open("truck_timelines.json", "w").write(json.dumps(truck_timelines, indent=4))
