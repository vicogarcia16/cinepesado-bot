from app.services.llm_agent import get_llm_response
from app.core.utils import is_saludo, parse_message
from app.data.prompt import SALUDO_INICIAL

async def generate_bot_response(text: str) -> str:
    last_line = text.strip().split("\n")[-1]
    if last_line.lower().startswith("user: "):
        user_input = last_line[6:].strip()
    else:
        user_input = last_line

    if is_saludo(user_input):
        return SALUDO_INICIAL

    raw_response = await get_llm_response(text)
    return parse_message(raw_response)