import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="AI Appointment Booking Agent",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constants
BACKEND_URL = "http://localhost:8000"  # Change this to your deployed backend URL

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .chat-message.user {
        background-color: #e3f2fd;
        flex-direction: row-reverse;
    }
    .chat-message.assistant {
        background-color: #f5f5f5;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin: 0 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
    }
    .chat-message.user .avatar {
        background-color: #1976d2;
    }
    .chat-message.assistant .avatar {
        background-color: #4caf50;
    }
    .chat-message .message {
        flex: 1;
        padding: 0.5rem 0;
    }
    .available-slots {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    .booking-confirmed {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "backend_available" not in st.session_state:
        st.session_state.backend_available = check_backend_health()

def check_backend_health():
    """Check if backend is available"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_message_to_backend(message: str):
    """Send message to backend and get response"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": message},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "response": "Sorry, I encountered an error. Please try again.",
                "available_slots": None,
                "booking_confirmed": False
            }
    
    except requests.exceptions.RequestException:
        return {
            "response": "Sorry, I'm having trouble connecting to the booking service. Please try again later.",
            "available_slots": None,
            "booking_confirmed": False
        }

def reset_conversation():
    """Reset the conversation"""
    try:
        requests.post(f"{BACKEND_URL}/reset", timeout=5)
        st.session_state.messages = []
        # st.rerun()
    except:
        st.error("Failed to reset conversation. Please refresh the page.")

def display_message(message, is_user=False):
    """Display a chat message"""
    role = "user" if is_user else "assistant"
    avatar = "👤" if is_user else "🤖"
    
    with st.container():
        col1, col2 = st.columns([1, 10] if not is_user else [10, 1])
        
        if is_user:
            with col1:
                st.markdown(f"**You:** {message}")
        else:
            with col2:
                st.markdown(f"**Assistant:** {message}")

def main():
    """Main application"""
    initialize_session_state()
    
    # Header
    st.title("📅 AI Appointment Booking Agent")
    st.markdown("---")
    
    # Sidebar with info
    with st.sidebar:
        st.header("ℹ️ How it works")
        st.markdown("""
        1. **Tell me when**: Say when you'd like to meet
        2. **Check availability**: I'll show you open slots
        3. **Pick a time**: Choose your preferred slot
        4. **Confirm**: I'll book it for you!
        
        **Example messages:**
        - "I need a meeting tomorrow afternoon"
        - "Show me available times this Friday"
        - "Book a call for next week"
        """)
        
        st.markdown("---")
        
        # Reset conversation button
        if st.button("🔄 Start New Conversation"):
            reset_conversation()
    
    # Check backend availability
    if not st.session_state.backend_available:
        st.error("⚠️ The booking service is currently unavailable. Please try again later.")
        st.info("💡 **For developers**: Make sure the FastAPI backend is running on http://localhost:8000")
        return
    
    # Chat interface
    st.subheader("💬 Chat with the Booking Agent")
    
    # Display conversation history
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    
                    # Display available slots if any
                    if message.get("available_slots"):
                        st.markdown("### 📅 Available Time Slots:")
                        for j, slot in enumerate(message["available_slots"]):
                            st.markdown(f"**{j+1}.** {slot}")
                        st.info("💡 Just tell me the number of your preferred slot!")
                    
                    # Display booking confirmation
                    if message.get("booking_confirmed"):
                        st.success("✅ **Appointment Booked Successfully!**")
                        st.balloons()
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to session state
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input
        })
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(user_input)
        
        # Send to backend and get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_data = send_message_to_backend(user_input)
            
            # Display assistant response
            st.write(response_data["response"])
            
            # Display available slots if any
            if response_data.get("available_slots"):
                st.markdown("### 📅 Available Time Slots:")
                for j, slot in enumerate(response_data["available_slots"]):
                    st.markdown(f"**{j+1}.** {slot}")
                st.info("💡 Just tell me the number of your preferred slot!")
            
            # Display booking confirmation
            if response_data.get("booking_confirmed"):
                st.success("✅ **Appointment Booked Successfully!**")
                st.balloons()
        
        # Add assistant response to session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_data["response"],
            "available_slots": response_data.get("available_slots"),
            "booking_confirmed": response_data.get("booking_confirmed")
        })
        
        # Rerun to update the display
        st.rerun()
    
    # Quick action buttons
    # Quick Action Buttons - One-time Trigger with Session State
st.markdown("---")
st.subheader("🚀 Quick Actions")

# Initialize flags
for key in ["clicked_tomorrow", "clicked_friday", "clicked_next_week", "clicked_help"]:
    if key not in st.session_state:
        st.session_state[key] = False

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📅 Tomorrow afternoon") and not st.session_state.clicked_tomorrow:
        st.session_state.messages.append({"role": "user", "content": "I want to book a meeting tomorrow afternoon"})
        st.session_state.clicked_tomorrow = True
        st.rerun()

with col2:
    if st.button("📅 This Friday") and not st.session_state.clicked_friday:
        st.session_state.messages.append({"role": "user", "content": "Do you have any free time this Friday?"})
        st.session_state.clicked_friday = True
        st.rerun()

with col3:
    if st.button("📅 Next week") and not st.session_state.clicked_next_week:
        st.session_state.messages.append({"role": "user", "content": "Book a meeting between 3-5 PM next week"})
        st.session_state.clicked_next_week = True
        st.rerun()

with col4:
    if st.button("❓ Help") and not st.session_state.clicked_help:
        help_message = """I can help you book appointments! Here are some things you can say:

• "I need a meeting tomorrow afternoon"  
• "Show me available times this Friday"  
• "Book a call for next week"  
• "Do you have any free time between 2-4 PM?"  

Just tell me when you'd like to meet and I'll check my calendar for you! 😊"""
        st.session_state.messages.append({"role": "assistant", "content": help_message})
        st.session_state.clicked_help = True
        st.rerun()

    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8em;'>"
        "🤖 Powered by LangGraph, FastAPI, and Streamlit | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
        
        # Backend status
    if st.session_state.backend_available:
        st.success("🟢 Service Online")
    else:
        st.error("🔴 Service Offline")
        
    if st.button("🔄 Retry Connection"):
        st.session_state.backend_available = check_backend_health()
        st.rerun()
        
    st.markdown("---")