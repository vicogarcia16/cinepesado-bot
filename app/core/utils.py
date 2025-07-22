from app.data.prompt import SALUDOS
import re

def is_saludo(text: str) -> bool:
    return any(s in text for s in SALUDOS)

def parse_message(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"```(.*?)```", r"<pre>\1</pre>", text, flags=re.DOTALL)
    text = re.sub(r"`(.*?)`", r"<code>\1</code>", text)

    return text

def clean_text(html_text: str) -> str:
    if not html_text:
        return ""
    clean = re.sub(r'<.*?>', '', html_text)
    return clean
