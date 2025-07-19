from app.data.prompt import SALUDOS

def is_saludo(text: str) -> bool:
    return any(s in text for s in SALUDOS)

def parse_message(text: str) -> str:
    return (
        text
        .replace("**", "<b>").replace("*", "<i>")
        .replace("```", "<pre>").replace("`", "<code>")
        .replace("\n", "\n")
    )
