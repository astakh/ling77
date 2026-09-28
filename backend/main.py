"""
WordFlow Backend — FastAPI application for spaced repetition language learning.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes import auth, onboarding, dashboard, lesson, vocabulary, admin, dictionaries

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting WordFlow backend...")
    yield
    logger.info("Shutting down WordFlow backend...")


app = FastAPI(
    title="WordFlow API",
    description="Spaced repetition language learning platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - должен быть ДО всех роутов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Временно разрешаем все origins для отладки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"📨 {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
    response = await call_next(request)
    logger.info(f"📤 {request.method} {request.url.path} → {response.status_code}")
    return response

# Явный обработчик OPTIONS для всех путей
@app.api_route("/{path:path}", methods=["OPTIONS"])
async def options_handler(path: str):
    logger.info(f"🔧 OPTIONS request for /{path}")
    return {}

# Include routers
app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(dashboard.router)
app.include_router(lesson.router)
app.include_router(vocabulary.router)
app.include_router(dictionaries.router)
app.include_router(admin.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "wordflow"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
