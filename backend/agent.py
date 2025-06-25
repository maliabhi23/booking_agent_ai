import os, re
from datetime import datetime, timedelta
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from calendar_service import GoogleCalendarService

class ConversationState:
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.intent: str = ""
        self.extracted_datetime: datetime = None
        self.duration: int = 60
        self.available_slots: List[Dict[str, str]] = []
        self.selected_slot: Dict[str, str] = None
        self.booking_confirmed: bool = False

class AppointmentBookingAgent:
    def __init__(self, openai_api_key=None):
        self.calendar_service = GoogleCalendarService()
        if openai_api_key:
            self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key=openai_api_key)
        else:
            self.llm = None
        self.state = ConversationState()

    def process_message(self, message: str) -> Dict[str, Any]:
        self.state.messages.append({"role": "user", "content": message})
        last = message.lower()

        # Intent detection
        if any(w in last for w in ["book", "schedule", "appointment", "meeting"]):
            intent = "book_appointment"
        elif any(w in last for w in ["available", "free", "time"]):
            intent = "check_availability"
        elif any(w in last for w in ["confirm", "yes", "book it"]):
            intent = "confirm_booking"
        elif any(w in last for w in ["cancel", "no", "different"]):
            intent = "modify_request"
        else:
            intent = "clarify"

        # Date extraction
        dt = datetime.now() + timedelta(days=1)
        if "tomorrow" in last: dt = datetime.now() + timedelta(days=1)
        elif "next week" in last: dt = datetime.now() + timedelta(days=7)
        dt = dt.replace(hour=10, minute=0)

        # Flow logic
        response = ""
        if intent in ["book_appointment", "check_availability"]:
            slots = self.calendar_service.find_available_slots(dt, dt + timedelta(days=7), 60)
            self.state.available_slots = slots
            if slots:
                response = "Available slots:\n" + "\n".join(
                    f"{i+1}. {s['display']}" for i, s in enumerate(slots[:5])
                )
                response += "\nWhich slot would you prefer?"
            else:
                response = "No available slots found in that period."
        elif intent == "confirm_booking":
            nums = re.findall(r"\d+", last)
            if nums and self.state.available_slots:
                idx = int(nums[0])-1
                if 0 <= idx < len(self.state.available_slots):
                    sel = self.state.available_slots[idx]
                    success = self.calendar_service.book_appointment(
                        datetime.strptime(sel["start"], "%Y-%m-%d %H:%M"),
                        datetime.strptime(sel["end"], "%Y-%m-%d %H:%M"),
                        "Meeting", ""
                    )
                    if success:
                        response = f"Booked for {sel['display']}."
                    else:
                        response = "Booking failed. Try again."
                    self.state.booking_confirmed = success
                else:
                    response = "Invalid slot. Please choose again."
            else:
                response = "Please select a valid slot number."
        elif intent == "modify_request":
            response = "Okay, let’s pick a new time. When would you like?"
        else:
            response = "Hi! I can help you check availability or book appointments. When would work for you?"

        self.state.messages.append({"role": "assistant", "content": response})
        return {
            "response": response,
            "available_slots": [s["display"] for s in self.state.available_slots],
            "booking_confirmed": self.state.booking_confirmed
        }
