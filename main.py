from flask import Flask, request, Response
from pyrogram import Client
import os
import asyncio

app = Flask(__name__)

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHANNEL_ID = "-1002734341593"  # Replace with your private channel ID

client = Client("streamer", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.route("/")
def home():
    return "✅ MTProto Telegram Video Streamer is running!"

@app.route("/stream/<int:message_id>")
def stream_video(message_id):
    async def generate():
        async with client:
            try:
                msg = await client.get_messages(CHANNEL_ID, message_id)
                async for chunk in client.stream_media(msg, chunk_size=1024 * 512):  # 512KB chunks
                    yield chunk
            except Exception as e:
                yield f"Error: {str(e)}"

    return Response(generate(), mimetype="video/mp4")


# ✅ TEMPORARY: Fix “Peer ID Invalid” by joining the channel from Render session
@app.route("/join")
def join_channel():
    async def do_join():
        async with client:
            try:
                await client.join_chat("https://t.me/+tjAFFEsryVs3YTU1")  # Your channel invite link
                return "✅ Joined channel successfully!"
            except Exception as e:
                return f"❌ Failed to join channel: {str(e)}"
    return asyncio.run(do_join())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
