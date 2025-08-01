from app.services.llm_agent import get_llm_response
from app.core.utils import parse_message

async def generate_bot_response(text: str) -> str:
    raw_response = await get_llm_response(text)
    return parse_message(raw_response)