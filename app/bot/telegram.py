import httpx
from app.core.config import get_settings

settings = get_settings()

async def send_typing_action(chat_id: int) -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(f"{settings.api_telegram}/sendChatAction", json={
            "chat_id": chat_id,
            "action": "typing"
        })

async def send_message(chat_id: int, text: str, parse_mode: str = "HTML", reply_markup: dict = None) -> None:
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(f"{settings.api_telegram}/sendMessage", json=payload)
