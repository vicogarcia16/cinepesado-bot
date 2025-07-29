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

async def _search_movie_by_year_and_title(search_client, movie_title: str, movie_year: str):
    """Helper to search for a movie by title and year, prioritizing exact year match."""
    response = await asyncio.to_thread(search_client.movie, query=movie_title, year=movie_year)
    
    best_match = None
    if response['results']:
        for movie_result in response['results']:
            if str(movie_result.get('release_date', ''))[:4] == movie_year:
                best_match = movie_result
                break
        if not best_match:
            best_match = response['results'][0]

    if not best_match:
        response = await asyncio.to_thread(search_client.movie, query=movie_title)
        if response['results']:
            best_match = response['results'][0]
            min_year_diff = abs(int(movie_year) - int(str(best_match.get('release_date', ''))[:4] or 0))

            for movie_result in response['results']:
                current_year = int(str(movie_result.get('release_date', ''))[:4] or 0)
                if current_year:
                    year_diff = abs(int(movie_year) - current_year)
                    if year_diff < min_year_diff:
                        min_year_diff = year_diff
                        best_match = movie_result
    return best_match

async def _get_trailer_link_from_movie_id(movie_id: int) -> str | None:
    """Helper to get a YouTube trailer link from a movie ID."""
    movie = tmdb.Movies(movie_id)
    videos = await asyncio.to_thread(movie.videos)
    
    if videos and videos.get('results'):
        for video in videos['results']:
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                return f"https://www.youtube.com/watch?v={video['key']}"
    return None

async def search_youtube_trailer(movie_title: str, movie_year: str) -> str | None:
    search = tmdb.Search()
    try:
        best_match = await _search_movie_by_year_and_title(search, movie_title, movie_year)
        if best_match:
            return await _get_trailer_link_from_movie_id(best_match['id'])
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

    matches = re.findall(r'(\[TÍTULO:\s*(.*?)\s*,?\s*AÑO:\s*(\d{4})\])', llm_response_content)

    final_response = llm_response_content

    for full_tag, movie_title, movie_year in matches:
        trailer_link = await search_youtube_trailer(movie_title, movie_year)
        
        trailer_info = f"Tráiler: {trailer_link}" if trailer_link else "Tráiler: (No encontrado en TMDb)"
        
        final_response = re.sub(re.escape(full_tag), f"{full_tag}\n{trailer_info}", final_response, 1)

    return final_response