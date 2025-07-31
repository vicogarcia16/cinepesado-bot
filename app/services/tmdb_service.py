import asyncio
import tmdbsimple as tmdb
from app.core.config import get_settings
from app.core.exceptions import YouTubeSearchError

settings = get_settings()
TMDB_API_KEY = settings.TMDB_API_KEY
tmdb.API_KEY = TMDB_API_KEY

async def _search_media_by_year_and_title(search_client, media_type: str, title: str, year: str):
    """Helper to search for a movie or TV show by title and year."""
    search_method = search_client.movie if media_type == 'PELICULA' else search_client.tv
    date_key = 'release_date' if media_type == 'PELICULA' else 'first_air_date'
    
    response = await asyncio.to_thread(search_method, query=title, year=year)
    
    best_match = None
    if response['results']:
        for result in response['results']:
            release_year = str(result.get(date_key, ''))[:4]
            if release_year == year:
                best_match = result
                break
        if not best_match:
            best_match = response['results'][0]

    if not best_match:
        response = await asyncio.to_thread(search_method, query=title)
        if response['results']:
            best_match = response['results'][0]
            try:
                min_year_diff = abs(int(year) - int(str(best_match.get(date_key, ''))[:4]))
            except (ValueError, TypeError):
                min_year_diff = float('inf')

            for result in response['results']:
                try:
                    current_year_str = str(result.get(date_key, ''))[:4]
                    if not current_year_str:
                        continue
                    current_year = int(current_year_str)
                    year_diff = abs(int(year) - current_year)
                    if year_diff < min_year_diff:
                        min_year_diff = year_diff
                        best_match = result
                except (ValueError, TypeError):
                    continue
                    
    return best_match

async def search_media_data(media_type: str, title: str, year: str) -> dict:
    """Searches for a movie or TV show and returns its data."""
    search = tmdb.Search()
    result = {
        "trailer_link": None,
        "poster_url": None,
        "watch_providers": None,
        "cast": None
    }
    try:
        best_match = await _search_media_by_year_and_title(search, media_type, title, year)
        if best_match:
            media_id = best_match['id']
            media_obj = tmdb.Movies(media_id) if media_type == 'PELICULA' else tmdb.TV(media_id)
            details = await asyncio.to_thread(media_obj.info, append_to_response='videos,watch/providers,credits')

            if details and details.get('poster_path'):
                result["poster_url"] = f"https://image.tmdb.org/t/p/w500{details['poster_path']}"

            videos = details.get('videos', {}).get('results', [])
            for video in videos:
                if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                    result["trailer_link"] = f"https://www.youtube.com/watch?v={video['key']}"
                    break
            
            if 'watch/providers' in details and 'results' in details['watch/providers'] and 'PE' in details['watch/providers']['results']:
                providers = details['watch/providers']['results']['PE']
                result['watch_providers'] = {
                    'buy': [p['provider_name'] for p in providers.get('buy', [])],
                    'rent': [p['provider_name'] for p in providers.get('rent', [])],
                    'flatrate': [p['provider_name'] for p in providers.get('flatrate', [])]
                }

            if 'credits' in details and 'cast' in details['credits']:
                result['cast'] = [actor['name'] for actor in details['credits']['cast'][:5]]

    except Exception as e:
        raise YouTubeSearchError(detail=f"Failed to search TMDb for movie data: {e}")

    return result
