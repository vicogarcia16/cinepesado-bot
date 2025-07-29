import httpx
import re
import asyncio
import tmdbsimple as tmdb
from app.core.config import get_settings
from app.data.prompt import SYSTEM_PROMPT
from app.core.exceptions import LLMApiError, YouTubeSearchError

settings = get_settings()

OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY
OPENROUTER_MODEL = settings.OPENROUTER_MODEL
TMDB_API_KEY = settings.TMDB_API_KEY

tmdb.API_KEY = TMDB_API_KEY

async def search_youtube_trailer(movie_title: str, movie_year: str) -> str | None:
    search = tmdb.Search()
    try:
        # Search for the movie
        response = await asyncio.to_thread(search.movie, query=movie_title, year=movie_year)
        
        if not response['results']:
            # If no exact match with year, try without year
            response = await asyncio.to_thread(search.movie, query=movie_title)

        if response['results']:
            movie_id = response['results'][0]['id']
            movie = tmdb.Movies(movie_id)
            
            # Get videos (trailers) for the movie
            videos = await asyncio.to_thread(movie.videos)
            
            if videos and videos.get('results'):
                for video in videos['results']:
                    if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                        return f"https://www.youtube.com/watch?v={video['key']}"
    except Exception as e:
        raise YouTubeSearchError(detail=f"Failed to search TMDb for trailer: {e}")
    return None

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

    # Extraer título y año de la respuesta del LLM
    match = re.search(r'\[TÍTULO:\s*(.*?)\s*,?\s*AÑO:\s*(\d{4})\]', llm_response_content)

    if not match:
        # Si no se encuentra el patrón, devolvemos la respuesta del LLM tal cual
        # y eliminamos cualquier TRAILER_PLACEHOLDER que el LLM haya puesto
        return llm_response_content.replace("[TRAILER_PLACEHOLDER]", "")

    movie_title, movie_year = match.groups()
    
    # Limpiar la etiqueta de título y año de la respuesta
    final_response = re.sub(r'\[TÍTULO:.*?\]', '', llm_response_content).strip()

    # Buscar el tráiler en TMDb
    trailer_link = await search_youtube_trailer(movie_title, movie_year)

    # Reemplazar el placeholder con el enlace real o eliminarlo si no se encuentra
    if trailer_link:
        final_response = final_response.replace("[TRAILER_PLACEHOLDER]", trailer_link)
    else:
        final_response = final_response.replace("[TRAILER_PLACEHOLDER]", "(Tráiler no disponible)")

    return final_response