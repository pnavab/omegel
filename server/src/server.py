from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()

@app.get("/")
async def blank():
    return {"message": "hello world"}

@app.websocket("/messaging")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  try:
    while True:
        data = await websocket.receive_text()
        print(f"Received data {data}")
        await websocket.send_text(data)
  except WebSocketDisconnect:
         print(f"client disconnected")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
