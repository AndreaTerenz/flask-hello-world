import json, events, os
from icecream import ic
from lobby import add_user, UserAlreadyExists, LobbyNotFound
from simple_websocket import ConnectionClosed
from flask import Flask
from flask_sock import Sock

if os.getenv("DEPLOYED"):
    ic.disable()

app = Flask(__name__)
sock = Sock(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@sock.route("/game-socket")
def game_socket(ws):
    while True:
        try:
            data = json.loads(ws.receive())
            msg_type = data.get("type")
            msg_body = data.get("body")

            if (msg_type is None) or (msg_body is None):
                ws.send("")
                continue

            packet = f"Echo: {data}"

            # FOR FUCK'S SAKE, RENDER UPDATE TO 3.10 I WANNA USE MATCH AAAAAAAAA
            if msg_type == "NEW_GAME":
                packet = events.emit_event("NEW_GAME", [ws, msg_body])
            elif msg_type == "JOIN_GAME":
                packet = events.emit_event("JOIN_GAME", [ws, msg_body])

            ws.send(packet)
        except ConnectionClosed:
            print("Connection closed")
            return ""

@events.on("NEW_GAME", make_main=True)
def on_new_game(data) -> str:
    ws = data[0]
    msg = data[1]

    user_id = msg["user_id"]

    try:
        lobby_id, _ = add_user(name=user_id, socket=ws)

        return json.dumps({
            "lobby_id": lobby_id,
            "players": [user_id]
        })
    except UserAlreadyExists:
        return ""

@events.on("JOIN_GAME", make_main=True)
def on_join_game(data) -> str:
    ws = data[0]
    msg = data[1]

    user_id = msg["user_id"]
    lobby_id = msg.get("lobby_id", "")

    if lobby_id == "":
        return ""

    try:
        lobby_id, players = add_user(name=user_id, socket=ws, lobby_id=lobby_id)

        return json.dumps({
            "lobby_id": lobby_id,
            "players": players
        })
    except LobbyNotFound | UserAlreadyExists:
        return ""