import asyncio
import tmdbsimple as tmdb
import logging
from app.core.config import get_settings
from app.core.exceptions import YouTubeSearchError

settings = get_settings()
TMDB_API_KEY = settings.TMDB_API_KEY
tmdb.API_KEY = TMDB_API_KEY

logger = logging.getLogger(__name__)

async def _search_media(search_client, media_type: str, title: str, year: str, actor: str = None, genre: str = None, director: str = None):
    search_method = search_client.movie if media_type == 'PELICULA' else search_client.tv
    date_key = 'release_date' if media_type == 'PELICULA' else 'first_air_date'
    
    best_match = None

    search_params = {"query": title}
    if year:
        search_params["year"] = year

    response = await asyncio.to_thread(search_method, **search_params)

    all_results = []
    if response and response.get('results'):
        all_results.extend(response['results'])

    if year:
        all_results = [r for r in all_results if str(r.get(date_key, ''))[:4] == year]

    best_score = -1

    for result in all_results:
        current_year_str = str(result.get(date_key, ''))[:4]
        current_year = int(current_year_str) if current_year_str.isdigit() else None
        has_poster = result.get('poster_path') is not None

        score = 0

        if has_poster:
            score += 100

        if year and current_year is not None:
            if str(current_year) == year:
                score += 50
            else:
                year_diff = abs(int(year) - current_year)
                score += max(0, 20 - year_diff)
        
        if actor:
            media_id = result['id']
            media_obj = tmdb.Movies(media_id) if media_type == 'PELICULA' else tmdb.TV(media_id)
            credits = await asyncio.to_thread(media_obj.credits)
            if 'cast' in credits:
                for cast_member in credits['cast']:
                    if actor.lower() in cast_member['name'].lower():
                        score += 75
                        break

        if director:
            media_id = result['id']
            media_obj = tmdb.Movies(media_id) if media_type == 'PELICULA' else tmdb.TV(media_id)
            credits = await asyncio.to_thread(media_obj.credits)
            if 'crew' in credits:
                for crew_member in credits['crew']:
                    if crew_member['job'] == 'Director' and director.lower() in crew_member['name'].lower():
                        score += 75
                        break

        if genre:
            if genre.lower() in [g['name'].lower() for g in result.get('genres', [])]:
                score += 50

        if score > best_score:
            best_score = score
            best_match = result
        elif score == best_score and best_match:
            if result.get('popularity', 0) > best_match.get('popularity', 0):
                best_match = result

    return best_match

async def search_media_data(media_type: str, title: str, year: str, actor: str = None, genre: str = None, director: str = None) -> dict:
    search = tmdb.Search()
    result = {
        "trailer_link": None,
        "poster_url": None,
        "watch_providers": None,
        "cast": None
    }
    try:
        best_match = await _search_media(search, media_type, title, year, actor, genre, director)
        if best_match:
            media_id = best_match['id']
            media_obj = tmdb.Movies(media_id) if media_type == 'PELICULA' else tmdb.TV(media_id)

            details_task = asyncio.to_thread(media_obj.info)
            videos_task = asyncio.to_thread(media_obj.videos)
            providers_task = asyncio.to_thread(media_obj.watch_providers)
            credits_task = asyncio.to_thread(media_obj.credits)

            details, videos_res, providers_res, credits_res = await asyncio.gather(
                details_task, videos_task, providers_task, credits_task, return_exceptions=True
            )

            if isinstance(details, Exception):
                logger.error(f"Error fetching details for {title} ({media_type}): {details}")
            elif details and details.get('poster_path'):
                result["poster_url"] = f"https://image.tmdb.org/t/p/w500{details['poster_path']}"

            if isinstance(videos_res, Exception):
                logger.error(f"Error fetching videos for {title} ({media_type}): {videos_res}")
            elif videos_res:
                videos = videos_res.get('results', [])
                if videos:
                    preferred_videos = [v for v in videos if v['site'] == 'YouTube' and 'official trailer' in v.get('name', '').lower()]
                    if not preferred_videos:
                        preferred_videos = [v for v in videos if v['site'] == 'YouTube' and 'tráiler oficial' in v.get('name', '').lower()]
                    if not preferred_videos:
                        preferred_videos = [v for v in videos if v['site'] == 'YouTube' and v.get('type') in ['Trailer', 'Teaser']]
                    if not preferred_videos:
                        preferred_videos = [v for v in videos if v['site'] == 'YouTube']
                    if preferred_videos:
                        result["trailer_link"] = f"https://www.youtube.com/watch?v={preferred_videos[0]['key']}"

            if isinstance(providers_res, Exception):
                logger.error(f"Error fetching providers for {title} ({media_type}): {providers_res}")
            elif providers_res and 'results' in providers_res and 'PE' in providers_res['results']:
                providers = providers_res['results']['PE']
                result['watch_providers'] = {
                    'buy': [p['provider_name'] for p in providers.get('buy', [])],
                    'rent': [p['provider_name'] for p in providers.get('rent', [])],
                    'flatrate': [p['provider_name'] for p in providers.get('flatrate', [])]
                }

            if isinstance(credits_res, Exception):
                logger.error(f"Error fetching credits for {title} ({media_type}): {credits_res}")
            elif credits_res and 'cast' in credits_res:
                cast_data = credits_res['cast']
                sorted_cast = sorted(cast_data, key=lambda actor: (actor.get('order', 999), -actor.get('popularity', 0.0)))
                result['cast'] = [actor['name'] for actor in sorted_cast if actor.get('known_for_department') == 'Acting'][:5]

    except Exception as e:
        logger.error(f"Unhandled exception in search_media_data for {title} ({media_type}): {e}")
        raise YouTubeSearchError(detail=f"Failed to search TMDb for movie data: {e}")

    return result