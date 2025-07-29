import httpx
import re
import asyncio
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.core.config import get_settings
from app.data.prompt import SYSTEM_PROMPT
from app.core.exceptions import LLMApiError, YouTubeSearchError

settings = get_settings()

OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY
OPENROUTER_MODEL = settings.OPENROUTER_MODEL
YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY

# Inicializar el cliente de la API de YouTube una vez
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

async def search_youtube_trailer(movie_title: str, movie_year: str) -> str | None:
    query = f'{movie_title} {movie_year} trailer español latino'
    try:
        response = await asyncio.to_thread(youtube.search().list, 
            q=query,
            type='video',
            part='id,snippet',
            maxResults=1
        )
        
        if response and response.get('items'):
            video_id = response['items'][0]['id']['videoId']
            return f"https://www.youtube.com/watch?v={video_id}"
    except HttpError as e:
        raise YouTubeSearchError(detail=f"YouTube API error: {e}")
    except Exception as e:
        raise YouTubeSearchError(detail=f"Failed to search YouTube for: {query}. Error: {e}")
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
            raise LLMApiError(detail="Failed to get a valid response from the LLM API.")

    match = re.search(r'\[TÍTULO:\s*(.*?)\s*,?\s*AÑO:\s*(\d{4})\]', llm_response_content)

    if not match:
        return llm_response_content

    movie_title, movie_year = match.groups()
    
    final_response = re.sub(r'\[TÍTULO:.*?\]', '', llm_response_content).strip()

    trailer_link = await search_youtube_trailer(movie_title, movie_year)

    if trailer_link:
        final_response = final_response.replace("[TRAILER_PLACEHOLDER]", trailer_link)
    else:
        final_response = final_response.replace("[TRAILER_PLACEHOLDER]", "(Tráiler no disponible)")

    return final_response
