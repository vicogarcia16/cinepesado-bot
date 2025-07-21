from fastapi import APIRouter, Request, Depends
from app.bot.telegram import send_typing_action, send_message
from app.bot.handlers import handle_message
from app.db.chat_history import create_chat_history
from app.schemas.chat_history import ChatHistoryCreate
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

router = APIRouter(prefix="/telegram", 
                   tags=["telegram"], 
                   responses={404: {"description": "Not found"}})

@router.post("/webhook/")
async def telegram_webhook(req: Request, db: AsyncSession = Depends(get_db)):
    body = await req.json()
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "").strip().lower()

    if not chat_id or not text:
        return {"ok": True}
    
    async def keep_typing():
        while True:
            await send_typing_action(chat_id)
            await asyncio.sleep(2)

    typing_task = asyncio.create_task(keep_typing())
    try:
        response = await handle_message(text)
    finally:
        typing_task.cancel()
        
    history_data = ChatHistoryCreate(
        chat_id=chat_id,
        user_id=user_id,
        message=text,
        response=response
    )

    await create_chat_history(db, history_data)
    await send_message(chat_id, response)
    return {"ok": True}