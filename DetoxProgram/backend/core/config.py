import os
from dotenv import load_dotenv

load_dotenv(encoding="utf-8", override=True)

class Settings:
    PROJECT_NAME: str = "언블리버블 v2"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://ttxkknefkcepctezomvh.supabase.co")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "sb_publishable_LBhJq0wk1zRS3EVCLHLpEw_mSgYj_hD")

settings = Settings()

if settings.GOOGLE_APPLICATION_CREDENTIALS:
    if os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
    else:
        # Fallback to local gcp_creds.json in the backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_creds = os.path.join(backend_dir, "gcp_creds.json")
        if os.path.exists(local_creds):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_creds


