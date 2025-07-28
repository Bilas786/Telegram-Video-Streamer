from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pyrogram import Client
import os
import asyncio
import io

app = FastAPI()

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

CHANNEL_ID = -1002734341593  # ✅ Your actual channel ID

client = Client("streamer", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.get("/")
def home():
    return {"status": "✅ Telegram Video Streamer is Running"}

@app.get("/stream/{message_id}")
async def stream_video(message_id: int):
    await client.start()
    try:
        # ✅ Get message from private channel
        message = await client.get_messages(CHANNEL_ID, message_id)

        file_stream = io.BytesIO()
        await client.download_media(message, file_stream)
        file_stream.seek(0)

        return StreamingResponse(file_stream, media_type="video/mp4")
    except Exception as e:
        return {"error": str(e)}
    finally:
        await client.stop()
