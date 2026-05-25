import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "언블리버블 v2"
    # 실제 프로덕션에서는 PostgreSQL을 사용하지만, 
    # 초기 개발 단계에서는 SQLite 또는 임시 연결을 사용할 수 있습니다.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

settings = Settings()
