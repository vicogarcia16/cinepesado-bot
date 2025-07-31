import asyncio
import tmdbsimple as tmdb
from app.core.config import get_settings
from app.core.exceptions import YouTubeSearchError

settings = get_settings()
TMDB_API_KEY = settings.TMDB_API_KEY
tmdb.API_KEY = TMDB_API_KEY

async def _search_movie_by_year_and_title(search_client, movie_title: str, movie_year: str):
    """Helper to search for a movie by title and year, prioritizing exact year match."""
    response = await asyncio.to_thread(search_client.movie, query=movie_title, year=movie_year)
    
    best_match = None
    if response['results']:
        for movie_result in response['results']:
            release_year = str(movie_result.get('release_date', ''))[:4]
            if release_year == movie_year:
                best_match = movie_result
                break
        if not best_match:
            best_match = response['results'][0]

    if not best_match:
        response = await asyncio.to_thread(search_client.movie, query=movie_title)
        if response['results']:
            best_match = response['results'][0]
            try:
                min_year_diff = abs(int(movie_year) - int(str(best_match.get('release_date', ''))[:4]))
            except (ValueError, TypeError):
                min_year_diff = float('inf')

            for movie_result in response['results']:
                try:
                    current_year_str = str(movie_result.get('release_date', ''))[:4]
                    if not current_year_str:
                        continue
                    current_year = int(current_year_str)
                    year_diff = abs(int(movie_year) - current_year)
                    if year_diff < min_year_diff:
                        min_year_diff = year_diff
                        best_match = movie_result
                except (ValueError, TypeError):
                    continue
                    
    return best_match

async def search_movie_data(movie_title: str, movie_year: str) -> dict:
    """Searches for a movie and returns its trailer link, poster URL, watch providers, cast, and rating."""
    search = tmdb.Search()
    result = {
        "trailer_link": None,
        "poster_url": None,
        "watch_providers": None,
        "cast": None,
        "rating": None
    }
    try:
        best_match = await _search_movie_by_year_and_title(search, movie_title, movie_year)
        if best_match:
            movie_id = best_match['id']
            movie = tmdb.Movies(movie_id)
            details = await asyncio.to_thread(movie.info, append_to_response='videos,watch/providers,credits')

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

            if 'vote_average' in details:
                result['rating'] = round(details['vote_average'], 1)

    except Exception as e:
        raise YouTubeSearchError(detail=f"Failed to search TMDb for movie data: {e}")

    return result
