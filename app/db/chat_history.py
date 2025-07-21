from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat_history import ChatHistory
from app.schemas.chat_history import ChatHistoryCreate, ChatHistoryResponse


async def create_chat_history(db: AsyncSession, chat_history: ChatHistoryCreate):
    db_chat_history = ChatHistory(**chat_history.model_dump())
    db.add(db_chat_history)
    await db.commit()
    await db.refresh(db_chat_history)
    return ChatHistoryResponse(message="Chat history created", data=db_chat_history)