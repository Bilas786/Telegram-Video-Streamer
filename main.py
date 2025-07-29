from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from pyrogram import Client
import os
import asyncio
from typing import AsyncGenerator

app = FastAPI()

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
OWNER_ID = int(os.environ.get("OWNER_ID"))  # Optional but good to include

client = Client(
    name="streamer",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

@app.on_event("startup")
async def startup_event():
    await client.start()

@app.on_event("shutdown")
async def shutdown_event():
    await client.stop()

@app.get("/")
async def root():
    return {"status": "MTProto Streamer is Running ✅"}

@app.get("/stream/{chat_id}/{message_id}")
async def stream_file(chat_id: str, message_id: int):
    try:
        message = await client.get_messages(chat_id, message_id)
        if not message.video and not message.document:
            raise HTTPException(status_code=400, detail="No streamable media in this message")

        async def file_stream() -> AsyncGenerator[bytes, None]:
            async for chunk in client.stream_media(message):
                yield chunk

        return StreamingResponse(file_stream(), media_type="video/mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
