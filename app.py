from flask import Flask, render_template, request
import folium
from generateMap import generateMap

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/map")
def map():
    lat = request.args.get("lat", default=46.492328, type=float)
    lon = request.args.get("lon", default=11.266533, type=float)
    zoom = 12

    m = generateMap([lat, lon], zoom)
    return m.get_root().render()


if __name__ == "__main__":
    app.run(debug=True, host="172.31.98.182")
