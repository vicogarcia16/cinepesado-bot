from fastapi import APIRouter, Request, Depends
from app.core.exceptions import JsonInvalidException
from app.bot.telegram import send_typing_action, send_message
from app.bot.handlers import generate_bot_response
from app.core.utils import validate_message
from app.db.chat_history import create_chat_history, get_last_chats, build_chat_context
from app.schemas.chat_history import ChatHistoryCreate, ChatHistoryListResponse
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import httpx

router = APIRouter(prefix="/telegram", 
                   tags=["telegram"], 
                   responses={404: {"description": "Not found"}})

async def answer_callback_query(callback_query_id: str, text: str = None, show_alert: bool = False) -> None:
    from app.core.config import get_settings
    settings = get_settings()
    async with httpx.AsyncClient(timeout=10) as client:
        payload = {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": show_alert
        }
        await client.post(f"{settings.api_telegram}/answerCallbackQuery", json=payload)

@router.get("/history/{chat_id}", response_model=ChatHistoryListResponse)
async def get_history(chat_id: int, db: AsyncSession = Depends(get_db)):
    return await get_last_chats(db, chat_id)

@router.post("/webhook/")
async def telegram_webhook(req: Request, db: AsyncSession = Depends(get_db)):
    try:
        body = await req.json()
    except Exception:
        raise JsonInvalidException()

    if "callback_query" in body:
        callback_query = body["callback_query"]
        chat_id = callback_query["message"]["chat"]["id"]
        callback_data = callback_query["data"]
        callback_query_id = callback_query["id"]

        if callback_data == "recommend_another":
            await answer_callback_query(callback_query_id)
            full_text = await build_chat_context(db, chat_id, "Recomiéndame otra película")
            
            typing_task = asyncio.create_task(send_typing_action(chat_id))
            try:
                response_text, reply_markup = await generate_bot_response(full_text, chat_id)
            finally:
                typing_task.cancel()
            
            await create_chat_history(db, 
                                      ChatHistoryCreate(
                                          chat_id=chat_id,
                                          message="Recomiéndame otra película", 
                                          response=response_text
                                      ))
            await send_message(chat_id, response_text, reply_markup=reply_markup)

        elif callback_data == "view_history":
            await answer_callback_query(callback_query_id, text="Cargando historial...")
            history = await get_last_chats(db, chat_id)
            history_text = "\n".join([f"User: {h.message}\nBot: {h.response}" for h in history.history])
            if not history_text:
                history_text = "Tu historial está vacío."
            await send_message(chat_id, f"Tu historial de chat:\n{history_text}")
        else:
            await answer_callback_query(callback_query_id, text="Acción no reconocida.")

    elif "message" in body:
        message = body.get("message", {})
        chat_id, text = validate_message(message)

        full_text = await build_chat_context(db, chat_id, text)
        async def keep_typing():
            while True:
                await send_typing_action(chat_id)
                await asyncio.sleep(2)

        typing_task = asyncio.create_task(keep_typing())
        try:
            response_text, reply_markup = await generate_bot_response(full_text, chat_id)
        finally:
            typing_task.cancel()

        await create_chat_history(db, 
                                  ChatHistoryCreate(
                                      chat_id=chat_id,
                                      message=text, 
                                      response=response_text
                                  ))
        await send_message(chat_id, response_text, reply_markup=reply_markup)
    return {"ok": True}
