from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
from typing import List, Dict
from passlib.context import CryptContext
import uvicorn
import asyncio

# Database setup
DATABASE_URL = "sqlite:///./chat.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

# Room model
class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    creator_id = Column(Integer, ForeignKey('users.id'))
    creator = relationship("User")

# Message model
class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))

Base.metadata.create_all(bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str

class RoomCreate(BaseModel):
    name: str
    creator_id: int

class MessageCreate(BaseModel):
    content: str
    room_id: int
    sender_id: int

# FastAPI app
app = FastAPI()

# In-memory storage for WebSocket connections
room_connections: Dict[int, List[WebSocket]] = {}

# Create user endpoint
@app.post("/users/", response_model=dict)
async def create_user(user: UserCreate):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        db.close()
        return JSONResponse(content={"error": "Username already exists"}, status_code=400)
    
    hashed_password = pwd_context.hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return {"message": "User created successfully", "user_id": new_user.id}

# Create room endpoint
@app.post("/rooms/", response_model=dict)
async def create_room(room: RoomCreate):
    db = SessionLocal()
    user = db.query(User).filter(User.id == room.creator_id).first()
    if not user:
        db.close()
        return JSONResponse(content={"error": "User not found"}, status_code=400)
    
    new_room = Room(name=room.name, creator_id=room.creator_id)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    db.close()
    return {"message": "Room created successfully", "room_id": new_room.id}

# Join room endpoint (WebSocket)
@app.websocket("/rooms/{room_id}")
async def join_room(room_id: int, websocket: WebSocket):
    await websocket.accept()
    if room_id not in room_connections:
        room_connections[room_id] = []
    
    # Add the connection to the room
    room_connections[room_id].append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast the message to all connected clients in the room
            for connection in room_connections[room_id]:
                if connection != websocket:
                    await connection.send_text(data)
    except WebSocketDisconnect:
        # Remove the disconnected client
        room_connections[room_id].remove(websocket)
        # If the room has no more connections, remove it from the dictionary
        if not room_connections[room_id]:
            del room_connections[room_id]

# Get room details endpoint
@app.get("/rooms/{room_id}", response_model=dict)
async def get_room_details(room_id: int):
    db = SessionLocal()
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        db.close()
        return JSONResponse(content={"error": "Room not found"}, status_code=400)
    
    creator = db.query(User).filter(User.id == room.creator_id).first()
    db.close()
    return {
        "room_id": room.id,
        "name": room.name,
        "creator": creator.username
    }

# Start the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
