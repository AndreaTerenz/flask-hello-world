import simple_websocket
from lobby import create_lobby, join_lobby
from flask import Flask, Response
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route("/create-lobby/<user_id>", methods=["GET"])
def create_lobby_route(user_id):
    lobby_id = create_lobby(initial_user=user_id)
    return Response(lobby_id, status= (200 if lobby_id != "" else 400))

@app.route("/join-lobby/<user_id>/<lobby_id>", methods=["GET"])
def join_lobby_route(user_id, lobby_id):
    ok = join_lobby(user=user_id, lobby_id=lobby_id)
    return Response(lobby_id, status= (200 if ok else 400))

@sock.route('/echo')
def echo(ws):
    count = 0
    print("AUAUAUAUAUA")
    while True:
        try:
            data = ws.receive()
            print(data)
            ws.send(f"Echo: {data}")
        except simple_websocket.ConnectionClosed:
            print("Connection closed")
            return ""

@sock.route("/ws")
def socket(ws):
    while True:
        try:
            data = ws.receive()
            print(data)
            ws.send(f"Echo: {data}")
        except simple_websocket.ConnectionClosed:
            print("Connection closed")
            return ""