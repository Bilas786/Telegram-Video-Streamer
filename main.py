from flask import Flask, jsonify
from pyrogram import Client
import asyncio
import os

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

app = Flask(__name__)
client = Client("streamer", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# Fix: Run the join_chat function in the event loop
@app.route("/join")
def join_channel():
    async def do_join():
        try:
            await client.start()
            await client.join_chat("tjAFFEsryVs3YTU1")  # Only the part after https://t.me/+
            await client.stop()
            return {"status": "joined successfully"}
        except Exception as e:
            return {"error": str(e)}

    result = asyncio.run(do_join())
    return jsonify(result)

@app.route("/")
def home():
    return "Telegram Video Streamer is Running!"
