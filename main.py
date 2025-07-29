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
    chat_id = os.getenv("CHAT_ID", "moviesnesthub")  # Your channel username
    videos = []
    async for msg in client.get_chat_history(chat_id, limit=20):
        if msg.video or (msg.document and msg.document.mime_type and msg.document.mime_type.startswith("video/")):
            file_name = msg.video.file_name if msg.video else msg.document.file_name
            videos.append({
                "chat_id": msg.chat.username or msg.chat.id,
                "message_id": msg.id,
                "file_name": file_name
            })
    return videos


@app.get("/stream/{chat_id}/{message_id}")
async def stream_video(chat_id: str, message_id: int, request: Request):
    try:
        # Force Pyrogram to resolve peer first
        chat = await client.get_chat(chat_id)
        msg = await client.get_messages(chat.id, message_id)
        media = msg.video or msg.document
        if not media:
            raise HTTPException(status_code=404, detail="No video found in this message")

        file_size = media.file_size

        # Handle Range headers for seeking/skipping
        range_header = request.headers.get('range')
        start = 0
        end = file_size - 1
        status_code = 200
        headers = {
            "Content-Type": "video/mp4",
            "Accept-Ranges": "bytes"
        }

        if range_header:
            bytes_range = range_header.replace("bytes=", "").split("-")
            start = int(bytes_range[0])
            if bytes_range[1]:
                end = int(bytes_range[1])
            status_code = 206
            headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
            headers["Content-Length"] = str(end - start + 1)

        async def video_stream():
            async for chunk in client.stream_media(msg, offset=start, limit=end - start + 1):
                yield chunk

        return StreamingResponse(video_stream(), status_code=status_code, headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting main.py ...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
