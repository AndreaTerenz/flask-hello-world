import shortuuid

shortuuid.set_alphabet("0123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")

lobbies = {}
users = {}

def create_lobby(initial_user : str):
    if user_to_lobby(initial_user):
        return ""

    lobby_id = shortuuid.ShortUUID().random(length=8)
    lobbies[lobby_id] = [initial_user]
    users[initial_user] = lobby_id
    return lobby_id

def join_lobby(user: str, lobby_id: str):
    lobby = lobbies.get(lobby_id)
    if not lobby:
        return False

    lobby[users].append(user)
    return True

def user_to_lobby(user: str):
    return users.get(user)