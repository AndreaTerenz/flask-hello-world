from flask import Flask
from flask_sock import Sock

app = Flask(__name__)

@app.route('/')
def hello_world():
    print("calogero")
    return 'Hello, World!'
