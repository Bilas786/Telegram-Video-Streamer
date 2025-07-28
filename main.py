from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pyrogram import Client
import os

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

app = FastAPI()
client = Client("streamer", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.on_event("startup")
async def startup():
    await client.start()

@app.on_event("shutdown")
async def shutdown():
    await client.stop()

@app.get("/")
async def home():
    return {"status": "Telegram Video Streamer is Working!"}

@app.get("/stream/{message_id}")
async def stream_video(message_id: int):
    try:
        msg = await client.get_messages(-1002734341593, message_id)
        if not msg or not msg.video and not msg.document:
            raise HTTPException(status_code=404, detail="Video not found")

        return StreamingResponse(
            client.stream_media(msg),
            media_type="video/mp4"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
