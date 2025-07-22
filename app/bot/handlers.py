from app.services.llm_agent import get_llm_response
from app.core.utils import is_saludo, parse_message
from app.data.prompt import SALUDO_INICIAL

async def generate_bot_response(text: str) -> str:
    print("texto recibido", text)
    if is_saludo(text):
        return SALUDO_INICIAL

    raw_response = await get_llm_response(text)
    return parse_message(raw_response)
