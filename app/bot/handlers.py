from app.services.llm_agent import get_llm_response
from app.core.utils import is_saludo, parse_message
from app.data.prompt import SALUDO_INICIAL
from app.services.tmdb_service import search_movie, get_movie_details
import re

async def generate_bot_response(text: str, chat_id: int) -> tuple[str, dict | None]:
    last_line = text.strip().split("\n")[-1]
    if last_line.lower().startswith("user: "):
        user_input = last_line[6:].strip()
    else:
        user_input = last_line

    if is_saludo(user_input):
        return SALUDO_INICIAL, None

    raw_response = await get_llm_response(text)
    parsed_response = parse_message(raw_response)

    movie_title = None
    match = re.search(r'"([^"]+)"|Recomiendo:\s*([^\n]+)', parsed_response)
    if match:
        movie_title = match.group(1) or match.group(2)
        if movie_title:
            movie_title = movie_title.strip()

    inline_keyboard = None
    if movie_title:
        try:
            search_results = await search_movie(movie_title)
            if search_results and len(search_results) > 0:
                movie_id = search_results[0]['id']
                movie_details = await get_movie_details(movie_id)

                buttons = []
                if 'videos' in movie_details and 'results' in movie_details['videos']:
                    for video in movie_details['videos']['results']:
                        if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                            buttons.append({"text": "Ver tráiler", "url": f"https://www.youtube.com/watch?v={video['key']}"})
                            break

                if 'watch/providers' in movie_details and 'results' in movie_details['watch/providers']:
                    if 'MX' in movie_details['watch/providers']['results']:
                        providers = movie_details['watch/providers']['results']['MX']
                        if 'flatrate' in providers:
                            for provider in providers['flatrate']:
                                buttons.append({"text": f"Ver en {provider['provider_name']}", "url": providers['link']})
                                break

                if len(buttons) > 0:
                    buttons.append({"text": "Recomiéndame otra", "callback_data": "recommend_another"})
                    inline_keyboard = {"inline_keyboard": [buttons]}

        except Exception as e:
            print(f"Error al obtener datos de TMDB para '{movie_title}': {e}")

    return parsed_response, inline_keyboard