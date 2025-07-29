import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pyrogram import Client

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

app = FastAPI()

client = Client(
    name="stream_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)


@app.on_event("startup")
async def startup_event():
    print("✅ Starting Pyrogram client...")
    await client.start()
    print("✅ Pyrogram client started!")


@app.on_event("shutdown")
async def shutdown_event():
    await client.stop()
    print("❌ Pyrogram client stopped!")


@app.get("/videos")
async def list_videos():
    chat_id = os.getenv("CHAT_ID", "moviesnesthub")  # Your channel username
    videos = []
    async for msg in client.get_chat_history(chat_id, limit=20):
        if msg.video or msg.document:
            file_name = None
            if msg.video:
                file_name = msg.video.file_name
            elif msg.document and msg.document.mime_type.startswith("video/"):
                file_name = msg.document.file_name

            videos.append({
                "chat_id": msg.chat.id,
                "message_id": msg.id,
                "file_name": file_name
            })
    return videos


@app.get("/stream/{chat_id}/{message_id}")
async def stream_video(chat_id: int, message_id: int):
    try:
        msg = await client.get_messages(chat_id, message_id)
        media = msg.video or msg.document
        if not media:
            raise HTTPException(status_code=404, detail="No video found in this message")

        async def iterfile():
            async for chunk in client.stream_media(msg):
                yield chunk

        return StreamingResponse(iterfile(), media_type="video/mp4")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting main.py ...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

