from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    available_slots: Optional[List[str]] = None
    booking_confirmed: Optional[bool] = None
    session_id: str

class TimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    title: str = "Meeting"

class BookingRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    title: str
    description: Optional[str] = None