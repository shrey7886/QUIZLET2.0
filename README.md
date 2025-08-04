# Dynamic Quiz Application

A modern, intelligent quiz platform powered by LLM with dynamic question generation, real-time scoring, and personalized learning analytics.

## Features

- 🚀 **Dynamic Quiz Generation**: Real-time LLM-powered questions based on user-selected topics
- ⚡ **Fast Performance**: Sub-2 second question generation with optimized prompts
- 🎯 **Smart Configuration**: Topic selection, difficulty levels, question count (1-15), and time limits
- 📊 **Comprehensive Analytics**: Detailed results with explanations and performance tracking
- 🤖 **AI Tutor**: Smart chatbot to help users understand mistakes and clarify doubts
- 📚 **History Tracking**: Complete quiz history with no question repetition per user
- 🔐 **Secure Authentication**: JWT-based user authentication and session management

## Tech Stack

### Frontend
- React 18 with TypeScript
- Tailwind CSS for styling
- React Router for navigation
- React Context for state management
- React Hook Form for form handling

### Backend
- FastAPI (Python) with async support
- SQLAlchemy ORM with PostgreSQL
- Redis for caching and session management
- OpenAI GPT-4o for question generation
- JWT authentication

### Database
- PostgreSQL for persistent data storage
- Redis for caching and real-time features

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL
- Redis
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd quizlet
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Environment Configuration**
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:password@localhost/quizlet
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key

# Frontend (.env)
REACT_APP_API_URL=http://localhost:8000
```

5. **Database Setup**
```bash
cd backend
alembic upgrade head
```

6. **Run the Application**
```bash
# Backend (Terminal 1)
cd backend
uvicorn main:app --reload

# Frontend (Terminal 2)
cd frontend
npm start
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Project Structure

```
quizlet/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Key Features Implementation

### Dynamic Question Generation
- Optimized prompts for consistent JSON output
- Caching system to avoid redundant API calls
- Parallel processing for multiple questions

### Performance Optimizations
- Redis caching for popular topics
- Database indexing for fast queries
- Async/await patterns throughout the stack

### User Experience
- Real-time quiz timer
- Question navigation
- Progress indicators
- Responsive design

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details. 