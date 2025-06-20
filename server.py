from flask import Flask, render_template, jsonify
from flask_restx import Api, Resource

app = Flask(__name__)

# Define standard custom routes BEFORE Api init
@app.route("/")
def index():
    return jsonify({"message": "ahoy captain! welcome aboard! xD"})

@app.route("/docs")
def scalar_docs():
    return render_template("index.html")


# Now initialize Api, specifying doc to avoid re-mounting /
api = Api(app, version="1.0", title="Weather API", doc="/swagger")

ns = api.namespace("weather", description="Weather endpoints")


@ns.route("/")
class Weather(Resource):
    def get(self):
        return {"temperature": "32°C", "condition": "Sunny"}


if __name__ == "__main__":
    app.run(debug=True, port=5050)
