import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime

from models import ChatMessage, ChatResponse
from agent import AppointmentBookingAgent

app = FastAPI(title="Appointment Booking Agent API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent
    openai_api_key = os.getenv("OPENAI_API_KEY")
    agent = AppointmentBookingAgent(openai_api_key)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Appointment Booking Agent API is running!", "timestamp": datetime.now()}

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Main chat endpoint"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        # Process the message
        result = agent.process_message(message.message)
        
        return ChatResponse(
            response=result["response"],
            available_slots=result["available_slots"] if result["available_slots"] else None,
            booking_confirmed=result["booking_confirmed"],
            session_id=message.session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.post("/reset")
async def reset_conversation():
    """Reset the conversation state"""
    try:
        global agent
        openai_api_key = os.getenv("OPENAI_API_KEY")
        agent = AppointmentBookingAgent(openai_api_key)
        return {"message": "Conversation reset successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting conversation: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)