from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

# Import route modules
from .routes import summarizer, questions
from .schemas.common import HealthResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Application startup time
startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 AI Academic Assistant API is starting up...")
    yield
    logger.info("🛑 AI Academic Assistant API is shutting down...")


# Create FastAPI application
app = FastAPI(
    title="AI Academic Assistant API",
    description="Summarization + question generation microservice",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:8080",  # Alternative frontend port
        "https://v0.app",         # V0 frontend
        "https://*.vercel.app",   # Vercel deployments
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(summarizer.router)
app.include_router(questions.router)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "AI Academic Assistant API", "version": "1.0.0", "docs": "/docs"}


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", uptime=time.time() - startup_time)


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=f"HTTP_{exc.status_code}",
            message=exc.detail
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred. Please try again later.",
            details={"error_type": type(exc).__name__}
        ).dict()
    )


# API information endpoints
@app.get("/api/info")
async def api_info():
    return {
        "api_name": "AI Academic Assistant API",
        "version": "1.0.0",
        "description": "Academic assistance core features",
        "features": {
            "summarizer": {
                "description": "Parse docs + summaries",
                "supported_formats": ["PDF", "DOCX", "TXT", "PPTX"],
                "capabilities": ["Text extraction", "Image extraction", "Table extraction", "AI summarization"],
                "summary_types": ["paragraph", "bullet_points", "key_concepts", "outline", "academic"],
                "summary_lengths": ["short", "medium", "long", "custom"]
            },
            "questions": {
                "description": "Generate question sets",
                "question_types": ["mcq", "short", "long"],
                "exam_types": ["cat1", "cat2", "fat"],
                "difficulty_levels": ["easy", "medium", "hard"],
                "features": ["Course selection", "Previous year papers", "Custom question count"]
            }
        },
        "endpoints_count": len(app.routes),
        "uptime": time.time() - startup_time
    }


@app.get("/api/stats")
async def api_stats():
    return {
        "total_routes": len(app.routes),
        "uptime_seconds": time.time() - startup_time,
        "services": {
            "summarizer": "active",
            "questions": "active"
        },
        "version": "1.0.0",
        "environment": "development"
    }