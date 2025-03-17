from flask import Flask, render_template, request
import folium
from generateMap import generateMap
from collections import defaultdict
import re

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/map")
def map():
    baustellen = defaultdict(dict)
    pattern = re.compile(r"baustellen\[(\d+)\]\[(\w+)\]")
    lat = 46.492328
    lon = 11.266533
    # lon = request.args.get("lon", default=11.266533, type=float)
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

    m = generateMap([lat, lon], zoom, baustellen, AufbereitungsWerk)
    return m.get_root().render()

if __name__ == "__main__":
    app.run(debug=True, host="172.31.98.182")
