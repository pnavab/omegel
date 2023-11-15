from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import uuid
import json
from dataclasses import dataclass

@dataclass
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict = {}
    
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

connection_manager = ConnectionManager()


@app.websocket("/messaging")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received data {data}")
            await connection_manager.broadcast(data)
    except WebSocketDisconnect:
        print(f"client disconnected")
        id = connection_manager.disconnect(websocket)
        await connection_manager.broadcast(json.dumps({ "type": "disconnected", "id": id }))

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
