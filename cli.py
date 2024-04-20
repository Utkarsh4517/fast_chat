import argparse
import asyncio
import requests
import websockets

# CLI for interacting with the FastAPI app

BASE_URL = "http://localhost:8000"

# Creates a new user on the database
def create_user(username, password):
    url = f"{BASE_URL}/users/"
    payload = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"User created successfully. User ID: {data['user_id']}")
        return data['user_id']
    else:
        print(f"Error: {response.json().get('detail', 'Unknown error')}")
        return None

# Any user can create a new room, it requires a room name and the user ID or creator ID
def create_room(name, creator_id):
    url = f"{BASE_URL}/rooms/"
    payload = {
        "name": name,
        "creator_id": creator_id
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"Room created successfully. Room ID: {data['room_id']}")
        return data['room_id']
    else:
        print(f"Error: {response.json().get('error')}")

# Returns the details of any room present in the database
def get_room_details(room_id):
    url = f"{BASE_URL}/rooms/{room_id}"
    response = requests.get(url)
    if response.status_code == 200:
        room_details = response.json()
        print(f"Room ID: {room_details['room_id']}")
        print(f"Room Name: {room_details['name']}")
        print(f"Creator: {room_details['creator']}")
    else:
        print(f"Error: {response.json().get('error')}")

# WebSocket: Room
async def join_room(username, room_id):
    websocket_url = f"ws://localhost:8000/rooms/{room_id}"
    async with websockets.connect(websocket_url) as websocket:
        print(f"Joined room {room_id}. You can start chatting now.")
        asyncio.create_task(listen_for_messages(websocket))
        while True:
            message = input(f"{username}: ")
            await websocket.send(f"{username}: {message}")

async def listen_for_messages(websocket):
    async for message in websocket:
        print(message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CLI Chat Tool')
    parser.add_argument('action', choices=['create_user', 'create_room', 'get_room_details', 'join_room'],
                        help='Action to perform')
    args = parser.parse_args()

    if args.action == "create_user":
        username = input("Enter username: ")
        password = input("Enter password: ")
        create_user(username, password)
    elif args.action == "create_room":
        name = input("Enter room name: ")
        creator_id = int(input("Enter creator ID: "))
        create_room(name, creator_id)
    elif args.action == "get_room_details":
        room_id = int(input("Enter room ID: "))
        get_room_details(room_id)
    elif args.action == "join_room":
        username = input("Enter username: ")
        room_id = int(input("Enter room ID: "))
        asyncio.run(join_room(username, room_id))

