from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()