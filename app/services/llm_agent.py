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

async def search_movie_data(movie_title: str, movie_year: str) -> dict:
    """Searches for a movie and returns its trailer link and poster URL."""
    search = tmdb.Search()
    result = {
        "trailer_link": None,
        "poster_url": None
    }
    try:
        best_match = await _search_movie_by_year_and_title(search, movie_title, movie_year)
        if best_match:
            movie_id = best_match['id']
            movie = tmdb.Movies(movie_id)
            details = await asyncio.to_thread(movie.info, append_to_response='videos')

            if details and details.get('poster_path'):
                result["poster_url"] = f"https://image.tmdb.org/t/p/w500{details['poster_path']}"

            videos = details.get('videos', {}).get('results', [])
            for video in videos:
                if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                    result["trailer_link"] = f"https://www.youtube.com/watch?v={video['key']}"
                    break
    except Exception as e:
        raise YouTubeSearchError(detail=f"Failed to search TMDb for movie data: {e}")

    return result

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
        movie_data = await search_movie_data(movie_title, movie_year)
        trailer_link = movie_data.get("trailer_link")
        poster_url = movie_data.get("poster_url")
        
        trailer_info = f"Tráiler: {trailer_link}" if trailer_link else "Tráiler: (No encontrado en TMDb)"
        poster_info = f"Poster: {poster_url}" if poster_url else "Poster: (No encontrado)"
        
        final_response = re.sub(re.escape(full_tag), f"{full_tag}\n{trailer_info}\n{poster_info}", final_response, 1)

    return final_response