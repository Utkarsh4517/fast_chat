import requests
import websockets
import asyncio

BASE_URL = "http://localhost:8000"

# Function to create a new user
def create_user(username, password):
    url = f"{BASE_URL}/users/"
    payload = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        res = response.json()
        print("User created successfully.")
        print(res['user_id'])
    else:
        print(f"Error: {response.json().get('error')}")

# Function to create a new room
def create_room(name, creator_id):
    url = f"{BASE_URL}/rooms/"
    payload = {
        "name": name,
        "creator_id": creator_id
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        room_id = response.json().get("room_id")
        print(f"Room created successfully. Room ID: {room_id}")
        return room_id
    else:
        print(f"Error: {response.json().get('error')}")

# Function to get room details
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

# Function to join a room and start chat
async def join_room(username, room_id):
    websocket_url = f"ws://localhost:8000/rooms/{room_id}"
    async with websockets.connect(websocket_url) as websocket:
        print(f"Joined room {room_id}. You can start chatting now.")
        # Start a task to listen for incoming messages
        asyncio.create_task(listen_for_messages(websocket, username))
        while True:
            message = input(f"{username}: ")
            await websocket.send(message)

# Function to listen for incoming messages
async def listen_for_messages(websocket, username):
    async for message in websocket:
        print(message)

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Create a new user")
    print("2. Create a new room")
    print("3. Get room details")
    print("4. Join a room and chat")

    choice = input("Enter your choice (1-4): ")

    if choice == "1":
        username = input("Enter username: ")
        password = input("Enter password: ")
        create_user(username, password)
    elif choice == "2":
        name = input("Enter room name: ")
        creator_id = int(input("Enter creator ID: "))
        create_room(name, creator_id)
    elif choice == "3":
        room_id = int(input("Enter room ID: "))
        get_room_details(room_id)
    elif choice == "4":
        username = input("Enter username: ")
        room_id = int(input("Enter room ID: "))
        asyncio.run(join_room(username, room_id))
    else:
        print("Invalid choice.")
