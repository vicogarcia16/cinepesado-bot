from app.services.llm_agent import get_llm_response
from app.core.utils import is_saludo, parse_message
from app.data.prompt import SALUDO_INICIAL
from app.services.tmdb_service import search_movie, get_movie_details
import re

async def generate_bot_response(text: str) -> tuple[str, dict | None]:
    last_line = text.strip().split("\n")[-1]
    if last_line.lower().startswith("user: "):
        user_input = last_line[6:].strip()
    else:
        user_input = last_line

    if is_saludo(user_input):
        return SALUDO_INICIAL, None

    raw_response = await get_llm_response(text)
    parsed_response = parse_message(raw_response)
    
    movie_data = re.findall(
        r'\"([^\"]+)\".*?(?:\[Trailer\]\((https?://www\.youtube\.com/watch\?v=[a-zA-Z0-9_-]+)\))?',
        parsed_response,
        re.DOTALL
    )

    all_buttons = []

    for title, llm_trailer_url in movie_data:
        movie_title = title.strip()
        movie_specific_buttons = []
        movie_id = None
        movie_details = None

        try:
            search_results = await search_movie(movie_title)
            if search_results and len(search_results) > 0:
                movie_id = search_results[0]['id']
                movie_details = await get_movie_details(movie_id)
        except Exception as e:
            print(f"Error al obtener datos de TMDB para '{movie_title}': {e}")


        if llm_trailer_url:
            movie_specific_buttons.append({"text": f"Tráiler: {movie_title}", "url": llm_trailer_url})
        elif movie_details and 'videos' in movie_details and 'results' in movie_details['videos']:
            for video in movie_details['videos']['results']:
                if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                    movie_specific_buttons.append({"text": f"Tráiler: {movie_title}", "url": f"https://www.youtube.com/watch?v={video['key']}"})
                    break

        if movie_details and 'watch/providers' in movie_details and 'results' in movie_details['watch/providers']:
            if 'MX' in movie_details['watch/providers']['results']:
                providers = movie_details['watch/providers']['results']['MX']
                if 'flatrate' in providers:
                    for provider in providers['flatrate']:
                        movie_specific_buttons.append({"text": f"Ver en {provider['provider_name']}: {movie_title}", "url": providers['link']})
                        break

        if movie_specific_buttons:
            all_buttons.extend(movie_specific_buttons)

    inline_keyboard = None
    if all_buttons:
        grouped_movie_buttons = [[button] for button in all_buttons]
        inline_keyboard = {"inline_keyboard": grouped_movie_buttons}

    return parsed_response, inline_keyboard