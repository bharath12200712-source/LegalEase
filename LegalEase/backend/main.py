from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.config import get_settings


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    description="AI-assisted legal document drafting API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def root():

    return {
        "service": settings.app_name,
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "gemini_configured": bool(
            settings.gemini_api_key
        ),
    }


app.include_router(router)