from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "Hello world"

app.