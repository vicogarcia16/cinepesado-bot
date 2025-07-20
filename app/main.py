from fastapi import FastAPI
from app.core.config import get_settings
from app.routes import telegram
from contextlib import asynccontextmanager
import httpx
from app.db.database import engine, Base


settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        print("Conectando y creando tablas...")
        await conn.run_sync(Base.metadata.create_all)
        print("¡Listo!")
        
    async with httpx.AsyncClient() as client:
            webhook_url = f"{settings.BASE_URL}/api/telegram/webhook/"
            await client.post(
                f"{settings.api_telegram}/setWebhook",
                params={"url": webhook_url}
            )
    yield
    
app = FastAPI(
    title="CinePesado Bot API",
    description="API para el bot de Telegram de CinePesado",
    version=f"{settings.API_VERSION}.0.0",
    docs_url="/",
    redoc_url="/redoc",
    lifespan=lifespan
)

@app.head("/ping", tags=["root"])
async def ping():
    return {"message": "pong"}

app.include_router(telegram.router, prefix=settings.api_prefix)