import requests

BASE_URL = "http://localhost:8000"

def create_user(username, password):
    url = f"{BASE_URL}/users/"
    payload = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"User '{username}' created successfully!")
    else:
        print(f"Error: {response.json()['detail']}")

def login_user(username, password):
    url = f"{BASE_URL}/token"
    payload = {
        "username": username,
        "password": password
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"Login successful! Access token: {token}")
    else:
        print(f"Error: {response.json()['detail']}")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Create a new user")
    print("2. Login")

    choice = input("Enter your choice (1 or 2): ")

    if choice == "1":
        username = input("Enter username: ")
        password = input("Enter password: ")
        create_user(username, password)
    elif choice == "2":
        username = input("Enter username: ")
        password = input("Enter password: ")
        login_user(username, password)
    else:
        print("Invalid choice")
