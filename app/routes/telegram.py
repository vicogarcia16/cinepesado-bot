from fastapi import APIRouter, Request
from app.bot.telegram import send_typing_action, send_message
from app.bot.handlers import handle_message

router = APIRouter(prefix="/telegram", 
                   tags=["telegram"], 
                   responses={404: {"description": "Not found"}})

@router.post("/webhook/")
async def telegram_webhook(req: Request):
    body = await req.json()
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip().lower()

    if not chat_id or not text:
        return {"ok": True}

    await send_typing_action(chat_id)
    response = await handle_message(text)
    await send_message(chat_id, response)

    return {"ok": True}