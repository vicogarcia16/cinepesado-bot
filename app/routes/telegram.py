from fastapi import APIRouter, Request, Depends
from app.bot.telegram import send_typing_action, send_message
from app.bot.handlers import generate_bot_response
from app.db.chat_history import create_chat_history, get_last_chats, build_chat_context
from app.schemas.chat_history import ChatHistoryCreate, ChatHistoryListResponse
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

router = APIRouter(prefix="/telegram", 
                   tags=["telegram"], 
                   responses={404: {"description": "Not found"}})


@router.get("/history/{chat_id}", response_model=ChatHistoryListResponse)
async def get_history(chat_id: int, db: AsyncSession = Depends(get_db)):
    return await get_last_chats(db, chat_id)

@router.post("/webhook/")
async def telegram_webhook(req: Request, db: AsyncSession = Depends(get_db)):
    body = await req.json()
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip().lower()

    if not chat_id or not text:
        return {"ok": True}

    full_text = await build_chat_context(db, chat_id, text)
    async def keep_typing():
        while True:
            await send_typing_action(chat_id)
            await asyncio.sleep(2)

    typing_task = asyncio.create_task(keep_typing())
    try:
        response = await generate_bot_response(full_text)
    finally:
        typing_task.cancel()

    await create_chat_history(db, 
                              ChatHistoryCreate(
                                  chat_id=chat_id,
                                  message=text, 
                                  response=response
                              ))
    await send_message(chat_id, response)
    return {"ok": True}
