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

# ✅ Your private channel invite link
CHANNEL_INVITE_LINK = "https://t.me/+tjAFFEsryVs3YTU1"

client = Client("streamer", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)


@app.get("/")
def home():
    return {"status": "✅ Telegram Video Streamer is Working!"}


@app.get("/stream/{message_id}")
async def stream_video(message_id: int):
    await client.start()
    try:
        # ✅ Join your private channel (registers the peer)
        await client.join_chat(CHANNEL_INVITE_LINK)

        # ✅ Fetch the specific video message
        message = await client.get_messages(CHANNEL_INVITE_LINK, message_id)

        # ✅ Download video to memory and stream
        file_stream = io.BytesIO()
        await client.download_media(message, file_stream)
        file_stream.seek(0)

        return StreamingResponse(file_stream, media_type="video/mp4")

    except Exception as e:
        return {"error": str(e)}

    finally:
        await client.stop()
