from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, dashboard, detox
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 개발 환경에서는 모두 허용, 운영 시 수정 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(upload.router, prefix="/api/upload", tags=["Upload & Processing"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(detox.router, prefix="/api/detox", tags=["Detox Mission"])

