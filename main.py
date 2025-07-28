from flask import Flask, request, Response
from pyrogram import Client
import os

app = Flask(__name__)

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
client = Client("streamer", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

CHANNEL_LINK = "https://t.me/+tjAFFEsryVs3YTU1"

@app.before_serving
async def startup():
    await client.start()
    try:
        await client.get_chat(CHANNEL_LINK)
        print("✅ Cached channel access")
    except Exception as e:
        print("❌ Failed to cache channel:", e)

@app.route("/")
def home():
    return "MTProto Telegram Video Streamer Running!"

@app.route("/stream/<int:msg_id>")
def stream_video(msg_id):
    async def generate():
        async with client:
            msg = await client.get_messages("-1002734341593", msg_id)
            async for chunk in client.download_media(msg, in_memory=True):
                yield chunk
    return Response(generate(), mimetype="video/mp4")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
