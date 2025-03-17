from flask import Flask
import folium

app = Flask(__name__)

# flask run --host=172.31.98.182

@app.route("/")
def home():
    m = folium.Map(location=[46.492328, 11.266533], zoom_start=10)
    return m.get_root().render()


if __name__ == "__main__":
    app.run(debug=True, host="172.31.98.182")
