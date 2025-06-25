# AI Appointment Booking Agent 📅

A conversational AI agent that helps users book appointments through natural language chat. Built with LangGraph, FastAPI, and Streamlit.

## 🚀 Features

- **Natural Language Processing**: Understands appointment requests in plain English
- **Calendar Integration**: Connects with Google Calendar for real availability
- **Intelligent Conversation Flow**: Guides users through the booking process
- **Real-time Availability**: Shows actual free time slots
- **Booking Confirmation**: Automatically creates calendar events
- **User-friendly Interface**: Clean chat interface with quick actions

## 🛠 Tech Stack

- **Backend**: FastAPI + LangGraph
- **Frontend**: Streamlit
- **Calendar**: Google Calendar API
- **AI**: OpenAI GPT (optional) + custom logic
- **Deployment**: Ready for cloud deployment

## 📋 Prerequisites

1. Python 3.8 or higher
2. Google Calendar API credentials (optional - will use mock data otherwise)
3. OpenAI API key (optional - will use rule-based responses otherwise)

## 🔧 Setup Instructions

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd appointment-booking-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Optional: Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

### 3. Google Calendar Setup (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Download `credentials.json` and place in project root
6. Run the backend once to complete OAuth flow

### 4. Frontend Setup

```bash
cd ../frontend
pip install -r requirements.txt
```

## 🚀 Running the Application

### Start Backend Server

```bash
cd backend
python main.py
# Backend will run on http://localhost:8000
```

### Start Frontend Application

```bash
cd frontend
streamlit run app.py
# Frontend will open in your browser at http://localhost:8501
```

## 💬 Usage Examples

The agent can handle various appointment requests:

### Basic Booking
- **User**: "I want to schedule a call for tomorrow afternoon"
- **Agent**: Shows available slots and guides through selection

### Availability Check
- **User**: "Do you have any free time this Friday?"
- **Agent**: Lists all available slots for Friday

### Specific Time Requests
- **User**: "Book a meeting between 3-5 PM next week"
- **Agent**: Finds slots within that time range

### Slot Selection
- **User**: "I'll take option 2"
- **Agent**: Confirms and books the selected appointment

## 🏗 Architecture

```
┌─────────────────┐    HTTP     ┌─────────────────┐
│   Streamlit     │◄────────────┤    FastAPI      │
│   Frontend      │             │    Backend      │
└─────────────────┘             └─────────────────┘
                                          │
                                          ▼
                                ┌─────────────────┐
                                │   LangGraph     │
                                │     Agent       │
                                └─────────────────┘
                                          │
                                          ▼
                                ┌─────────────────┐
                                │ Google Calendar │
                                │      API        │
                                └─────────────────┘
```

## 🔄 Conversation Flow

The agent uses LangGraph to manage conversation state:

1. **Intent Understanding**: Analyzes user message
2. **DateTime Extraction**: Parses time preferences
3. **Availability Check**: Queries calendar for free slots
4. **Slot Selection**: Handles user's choice
5. **Booking Confirmation**: Creates calendar event

## 🌐 Deployment Options

### Option 1: Local Development
- Backend: `python main.py`
- Frontend: `streamlit run app.py`

### Option 2: Cloud Deployment
- Backend: Deploy to Heroku, Railway, or similar
- Frontend: Deploy to Streamlit Cloud
- Update `BACKEND_URL` in frontend app

### Option 3: Docker (Coming Soon)
```bash
docker-compose up
```

## 🔧 Configuration

### Environment Variables

```bash
# Optional - for enhanced AI responses
OPENAI_API_KEY=your_openai_api_key

# Optional - for real Google Calendar integration
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Backend configuration
PORT=8000
HOST=0.0.0.0
```

### Calendar Settings

Modify `calendar_service.py` to customize:
- Business hours (default: 9 AM - 5 PM)
- Meeting duration (default: 60 minutes)
- Available days (default: Monday - Friday)

## 🧪 Testing

### Manual Testing

1. Start both backend and frontend
2. Try various appointment requests
3. Check calendar integration (if configured)

### Automated Testing (Future Enhancement)

```bash
# Unit tests
pytest backend/tests/

# Integration tests
pytest tests/integration/
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend not connecting**
   - Check if FastAPI server is running on port 8000
   - Verify CORS settings in main.py

2. **Calendar integration failing**
   - Ensure credentials.json is in correct location
   - Complete OAuth flow by running backend once

3. **OpenAI API errors**
   - Check API key validity
   - Verify account has sufficient credits

### Mock Mode

The application works without external APIs:
- Uses mock calendar data
- Provides rule-based responses
- Perfect for development and testing

## 📈 Future Enhancements

- [ ] Multiple calendar support
- [ ] Email notifications
- [ ] Meeting types and durations
- [ ] Recurring appointments
- [ ] Integration with other calendar systems
- [ ] Voice interface
- [ ] Mobile app

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LangGraph for conversation management
- FastAPI for robust backend framework
- Streamlit for rapid frontend development
- Google Calendar API for calendar integration

---

**Ready to deploy? Follow the setup instructions and start booking appointments with AI! 🎉**
