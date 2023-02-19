import json
from typing import Union

import shortuuid
from game import Game
from icecream import ic

LOBBY_ID_LEN = 6
LOBBY_ID_ALPHABET = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ"

# Key: Lobby ID
# Value: {
#   "state": <Game object>
#   "players": [<IDs of users in lobby>]
# }
lobbies = {}

# Key: User ID
# Value: {
#   "ws": <socket obj>
#   "lobby": <lobby ID>
# }
users = {}

def user_exists(user: str):
    return users.get(user) is not None

def lobby_exists(lobby_id: str):
    return lobbies.get(lobby_id) is not None

def add_user(name: str, socket, lobby_id: str = ""):
    if user_exists(name):
        raise UserAlreadyExists(name)

    if lobby_id == "":
        lobby_id = shortuuid.ShortUUID(alphabet=LOBBY_ID_ALPHABET).random(length=LOBBY_ID_LEN)
        lobbies[lobby_id] = {
            "state": Game(),
            "players": [name],
        }
    elif lobbies.get(lobby_id):
        if len(users_in_lobby(lobby_id)) == 2:
            raise LobbyIsFull(lobby_id)

        lobbies[lobby_id]["players"].append(name)
    else:
        raise LobbyNotFound(lobby_id)

    users[name] = {
        "lobby": lobby_id,
        "ws": socket
    }

    return lobby_id, users_in_lobby(lobby_id)

def remove_user(user_id: str):
    """
    Remove a user from its lobby
    :param user_id: ID of the user to be removed
    :return: Number of users left in the lobby
    """
    if not user_exists(user_id):
        raise UserNotFound(user_id)

    lobby_id = users[user_id]["lobby"]
    left = len(lobbies[lobby_id]) - 1

    lobbies[lobby_id].remove(user_id)
    del users[user_id]

    return left

def user_to_lobby(user: str):
    if not user_exists(user):
        return ""

    return users[user]["lobby"]

def user_role(user: str):
    if not user_exists(user):
        return Game.EMPTY

    lobby_id = user_to_lobby(user)
    players = lobbies[lobby_id]["players"]

    return Game.X if user == players[0] else Game.O

def role_to_user(lobby_id: str, role: int):
    if not lobby_exists(lobby_id):
        return ""

    players = users_in_lobby(lobby_id)
    if role == Game.X:
        return players[0]
    elif role == Game.O:
        return players[1]

    return ""

def lobby_to_game(lobby_id: str):
    if not lobby_exists(lobby_id):
        return None

    return lobbies[lobby_id]["state"]

def socket_to_user(ws):
    tmp = [u for u in users.keys() if users[u]["ws"] == ws]
    return tmp[0]

def emit_to_user(username, data):
    if not user_exists(username):
        raise UserNotFound(username)

    ws = users[username]["ws"]
    ws.send(data)

def emit_to_lobby(lobby_id, data: Union[str, dict], excepts=None):
    if not lobby_exists(lobby_id):
        raise LobbyNotFound(lobby_id)
    if excepts is None:
        excepts = []

    if type(data) is dict:
        data = json.dumps(data)

    targets = [u for u in users_in_lobby(lobby_id) if not(u in excepts)]
    for user in targets:
        emit_to_user(user, data)

def users_in_lobby(lobby_id):
    if not lobby_exists(lobby_id):
        raise LobbyNotFound(lobby_id)

    return lobbies[lobby_id]["players"]

def lobby_is_empty(lobby_id):
    if not lobby_exists(lobby_id):
        raise LobbyNotFound(lobby_id)

    return len(lobbies[lobby_id]) <= 0

##################### EXCEPTIONS

class LobbyException(BaseException):
    """Generic lobby-related exception"""
    def __init__(self, lobby_id):
        self.lobby_id = lobby_id

class LobbyNotFound(LobbyException):
    """Raised when trying to join a non-existing lobby"""
    pass

class LobbyAlreadyExists(LobbyException):
    """Raised when trying to create a lobby that already exists"""
    pass

class LobbyIsFull(LobbyException):
    """Raised when trying to add too many players to a lobby"""
    def __str__(self):
        return f"{self.lobby_id} ({users_in_lobby(self.lobby_id)})"

class UserException(BaseException):
    """Generic user-related exception"""
    def __init__(self, username):
        self.username = username

class UserNotFound(UserException):
    """Raised when trying to access a non-existing user"""
    pass

class UserAlreadyExists(UserException):
    """Raised when trying to add an already present user"""
    pass

class UserNotInLobby(UserException, LobbyException):
    """Raised when there's a mismatch between user_id and lobby"""
    def __init__(self, username, lobby):
        self.username = username
        self.lobby = lobby