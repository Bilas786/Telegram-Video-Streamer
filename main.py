from flask import Flask, jsonify
from pyrogram import Client
import asyncio
import os
import nest_asyncio

nest_asyncio.apply()

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

app = Flask(__name__)
client = Client("streamer", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@app.route("/")
def home():
    return "✅ Telegram Video Streamer is running!"

@app.route("/join")
def join_channel():
    async def do_join():
        try:
            await client.start()
            await client.join_chat("https://t.me/+tjAFFEsryVs3YTU1")  # ✅ Correct format
            await client.stop()
            return {"status": "joined"}
        except Exception as e:
            return {"error": str(e)}

    result = asyncio.run(do_join())
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
