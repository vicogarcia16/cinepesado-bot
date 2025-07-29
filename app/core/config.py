from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str
    TELEGRAM_API_URL: str
    BASE_URL: str
    DATABASE_URL: str
    API_VERSION: str = '1'
    TMDB_API_KEY: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    @property
    def api_prefix(self) -> str:
        return f"/api/v{self.API_VERSION}"
    
    @property
    def api_telegram(self) -> str:
        return f"{self.TELEGRAM_API_URL}{self.TELEGRAM_TOKEN}"
    
    @property
    def webhook_url(self) -> str:
        return f"{self.BASE_URL}{self.api_prefix}/telegram/webhook/"
    
    @property
    def setwebhook_url(self) -> str:
        return f"{self.api_telegram}/setWebhook?url={self.webhook_url}"
    
    
    
@lru_cache
def get_settings():
    return Settings()