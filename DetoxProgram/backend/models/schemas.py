from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean
from core.database import Base
from datetime import datetime

class RawEvent(Base):
    __tablename__ = "raw_event"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String, index=True)
    raw_data = Column(JSON) # 전체 원본 JSON
    created_at = Column(DateTime, default=datetime.utcnow)

class NormEvent(Base):
    __tablename__ = "norm_event"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String, index=True)
    video_id = Column(String, index=True)
    channel_id = Column(String)
    channel_name = Column(String)
    title = Column(String)
    description = Column(String)
    watch_time = Column(DateTime)
    duration_watched = Column(Integer) # 초 단위 시청 시간
    parse_status = Column(String) # 'success', 'reject' (fake dopamine)
    created_at = Column(DateTime, default=datetime.utcnow)

class NLPResult(Base):
    __tablename__ = "nlp_result"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String, index=True)
    session_id = Column(String, index=True)
    session_text = Column(String)
    analysis_data = Column(JSON) # JSONB 대체
    created_at = Column(DateTime, default=datetime.utcnow)

class ScoreRun(Base):
    __tablename__ = "score_run"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String, unique=True, index=True)
    # Original 4-axis values for backward compatibility
    diversity = Column(Float)
    stability = Column(Float)
    proactivity = Column(Float)
    openness = Column(Float)
    manipulation_index = Column(Float)
    
    # 6-axis detailed values from UDF specification
    tds = Column(Float, default=0.0) # 주제 다양성 점수
    sbs = Column(Float, default=0.0) # 출처 균형 점수
    ebs = Column(Float, default=0.0) # 감정 균형 점수
    vos = Column(Float, default=0.0) # 관점 개방성 점수
    sms = Column(Float, default=0.0) # 유해/자극 안전 점수
    uas = Column(Float, default=0.0) # 사용자 주도성 점수
    brs = Column(Float, default=0.0) # 종합 편향 위험도 (Bias Risk Score)
    
    persona_type = Column(String) # ex: INTP
    created_at = Column(DateTime, default=datetime.utcnow)

class ReportSnapshot(Base):
    __tablename__ = "report_snapshot"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String, unique=True, index=True)
    report_data = Column(JSON) # LLM이 생성한 리포트 (코멘트, 미션 등)
    created_at = Column(DateTime, default=datetime.utcnow)
