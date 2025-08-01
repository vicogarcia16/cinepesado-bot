import httpx
import json
import asyncio
from app.core.config import get_settings
from app.data.prompt import IDENTIFICATION_PROMPT, CREATIVE_PROMPT, SUGGESTION_PROMPT
from app.core.exceptions import LLMApiError
from app.services.tmdb_service import search_media_data
from app.db import chat_history


settings = get_settings()

OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY
OPENROUTER_MODEL = settings.OPENROUTER_MODEL

async def _call_llm_api(messages: list[dict], is_json: bool = False) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1500
    }
    if is_json:
        data["response_format"] = {"type": "json_object"}

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            res = await client.post(url, headers=headers, json=data)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPStatusError, KeyError, IndexError) as e:
            error_detail = f"Failed to get a valid response from the LLM API. Error: {e}"
            if hasattr(res, 'text'):
                error_detail += f" Raw response: {res.text}"
            raise LLMApiError(detail=error_detail)

async def get_llm_response(db, chat_id: int, user_message: str) -> str:
    history_response = await chat_history.get_last_chats(db, chat_id)
    history = history_response.data

    identification_messages = [
        {"role": "system", "content": IDENTIFICATION_PROMPT},
    ]
    for entry in history:
        identification_messages.append({"role": "user", "content": entry.message})
        identification_messages.append({"role": "assistant", "content": entry.response})
    identification_messages.append({"role": "user", "content": user_message})

    identification_response = await _call_llm_api(identification_messages, is_json=True)
    try:
        media_list = json.loads(identification_response).get("media", [])
    except json.JSONDecodeError:
        media_list = []

    if not media_list:
        suggestion_messages = [
            {"role": "system", "content": SUGGESTION_PROMPT},
        ]
        for entry in history:
            suggestion_messages.append({"role": "user", "content": entry.message})
            suggestion_messages.append({"role": "assistant", "content": entry.response})
        suggestion_messages.append({"role": "user", "content": user_message})

        suggestion_response = await _call_llm_api(suggestion_messages, is_json=True)
        try:
            suggested_media_list = json.loads(suggestion_response).get("media", [])
        except json.JSONDecodeError:
            suggested_media_list = []
        
        if not suggested_media_list:
            creative_prompt_content = CREATIVE_PROMPT.format(user_query=user_message, media_data="")
            creative_messages = [
                {"role": "system", "content": creative_prompt_content},
            ]
            for entry in history:
                creative_messages.append({"role": "user", "content": entry.message})
                creative_messages.append({"role": "assistant", "content": entry.response})
            creative_messages.append({"role": "user", "content": user_message})
            return await _call_llm_api(creative_messages)
        
        media_list = suggested_media_list

    tasks = [search_media_data(media.get("type"), media.get("title"), media.get("year")) for media in media_list]
    media_data_results = await asyncio.gather(*tasks)

    formatted_media_data = []
    for media, data in zip(media_list, media_data_results):
        formatted_media_data.append({
            "title": media.get("title"),
            "type": media.get("type"),
            "year": media.get("year"),
            "trailer_link": data.get("trailer_link"),
            "poster_url": data.get("poster_url"),
            "watch_providers": data.get("watch_providers"),
            "cast": data.get("cast")
        })

    creative_prompt_content = CREATIVE_PROMPT.format(user_query=user_message, media_data=json.dumps(formatted_media_data, indent=2, ensure_ascii=False))
    creative_messages = [
        {"role": "system", "content": creative_prompt_content},
    ]
    for entry in history:
        creative_messages.append({"role": "user", "content": entry.message})
        creative_messages.append({"role": "assistant", "content": entry.response})
    creative_messages.append({"role": "user", "content": user_message})

    final_response = await _call_llm_api(creative_messages)

    return final_response.strip()