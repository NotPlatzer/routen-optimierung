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
    baustellen = [{"lat": "46.655027", "lon": "11.157470", "größe": 100}, {"lat": "46.231694", "lon": "11.172098", "größe": 100}]
    AufbereitungsWerk = [46.463926, 11.337877]
    print(baustellen)
    zoom = 12

    m = generateMap([lat, lon], zoom, baustellen, AufbereitungsWerk)
    return m.get_root().render()

if __name__ == "__main__":
    app.run(debug=True, host="172.31.98.182")
