from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List


class ChatHistoryCreate(BaseModel):
    chat_id: int
    message: str
    response: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "chat_id": 123456789,
                "message": "Hello, world!",
                "response": "Hello, world!"
            }
        }
    }
    
class ChatHistoryView(BaseModel):
    id: int
    chat_id: int
    message: str
    response: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    
class ChatHistoryResponse(BaseModel):
    message: str
    data: ChatHistoryView
    
class ChatHistoryListResponse(BaseModel):
    message: str
    data: List[ChatHistoryView]