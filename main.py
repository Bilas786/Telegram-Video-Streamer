import os
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from pyrogram import Client

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
CHAT_USERNAME = os.getenv("CHAT_USERNAME", "moviesnesthub")  # ✅ username only

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
    videos = []
    async for msg in client.get_chat_history(CHAT_USERNAME, limit=20):
        if msg.video or (msg.document and msg.document.mime_type.startswith("video/")):
            file_name = msg.video.file_name if msg.video else msg.document.file_name
            file_size = msg.video.file_size if msg.video else msg.document.file_size
            videos.append({
                "message_id": msg.id,
                "file_name": file_name,
                "file_size": file_size
            })
    return videos

@app.get("/stream/{message_id}")
async def stream_video(message_id: int, request: Request):
    try:
        msg = await client.get_messages(CHAT_USERNAME, message_id)
        media = msg.video or msg.document
        if not media:
            raise HTTPException(status_code=404, detail="No video found in this message")

        file_size = media.file_size
        range_header = request.headers.get("range")

        if range_header:
            byte1, byte2 = 0, None
            match = range_header.replace("bytes=", "").split("-")
            if match[0]:
                byte1 = int(match[0])
            if len(match) > 1 and match[1]:
                byte2 = int(match[1])

            length = file_size - byte1 if byte2 is None else byte2 - byte1 + 1

            async def iterfile(start, length):
                async for chunk in client.stream_media(msg, offset=start, limit=length):
                    yield chunk

            headers = {
                "Content-Range": f"bytes {byte1}-{byte1+length-1}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(length),
                "Content-Type": "video/mp4",
            }
            return StreamingResponse(iterfile(byte1, length), status_code=206, headers=headers)

        # No range requested → full file
        async def iterfile_full():
            async for chunk in client.stream_media(msg):
                yield chunk

        return StreamingResponse(iterfile_full(), media_type="video/mp4")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting main.py ...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
