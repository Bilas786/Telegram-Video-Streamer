import os
from fastapi import FastAPI, HTTPException
from pyrogram import Client, errors

app = FastAPI()

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHAT_ID = int(os.environ.get("CHAT_ID"))  # must be numeric ID like -1002734341593

tg_client = Client(
    "tg_session",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

@app.on_event("startup")
async def startup():
    await tg_client.start()

    # Try to join the channel if not already a member
    try:
        await tg_client.join_chat(CHAT_ID)
    except errors.UserAlreadyParticipant:
        # Already joined, no problem
        pass
    except Exception as e:
        print(f"Join chat warning: {e}")

@app.on_event("shutdown")
async def shutdown():
    await tg_client.stop()

@app.get("/")
async def root():
    return {"message": "Telegram video streamer is working!"}

@app.get("/videos")
async def get_videos():
    try:
        videos = []
        async for msg in tg_client.get_chat_history(CHAT_ID, limit=20):
            if msg.video:
                videos.append({
                    "message_id": msg.message_id,
                    "file_name": msg.video.file_name or "Unknown",
                    "duration": msg.video.duration,
                    "mime_type": msg.video.mime_type
                })
        return {"videos": videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching videos: {e}")
