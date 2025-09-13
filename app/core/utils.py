from app.data.prompt import SALUDOS
from app.core.exceptions import DataRequiredException
import re

def is_saludo(text: str) -> bool:
    cleaned_text = text.lower().strip()
    if cleaned_text in SALUDOS:
        return True

    for saludo in SALUDOS:
        pattern = re.compile(rf"(^|\W){re.escape(saludo)}($|\W)")
        if pattern.search(cleaned_text):
            return True
            
    return False


def clean_text(html_text: str) -> str:
    if not html_text:
        return ""
    return re.sub(r'<.*?>', '', html_text)

def validate_message(message: dict) -> tuple[int, str]:
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip().lower()

    if not chat_id or not text:
        raise DataRequiredException("chat_id and text are required")
    
    return chat_id, text