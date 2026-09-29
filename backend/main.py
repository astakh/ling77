"""
WordFlow Backend — FastAPI application for spaced repetition language learning.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

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

# Middleware для логирования запросов и CORS
@app.middleware("http")
async def add_cors_and_log(request, call_next):
    logger.info(f"📨 {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
    
    # Получаем origin из запроса
    origin = request.headers.get("origin", "")
    
    # Проверяем что origin в списке разрешённых
    allowed_origins = settings.CORS_ORIGINS
    allow_origin = origin if origin in allowed_origins else (allowed_origins[0] if allowed_origins else "")
    
    # Обработка OPTIONS запросов (preflight)
    if request.method == "OPTIONS":
        from fastapi.responses import JSONResponse
        response = JSONResponse(content={"status": "ok"})
        response.headers["Access-Control-Allow-Origin"] = allow_origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "3600"
        logger.info(f"🔧 OPTIONS preflight → 200 (origin: {origin})")
        return response
    
    try:
        response = await call_next(request)
        logger.info(f"📤 {request.method} {request.url.path} → {response.status_code}")
        # Добавляем CORS заголовки ко всем ответам
        response.headers["Access-Control-Allow-Origin"] = allow_origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

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
