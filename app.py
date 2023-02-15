import time

import simple_websocket
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
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    count = 0
    while True:
        try:
            data = ws.receive()
            print(data)
            ws.send(f"Echo: {data}")
            count += 1
        except simple_websocket.ConnectionClosed:
            print("Connection closed")
            return ""