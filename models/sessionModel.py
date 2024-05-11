from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from enum import Enum

class SenderType(Enum):
    bot = "bot"
    user = "user"

class Message(BaseModel):
    sender: SenderType
    time: datetime = Field(default_factory=datetime.now)
    message: str

class SessionCreate(BaseModel):
    sessionID: str
    messages: List[Message]

class Session(BaseModel):
    sessionID: str
    messages: List[Message]

