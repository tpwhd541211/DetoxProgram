from core.database import engine, Base
# 이 임포트가 있어야 Base가 자식 테이블(스키마)을 인식합니다.
from models.schemas import (
    RawEvent, NormEvent, NLPResult, ScoreRun, ReportSnapshot,
    Profiles, ConsentLog, RawFile, 
    AuditLog, AnalysisJob, MissionLog, UserStreak, UserSession
)

def init_db():
    print("데이터베이스 테이블 생성을 시작합니다...")
    # 등록된 모든 스키마를 바탕으로 DB에 테이블을 생성합니다.
    Base.metadata.create_all(bind=engine)
    print("테이블 생성 완료!")

if __name__ == "__main__":
    init_db()
