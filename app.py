import os
from icecream import ic

if os.getenv("DEPLOYED"):
    ic.disable()

import json, lobby
from simple_websocket import ConnectionClosed
from flask import Flask
from flask_sock import Sock

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
                packet = on_new_game(ws, msg_body)
            elif msg_type == "JOIN_GAME":
                packet = on_join_game(ws, msg_body)

            ws.send(packet)
        except ConnectionClosed:
            print("Connection closed")
            on_player_left(ws)
            return ""

def on_new_game(ws, msg) -> str:
    user_id = msg["user_id"]

    try:
        lobby_id, players = lobby.add_user(name=user_id, socket=ws)

        return json.dumps({
            "type": "NEW_GAME_OK",
            "lobby_id": lobby_id,
            "players": [user_id]
        })
    except lobby.UserAlreadyExists:
        return ""

def on_join_game(ws, msg) -> str:
    user_id = msg["user_id"]
    lobby_id = msg.get("lobby_id", "")

    if lobby_id == "":
        return ""

    try:
        lobby_id, players = lobby.add_user(name=user_id, socket=ws, lobby_id=lobby_id)

        on_player_joined(user_id, lobby_id)

        return json.dumps({
            "type": "JOIN_GAME_OK",
            "lobby_id": lobby_id,
            "players": players
        })
    except lobby.LobbyNotFound | lobby.UserAlreadyExists:
        return ""

def on_player_joined(new_user_id, lobby_id):
    lobby_packet = {
        "type": "PLAYER_JOINED",
        "new_player": new_user_id
    }
    lobby.emit_to_lobby(lobby_id, json.dumps(lobby_packet), excepts=[new_user_id])

def on_player_left(ws):
    user_id = lobby.socket_to_user(ws)
    lobby_id = lobby.user_to_lobby(ic(user_id))
    left = lobby.remove_user(user_id)

    if left > 0:
        lobby_packet = {
            "type": "PLAYER_LEFT",
            "players": lobby.users_in_lobby(lobby_id)
        }
        lobby.emit_to_lobby(lobby_id, json.dumps(lobby_packet))
    else:
        print(f"Lobby {lobby_id} closed")