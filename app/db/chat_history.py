from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat_history import ChatHistory
from app.schemas.chat_history import (
    ChatHistoryCreate,
    ChatHistoryResponse,
    ChatHistoryListResponse,
)
from sqlalchemy import select, desc


async def create_chat_history(db: AsyncSession, chat_history: ChatHistoryCreate):
    db_chat_history = ChatHistory(**chat_history.model_dump())
    db.add(db_chat_history)
    await db.commit()
    await db.refresh(db_chat_history)
    return ChatHistoryResponse(message="Chat history created", data=db_chat_history)


async def get_last_chats(db: AsyncSession, chat_id: int, limit: int = 5):
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.chat_id == chat_id)
        .order_by(desc(ChatHistory.created_at))
        .limit(limit)
    )
    chat_history = result.scalars().all()
    if not chat_history:
        return ChatHistoryListResponse(message="No chat history found", data=[])

    return ChatHistoryListResponse(message="Chat history found", data=chat_history)
