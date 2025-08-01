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

def parse_message(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"^#{2,6}\s*(.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)
    text = re.sub(r"```(.*?)```", r"<pre>\1</pre>", text, flags=re.DOTALL)
    text = re.sub(r"`([^`\n]+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.*?)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"^- (.+)$", r"• \1", text, flags=re.MULTILINE)
    text = re.sub(r"</?(ul|li|h2|h3|h4|h5|h6)>", "", text)
    text = re.sub(r"Tráiler: (https?://[^\s]+)", r'Tráiler: <a href="\1">\1</a>', text)
    text = re.sub(r"Poster: (https?://[^\s]+)", r'Poster: <a href="\1">\1</a>', text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r'<a href="\2">\1</a>', text)
    return text.strip()


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
