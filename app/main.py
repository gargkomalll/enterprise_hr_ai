from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.utils.config import settings
from app.utils.logger import logger

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Enterprise HR AI Workforce Intelligence & Upskilling Platform Backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.on_event("startup")
def startup_event():
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION} backend server...")

@app.get("/")
def root():
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }
