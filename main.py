import os
from fastapi import FastAPI, HTTPException, Request
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
    chat_id = os.getenv("CHAT_ID", "moviesnesthub")  # Username or ID
    videos = []
    async for msg in client.get_chat_history(chat_id, limit=20):
        if msg.video or (msg.document and msg.document.mime_type.startswith("video/")):
            file_name = msg.video.file_name if msg.video else msg.document.file_name
            videos.append({
                "chat_id": str(msg.chat.id),  # String to avoid Peer ID invalid
                "message_id": msg.id,
                "file_name": file_name
            })
    return videos

@app.get("/stream/{chat_id}/{message_id}")
async def stream_video(chat_id: str, message_id: int, request: Request):
    try:
        # ✅ Use string chat_id for Pyrogram to avoid Peer ID errors
        msg = await client.get_messages(chat_id, message_id)
        media = msg.video or msg.document
        if not media:
            raise HTTPException(status_code=404, detail="No video found in this message")

        file_size = media.file_size

        # Range request for skipping
        range_header = request.headers.get("range")
        start = 0
        if range_header:
            start = int(range_header.replace("bytes=", "").split("-")[0])

        async def file_iterator():
            async for chunk in client.stream_media(msg, offset=start):
                yield chunk

        headers = {
            "Content-Type": "video/mp4",
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {start}-{file_size-1}/{file_size}"
        }
        status_code = 206 if range_header else 200
        return StreamingResponse(file_iterator(), headers=headers, status_code=status_code)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting main.py ...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
