import themoviedb as tmdb_api
from app.core.config import get_settings
import httpx

settings = get_settings()
tmdb_api.API_KEY = settings.TMDB_API_KEY

async def search_movie(title: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.themoviedb.org/3/search/movie",
            params={
                "api_key": settings.TMDB_API_KEY,
                "query": title,
                "language": "es-ES"
            }
        )
        response.raise_for_status()
        data = response.json()
        return data.get("results")

async def get_movie_details(movie_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={
                "api_key": settings.TMDB_API_KEY,
                "language": "es-ES",
                "append_to_response": "videos,watch/providers"
            }
        )
        response.raise_for_status()
        return response.json()
