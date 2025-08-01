import httpx
import re
from app.core.config import get_settings
from app.data.prompt import SYSTEM_PROMPT
from app.core.exceptions import LLMApiError
from app.services.tmdb_service import search_media_data

settings = get_settings()

OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY
OPENROUTER_MODEL = settings.OPENROUTER_MODEL

async def get_llm_response(user_message: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 1500
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            res = await client.post(url, headers=headers, json=data)
            res.raise_for_status()
            llm_response_content = res.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPStatusError, KeyError, IndexError) as e:
            error_detail = f"Failed to get a valid response from the LLM API. Error: {e}"
            if hasattr(res, 'text'):
                error_detail += f" Raw response: {res.text}"
            raise LLMApiError(detail=error_detail)

    matches = re.findall(r'(\[TIPO:\s*(PELICULA|SERIE)\s*,\s*TÍTULO:\s*(.*?)\s*,\s*AÑO:\s*(\d{4})\])', llm_response_content)
    
    final_response = llm_response_content
    
    for full_tag, media_type, title, year in matches:
        movie_data = await search_media_data(media_type, title, year)
        
        trailer_link = movie_data.get("trailer_link")
        poster_url = movie_data.get("poster_url")
        watch_providers = movie_data.get("watch_providers")
        cast = movie_data.get("cast")

        trailer_info = f"Tráiler: {trailer_link}" if trailer_link else ""
        poster_info = f"Poster: {poster_url}" if poster_url else ""

        watch_info = ""
        if watch_providers and any(watch_providers.values()):
            watch_info += "\n¿Dónde ver?"
            if watch_providers.get('flatrate'):
                watch_info += f"\nStreaming: {', '.join(watch_providers['flatrate'])}"
            if watch_providers.get('rent'):
                watch_info += f"\nAlquiler: {', '.join(watch_providers['rent'])}"
            if watch_providers.get('buy'):
                watch_info += f"\nCompra: {', '.join(watch_providers['buy'])}"

        cast_info = f"\nReparto: {', '.join(cast)}" if cast else ""

        replacement_text = f"{trailer_info}\n{poster_info}{watch_info}{cast_info}"
        final_response = re.sub(re.escape(full_tag), replacement_text, final_response, 1)

    return final_response.strip()