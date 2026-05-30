import os
from dotenv import load_dotenv

load_dotenv(encoding="utf-8", override=True)

class Settings:
    PROJECT_NAME: str = "언블리버블 v2"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://ttxkknefkcepctezomvh.supabase.co")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "sb_publishable_AyCa01GmVrxFW2QJUMkPMQ_g2ZL7Lfo")

settings = Settings()

if settings.GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS

