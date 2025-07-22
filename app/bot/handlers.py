from app.services.llm_agent import get_llm_response
from app.core.utils import is_saludo, parse_message
from app.data.prompt import SALUDO_INICIAL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_bot_response(text: str) -> str:
    logger.info(f"Texto recibido: {text}")

    if is_saludo(text):
        logger.info("Detectado como saludo")
        return SALUDO_INICIAL

    raw_response = await get_llm_response(text)
    logger.info(f"Respuesta cruda del modelo: {raw_response}")

    parsed = parse_message(raw_response)
    logger.info(f"Respuesta parseada: {parsed}")

    return parsed