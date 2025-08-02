import asyncio
import tmdbsimple as tmdb
from app.core.config import get_settings
from app.core.exceptions import YouTubeSearchError

settings = get_settings()
TMDB_API_KEY = settings.TMDB_API_KEY
tmdb.API_KEY = TMDB_API_KEY

async def _search_media_by_year_and_title(search_client, media_type: str, title: str, year: str):
    search_method = search_client.movie if media_type == 'PELICULA' else search_client.tv
    date_key = 'release_date' if media_type == 'PELICULA' else 'first_air_date'
    
    best_match = None
    
    def find_best_in_results(results, target_year=None):
        best_local_match = None
        best_local_match_has_poster = False
        min_local_year_diff = float('inf')

        for result in results:
            has_poster = result.get('poster_path')
            current_year_str = str(result.get(date_key, ''))[:4]
            current_year = int(current_year_str) if current_year_str.isdigit() else None

            if target_year and current_year is not None:
                year_diff = abs(int(target_year) - current_year)
            else:
                year_diff = 0

            if has_poster:
                if not best_local_match_has_poster or (target_year and year_diff < min_local_year_diff):
                    best_local_match = result
                    best_local_match_has_poster = True
                    min_local_year_diff = year_diff
            elif not best_local_match_has_poster and (target_year and year_diff < min_local_year_diff):
                best_local_match = result
                min_local_year_diff = year_diff
            elif not best_local_match:
                best_local_match = result
                min_local_year_diff = year_diff

        return best_local_match

    response_with_year = await asyncio.to_thread(search_method, query=title, year=year)
    if response_with_year['results']:
        best_match = find_best_in_results(response_with_year['results'], year)
        if best_match and best_match.get('poster_path'):
            return best_match

    response_no_year = await asyncio.to_thread(search_method, query=title)
    if response_no_year['results']:
        temp_best_match_no_year = find_best_in_results(response_no_year['results'], year)
        if temp_best_match_no_year and temp_best_match_no_year.get('poster_path'):
            return temp_best_match_no_year
        elif not best_match:
            best_match = temp_best_match_no_year

    all_results = []
    if response_with_year['results']:
        all_results.extend(response_with_year['results'])
    if response_no_year['results']:
        all_results.extend(response_no_year['results'])
    
    for result in all_results:
        if result.get('poster_path'):
            return result

    return best_match

async def search_media_data(media_type: str, title: str, year: str) -> dict:
    
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
            if videos:
                for video in videos:
                    if video['site'] == 'YouTube' and video.get('type') in ['Trailer', 'Teaser']:
                        result["trailer_link"] = f"https://www.youtube.com/watch?v={video['key']}"
                        break
                
                if not result["trailer_link"]:
                    for video in videos:
                        if video['site'] == 'YouTube':
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
                cast_data = details['credits']['cast']
                sorted_cast = sorted(cast_data, key=lambda actor: (actor.get('order', 999), -actor.get('popularity', 0.0)))
                result['cast'] = [actor['name'] for actor in sorted_cast if actor.get('known_for_department') == 'Acting'][:5]

    except Exception as e:
        raise YouTubeSearchError(detail=f"Failed to search TMDb for movie data: {e}")

    return result