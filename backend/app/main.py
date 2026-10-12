import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.database.database import init_db
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.api.chat import router as chat_router
from app.api.essays import router as essays_router
from app.api.artifacts import router as artifacts_router
from app.api.config import router as config_router
from app.api.knowledge import router as knowledge_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Lenny Growth Assistant backend...")
    init_db()
    logger.info("Database tables initialized.")
    yield
    logger.info("Lenny Growth Assistant backend shutting down.")


app = FastAPI(
    title="The Lenny Growth Assistant API",
    description="Full-stack AI assistant grounded in Lenny's Podcast transcripts with Ship 30 for 30 essay generation and Claude-style side-by-side artifacts.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development allow all; configurable via settings.cors_origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "path": request.url.path}
    )

# Register Routers
app.include_router(health_router)
app.include_router(sessions_router)
app.include_router(chat_router)
app.include_router(essays_router)
app.include_router(artifacts_router)
app.include_router(config_router)
app.include_router(knowledge_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
