from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import auth, quiz, user, analytics, flashcards, chat, tenants
# Temporarily disable export routes due to PDF dependency issues
# from app.api.routes import export
from app.core.config import settings
import os

app = FastAPI(
    title="Quizlet AI Quiz Generator - Multitenant",
    description="A modern multitenant quiz platform with LLM-powered question generation, comprehensive analytics, flashcard revision, and real-time community chat",
    version="2.0.0"
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://quizlet-production-0834.up.railway.app",
        "https://*.up.railway.app",
        "https://*.render.com",
        "*"  # Allow all origins for development
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
app.include_router(tenants.router, prefix="/api/tenants", tags=["Tenants"])

# Mount static files for frontend
try:
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    elif os.path.exists("frontend/build"):
        app.mount("/static", StaticFiles(directory="frontend/build"), name="static")
except Exception as e:
    print(f"Warning: Could not mount static files: {e}")

@app.get("/")
async def root():
    """Serve the React app or API info"""
    try:
        # Try to serve the React app
        if os.path.exists("static/index.html"):
            return FileResponse("static/index.html")
        elif os.path.exists("frontend/build/index.html"):
            return FileResponse("frontend/build/index.html")
    except:
        pass
    
    # Fallback to API info
    return {
        "message": "🎉 Quizlet AI Quiz Generator API is running!",
        "version": "2.0.0",
        "status": "healthy",
        "architecture": "multitenant",
        "features": [
            "AI-powered quiz generation",
            "Comprehensive analytics dashboard",
            "Flashcard learning system",
            "Real-time community chat",
            "Progress tracking",
            "Multiple LLM providers support",
            "Schema-based multitenancy",
            "Tenant isolation",
            "Neon PostgreSQL database"
        ],
        "endpoints": {
            "api_docs": "/docs",
            "health_check": "/health",
            "authentication": "/api/auth",
            "quiz_generation": "/api/quiz",
            "analytics": "/api/analytics",
            "flashcards": "/api/flashcards",
            "chat": "/api/chat",
            "tenant_management": "/api/tenants"
        },
        "llm_providers": ["Google AI", "Groq", "Cohere"],
        "multitenant_features": {
            "schema_isolation": "Each tenant has isolated database schema",
            "tenant_management": "Create, manage, and monitor tenants",
            "data_isolation": "Complete data separation between tenants",
            "scalability": "Horizontal scaling with connection pooling"
        },
        "frontend": "If you see this, the frontend is not built. Run 'npm run build' in the frontend directory."
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "architecture": "multitenant",
        "database": "Neon PostgreSQL",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Quizlet AI Quiz Generator API",
        "version": "1.0.0",
        "description": "A comprehensive quiz platform with AI-powered features",
        "endpoints": {
            "authentication": "/api/auth",
            "quiz": "/api/quiz", 
            "analytics": "/api/analytics",
            "flashcards": "/api/flashcards",
            "chat": "/api/chat",
            "user": "/api/user"
        }
    }

# Catch-all route for client-side routing
@app.get("/{full_path:path}")
async def catch_all(full_path: str, request: Request):
    # Don't interfere with API routes
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve the React app for all other routes
    try:
        if os.path.exists("static/index.html"):
            return FileResponse("static/index.html")
        elif os.path.exists("frontend/build/index.html"):
            return FileResponse("frontend/build/index.html")
    except:
        pass
    
    raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 