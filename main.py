import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pyrogram import Client
import asyncio

# Environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
CHAT_ID = int(os.getenv("CHAT_ID"))  # Example: -1002734341593

# Initialize FastAPI
app = FastAPI()

# Pyrogram client
client = Client("streamer", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# Start client
loop = asyncio.get_event_loop()
loop.run_until_complete(client.start())


@app.get("/")
def home():
    return {"message": "Telegram video streamer is working!"}


@app.get("/stream/{message_id}")
async def stream_video(message_id: int):
    try:
        msg = await client.get_messages(CHAT_ID, message_id)
        if not msg.video and not msg.document:
            raise HTTPException(status_code=404, detail="This message does not contain a video")

        file = await msg.download(in_memory=True)
        return StreamingResponse(file, media_type="video/mp4")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
