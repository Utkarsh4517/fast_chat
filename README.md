# Fast Chat CLI Tool

A command-line interface (CLI) tool for interacting with a chat application built using FastAPI. This tool allows users to create users, create rooms, get room details, and join rooms for chatting and many more (under development).

## Table of Contents

- [Features](#features)
- [Setup](#setup)
  - [Installation](#installation)
  - [Running the FastAPI App](#running-the-fastapi-app)
  - [Running the CLI](#running-the-cli)
- [Usage](#usage)
  - [Creating a New User](#creating-a-new-user)
  - [Creating a New Room](#creating-a-new-room)
  - [Getting Room Details](#getting-room-details)
  - [Joining a Room](#joining-a-room)
- [Database](#database)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Management**: Create new users with usernames and passwords.
- **Room Management**: Create new chat rooms with room names and creator IDs.
- **Room Details**: Retrieve details of existing chat rooms.
- **Chatting**: Join existing chat rooms and start chatting with other users.

## Setup

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Utkarsh4517/fast_chat.git
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Running the FastAPI App

1. Navigate to the `app` directory:

    ```bash
    cd fast_chat/app
    ```

2. Run the FastAPI app using Uvicorn:

    ```bash
    uvicorn app:app --reload
    ```

### Running the CLI

1. Navigate to the `cli` directory:

    ```bash
    cd fast_chat/cli
    ```

2. Run the CLI:

    ```bash
    python cli.py <command>
    ```

## Usage

### Creating a New User

To create a new user, run the following command:

```bash
python cli.py create_user
```

Follow the prompts to enter the username and password for the new user.

### Creating a New Room

To create a new room, run the following command:

```bash
python cli.py create_room
```

Follow the prompts to enter the room name and creator ID for the new room.

### Getting Room Details

To get details of a specific room, run the following command:

```bash
python cli.py get_room_details
```

Follow the prompts to enter the room ID.

### Joining a Room

To join a room and start chatting, run the following command:

```bash
python cli.py join_room
```

Follow the prompts to enter your username and the room ID.

## Database

The project uses SQLite as the database. The database file is named `chat.db` and contains tables for storing users, rooms, and messages.

## License

This project is licensed under the [MIT License](LICENSE).