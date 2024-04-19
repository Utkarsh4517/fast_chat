from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import List, Dict
import asyncio
import time
import uvicorn

# Database setup
DATABASE_URL = "sqlite:///./chat.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    messages = relationship("Message", back_populates="sender")

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    creator_id = Column(Integer, ForeignKey('users.id'))
    creator = relationship("User")
    
    messages = relationship("Message", back_populates="room")

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))
    
    sender = relationship("User", back_populates="messages")
    room = relationship("Room", back_populates="messages")

    timestamp = Column(Integer, default=int(time.time()))

Base.metadata.create_all(bind=engine)

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

class UserResponse(BaseModel):
    message: str
    user_id: int

app = FastAPI()

room_connections: Dict[int, List[WebSocket]] = {}

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        db.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return UserResponse(message="User created successfully", user_id=new_user.id)

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

@app.websocket("/rooms/{room_id}")
async def join_room(room_id: int, websocket: WebSocket):
    await websocket.accept()
    db = SessionLocal()
    previous_messages = db.query(Message).filter(Message.room_id == room_id).order_by(Message.timestamp).all()
    for message in previous_messages:
        sender = db.query(User).filter(User.id == message.sender_id).first()
        await websocket.send_text(f"{sender.username}: {message.content}")
    if room_id not in room_connections:
        room_connections[room_id] = []
    
    room_connections[room_id].append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            sender_username, message_content = data.split(": ", 1)
            sender = db.query(User).filter(User.username == sender_username).first()
            new_message = Message(content=message_content, room_id=room_id, sender_id=sender.id)
            db.add(new_message)
            db.commit()
            for connection in room_connections[room_id]:
                await connection.send_text(data)
    except WebSocketDisconnect:
        room_connections[room_id].remove(websocket)
        if not room_connections[room_id]:
            del room_connections[room_id]
    
    db.close()

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
