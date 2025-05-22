# backend/app/config.py
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    COLAB_URL: str = os.getenv("COLAB_URL")
    MODEL_TIMEOUT: int = 30


settings = Settings()
