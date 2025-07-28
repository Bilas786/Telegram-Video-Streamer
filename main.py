from flask import Flask, Response
from pyrogram import Client
import os
import asyncio
import nest_asyncio

# Fix event loop issues
nest_asyncio.apply()

app = Flask(__name__)

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

client = Client("streamer", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.route("/")
def home():
    return "✅ MTProto Video Streamer Running"

@app.route("/join")
def join_channel():
    async def do_join():
        async with client:
            try:
                await client.join_chat("https://t.me/+tjAFFEsryVs3YTU1")
                return "✅ Joined channel successfully!"
            except Exception as e:
                return f"❌ Join failed: {e}"

    return asyncio.run(do_join())

@app.route("/stream/<int:msg_id>")
def stream_video(msg_id):
    async def generate():
        async with client:
            try:
                msg = await client.get_messages("-1002734341593", msg_id)
                async for chunk in client.download_media(msg, in_memory=True):
                    yield chunk
            except Exception as e:
                yield f"❌ Stream Error: {e}".encode()

    return Response(generate(), mimetype="video/mp4")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
