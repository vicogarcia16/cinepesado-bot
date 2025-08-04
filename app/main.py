import logging
from fastapi import FastAPI
from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.routes import telegram
from contextlib import asynccontextmanager
import httpx
from app.db.database import engine
from app.models.chat_history import Base

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with httpx.AsyncClient() as client:
            await client.post(settings.setwebhook_url)  
    yield
    
app = FastAPI(
    title="TelePesado Bot API",
    description="API para el bot de Telegram TelePesado, un recomendador de películas y series.",
    version=f"{settings.API_VERSION}.0.0",
    docs_url="/",
    redoc_url="/redoc",
    lifespan=lifespan
)

@app.head("/ping", tags=["root"])
async def ping():
    return {"message": "pong"}

register_exception_handlers(app)
app.include_router(telegram.router, prefix=settings.api_prefix)