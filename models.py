from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class MessagePayload(BaseModel):
    content: str = Field(..., description="訊息內容")
    channel_id: Optional[int] = Field(None, description="Discord 頻道 ID，不指定則使用預設頻道")
    embed: Optional[Dict[str, Any]] = Field(None, description="Embed 物件")

class MessageResponse(BaseModel):
    success: bool
    message_id: Optional[int] = None
    error: Optional[str] = None
    timestamp: datetime

class WebSocketMessage(BaseModel):
    type: str
    message: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None
