from fastapi import FastAPI, HTTPException from fastapi.responses import StreamingResponse from pyrogram import Client from pyrogram.errors import FloodWait, PeerIdInvalid, UsernameNotOccupied, UserAlreadyParticipant import asyncio import os

app = FastAPI()

API_ID = int(os.getenv("API_ID")) API_HASH = os.getenv("API_HASH") SESSION_STRING = os.getenv("SESSION_STRING") OWNER_ID = int(os.getenv("OWNER_ID"))  # numeric Telegram ID

app.client = Client( "streamer", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING )

@app.on_event("startup") async def startup(): await app.client.start()

@app.on_event("shutdown") async def shutdown(): await app.client.stop()

@app.get("/") async def root(): return {"message": "Telegram Video Streamer Running Successfully!"}

@app.get("/stream/{message_id}") async def stream_video(message_id: int): chat_id = "me"  # default to saved messages or use private channel ID if needed

try:
    msg = await app.client.get_messages(chat_id, message_id)
    if not msg.video and not msg.document:
        raise HTTPException(status_code=404, detail="No video/document found in this message")

    file = await app.client.download_media(msg, in_memory=True)
    return StreamingResponse(file, media_type="video/mp4")

except PeerIdInvalid:
    raise HTTPException(status_code=400, detail="Peer ID invalid: Make sure you're accessing your own channel or saved messages")
except UsernameNotOccupied:
    raise HTTPException(status_code=400, detail="The username is invalid or not occupied")
except UserAlreadyParticipant:
    pass  # skip join attempt if already participant
except ModuleNotFoundError as e:
    raise HTTPException(status_code=500, detail=f"Missing module: {str(e)}")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

