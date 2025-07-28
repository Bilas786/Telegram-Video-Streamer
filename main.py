from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pyrogram import Client
import os
import io

app = FastAPI()

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

CHANNEL_ID = -1002734341593
INVITE_LINK = "https://t.me/+tjAFFEsryVs3YTU1"

client = Client("streamer", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.get("/")
def home():
    return {"status": "✅ Telegram Video Streamer is Running"}

@app.get("/stream/{message_id}")
async def stream_video(message_id: int):
    await client.start()
    try:
        # ✅ Safely try to join the private channel
        try:
            await client.join_chat(INVITE_LINK)
        except Exception as e:
            if "USER_ALREADY_PARTICIPANT" in str(e):
                pass
            else:
                raise e

        # ✅ Now fetch the message
        message = await client.get_messages(CHANNEL_ID, message_id)

        file_stream = io.BytesIO()
        await client.download_media(message, file_stream)
        file_stream.seek(0)

        return StreamingResponse(file_stream, media_type="video/mp4")
    except Exception as e:
        return {"error": str(e)}
    finally:
        await client.stop()
