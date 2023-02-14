from flask import Flask
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

@app.route('/')
def hello_world():
    print("calogero")
    return 'Hello, World!'

@sock.route('/ws')
def echo(ws):
    while True:
        data = ws.receive()
        print(data)
        ws.send(data)