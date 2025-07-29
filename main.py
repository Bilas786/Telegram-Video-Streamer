from fastapi import FastAPI
from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant

import os, asyncio

app = FastAPI()

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]
INVITE_LINK = os.environ["INVITE_LINK"]

pyro_app = Client("streamer", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.on_event("startup")
async def startup_event():
    await pyro_app.start()

@app.get("/")
async def home():
    return {"message": "Telegram video streamer is working!"}

@app.get("/videos")
async def get_videos():
    try:
        # First, try to join or confirm membership
        try:
            await pyro_app.join_chat(INVITE_LINK)
        except UserAlreadyParticipant:
            pass  # already joined

        # Resolve chat from invite link
        chat = await pyro_app.get_chat(INVITE_LINK)

        # Fetch last 20 video messages
        videos = []
        async for msg in pyro_app.get_chat_history(chat.id, limit=20):
            if msg.video:
                videos.append({
                    "message_id": msg.id,
                    "file_name": msg.video.file_name,
                    "duration": msg.video.duration,
                    "chat_id": chat.id
                })

        return {"videos": videos}

    except Exception as e:
        return {"detail": f"Error fetching videos: {e}"}
