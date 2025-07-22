from app.data.prompt import SALUDOS
import re
import logging

def is_saludo(text: str) -> bool:
    text = text.lower()
    logging.info("Text: %s", text)
    for saludo in SALUDOS:
        if re.search(rf"\b{re.escape(saludo)}\b", text):
            return True
    return False

def parse_message(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"```(.*?)```", r"<pre>\1</pre>", text, flags=re.DOTALL)

    text = re.sub(r"`([^`\n]+?)`", r"<code>\1</code>", text)

    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)

    text = re.sub(r"(?<!\*)\*(?!\*)(.*?)\*(?!\*)", r"<i>\1</i>", text)

    text = re.sub(r"^# (.+)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)

    text = re.sub(r"^- (.+)$", r"<li>\1</li>", text, flags=re.MULTILINE)
    if "<li>" in text:
        text = "<ul>" + text + "</ul>"
    return text.strip()


def clean_text(html_text: str) -> str:
    if not html_text:
        return ""
    clean = re.sub(r'<.*?>', '', html_text)
    return clean
