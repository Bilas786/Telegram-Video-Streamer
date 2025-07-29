import os
import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from pyrogram import Client, errors

app = FastAPI()

# ──── Configure via ENV VARS ─────────────────────────────
API_ID         = int(os.getenv("API_ID"))
API_HASH       = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
INVITE_LINK    = os.getenv("INVITE_LINK")   # e.g. https://t.me/+tjAFFEsryVs3YTU1
CHAT_ID        = int(os.getenv("CHAT_ID"))  # e.g. -1002734341593

# ──── Initialize Pyrogram ────────────────────────────────
tg = Client(
    "streamer",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

@app.on_event("startup")
async def startup():
    await tg.start()
    # join (or skip if already a member)
    try:
        await tg.join_chat(INVITE_LINK)
    except errors.UserAlreadyParticipant:
        pass
    except Exception as e:
        print("⚠️ Join warning:", e)

@app.on_event("shutdown")
async def shutdown():
    await tg.stop()

# ──── Home & Player UI ───────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h1>Telegram Video Streamer</h1>
    <p>Use <code>/stream/&lt;message_id&gt;</code> to play.</p>
    <form action="/stream" method="get">
      Message ID: <input name="id" required>
      <button>Play</button>
    </form>
    """

@app.get("/stream", response_class=HTMLResponse)
async def play_form(id: int):
    # Simple HTML5 player
    return f'''
    <video controls width="100%" height="auto">
      <source src="/stream/{id}" type="video/mp4">
      Your browser does not support the video tag.
    </video>
    '''

# ──── Streaming Endpoint ─────────────────────────────────
@app.get("/stream/{msg_id}")
async def stream_video(request: Request, msg_id: int):
    # temp path
    tmp = f"/tmp/{msg_id}.mp4"
    try:
        msg = await tg.get_messages(CHAT_ID, msg_id)
        if not (msg.video or msg.document):
            raise HTTPException(404, "No video found in this message")

        # download if not exists
        if not os.path.exists(tmp):
            await tg.download_media(msg, file_name=tmp)

        return FileResponse(tmp, media_type="video/mp4")
    except errors.PeerIdInvalid:
        raise HTTPException(400, "Peer ID invalid – check your CHAT_ID or invite link")
    except Exception as e:
        raise HTTPException(500, str(e))
