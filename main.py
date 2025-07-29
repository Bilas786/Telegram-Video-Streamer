from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pyrogram import Client
from pyrogram.errors import PeerIdInvalid
import os
import asyncio

app = FastAPI()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

client = Client("streamer", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)


@app.on_event("startup")
async def startup_event():
    await client.start()


@app.on_event("shutdown")
async def shutdown_event():
    await client.stop()


@app.get("/")
async def root():
    return {"message": "Telegram video streamer is working!"}


@app.get("/stream/{chat_id}/{message_id}")
async def stream_video(chat_id: str, message_id: int):
    try:
        message = await client.get_messages(chat_id, message_id)
        if not message.video and not message.document:
            return JSONResponse(content={"error": "No video found in this message."}, status_code=404)

        file = await client.download_media(message, file_name="video.mp4")

        def iterfile():
            with open(file, mode="rb") as f:
                yield from f

        return StreamingResponse(iterfile(), media_type="video/mp4")

    except PeerIdInvalid:
        return JSONResponse(content={"error": "PEER_ID_INVALID. Check chat_id and your access."}, status_code=400)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
