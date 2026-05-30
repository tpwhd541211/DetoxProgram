from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import upload, dashboard, detox, settings
from core.database import engine
from models.schemas import Base

# DB 테이블 초기 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="언블리버블 v2 Backend API",
    description="유튜브 시청 기록 기반 디톡스 프로그램 분석 서버",
    version="2.0.0"
)

# CORS 설정 (프론트엔드 통신 허용)
import os
origins_env = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(upload.router, prefix="/api/upload", tags=["Upload & Processing"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(detox.router, prefix="/api/detox", tags=["Detox Mission"])
app.include_router(settings.router, prefix="/api", tags=["Settings"])

