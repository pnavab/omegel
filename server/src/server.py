import sqlite3
import json
from dataclasses import dataclass
import ast
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import db

@dataclass
class ConnectionManager:
    conn = None
    database = None
    def __init__(self) -> None:
        self.active_connections: dict = {}
        self.database = db.db()
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        id = str(uuid.uuid4())
        print(id)
        self.active_connections[id] = websocket
        
        await self.send_message_to(websocket, json.dumps({ "type": "connect", "id": id }))
    
    def disconnect(self, websocket: WebSocket):
        id = self.find_connection_id(websocket)
        del self.active_connections[id]

    def find_connection_id(self, websocket: WebSocket):
        val_list = list(self.active_connections.values())
        key_list = list(self.active_connections.keys())
        id = val_list.index(websocket)
        return key_list[id]
    
    async def send_message_to(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)
connection_manager = ConnectionManager()

@app.websocket_route("/messaging")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received data {data}")
            copy = ast.literal_eval(data)
            connection_manager.database.write_message(copy["userID"], copy["text"])
            await connection_manager.broadcast(data)
    except WebSocketDisconnect:
        print(f"client disconnected")
        id = connection_manager.disconnect(websocket)
        await connection_manager.broadcast(json.dumps({ "type": "disconnected", "id": id }))

@app.get("/prevmessages")
def prev_messages():
    return {"messages" : connection_manager.database.get_messages()}

if __name__ == "__main__":
    uvicorn.run("server:app", port=8000, reload=True)
