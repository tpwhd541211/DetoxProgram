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
    is_short = Column(Boolean, default=False)
    is_autoplay = Column(Boolean, default=False)
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

class UserSession(Base):
    __tablename__ = "user_session"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    dataset_id = Column(String, index=True)
    session_start = Column(DateTime)
    session_end = Column(DateTime)
    total_events = Column(Integer, default=0)
    is_binge = Column(Boolean, default=False)
    session_type = Column(String) # ex: 'late_night', 'normal'
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
    user_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReportSnapshot(Base):
    __tablename__ = "report_snapshot"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String, unique=True, index=True)
    report_data = Column(JSON) # LLM이 생성한 리포트 (코멘트, 미션 등)
    user_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# 추가된 UDF DBMS 설계 테이블들
class Profiles(Base):
    __tablename__ = "profiles"
    id = Column(String, primary_key=True, index=True)
    email = Column(String)
    display_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConsentLog(Base):
    __tablename__ = "consent_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    consent_version = Column(String)
    agreed_at = Column(DateTime, default=datetime.utcnow)

class RawFile(Base):
    __tablename__ = "raw_file"
    dataset_id = Column(String, primary_key=True, index=True)
    file_name = Column(String)
    platform = Column(String)
    hash = Column(String)
    storage_path = Column(String)
    user_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String)
    target_id = Column(String)
    status_code = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalysisJob(Base):
    __tablename__ = "analysis_job"
    analysis_id = Column(String, primary_key=True, index=True)
    dataset_id = Column(String)
    status = Column(String)
    current_stage = Column(String)
    retry_count = Column(Integer, default=0)
    user_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class MissionLog(Base):
    __tablename__ = "mission_log"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String, index=True)
    mission_id = Column(String)
    completed_yn = Column(Boolean, default=False)
    completed_at = Column(DateTime)

class UserStreak(Base):
    __tablename__ = "user_streak"
    user_id = Column(String, primary_key=True, index=True)
    current_streak = Column(Integer, default=0)
    last_completed_date = Column(DateTime)
