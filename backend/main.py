from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import auth, quiz, user, analytics, flashcards, chat
# Temporarily disable export routes due to PDF dependency issues
# from app.api.routes import export
from app.core.config import settings

app = FastAPI(
    title="Dynamic Quiz API",
    description="A modern quiz platform with LLM-powered question generation, comprehensive analytics, flashcard revision, PDF export, and real-time community chat",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://quizlet-production-0834.up.railway.app",
        "https://*.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(flashcards.router, prefix="/api/flashcards", tags=["Flashcards"])
# app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

# Mount static files for frontend
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    pass  # Static files might not exist in development

@app.get("/")
async def root():
    try:
        return FileResponse("static/index.html")
    except:
        return {
            "message": "🎉 Quizlet AI Quiz Generator API is running!",
            "version": "1.0.0",
            "status": "healthy",
            "endpoints": {
                "api_docs": "/docs",
                "health_check": "/health",
                "authentication": "/api/auth",
                "quiz_generation": "/api/quiz",
                "analytics": "/api/analytics",
                "flashcards": "/api/flashcards",
                "chat": "/api/chat"
            },
            "llm_providers": ["Google AI", "Groq", "Cohere"],
            "visit_docs": "https://quizlet-production-0834.up.railway.app/docs"
        }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Catch-all route for client-side routing
@app.get("/{full_path:path}")
async def catch_all(full_path: str, request: Request):
    # Don't interfere with API routes
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve the React app for all other routes
    try:
        return FileResponse("static/index.html")
    except:
        raise HTTPException(status_code=404, detail="Not found") 