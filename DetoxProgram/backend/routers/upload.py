from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
import uuid

from services.parser_service import process_and_normalize
from services.session_service import group_into_sessions
from services.youtube_service import enrich_events_with_meta
from services.scoring_service import calculate_detox_score
from services.llm_service import generate_report_and_missions

from core.database import SessionLocal
from models.schemas import RawEvent, NormEvent, NLPResult, ScoreRun, ReportSnapshot
from datetime import datetime

router = APIRouter()

def save_to_db(dataset_id: str, raw_events, normalized_events, sessions, scores, report_data):
    db = SessionLocal()
    try:
        # 1. RawEvent 저장
        raw_events_serializable = []
        for ev in raw_events:
            ev_copy = ev.copy()
            if isinstance(ev_copy.get("watch_time"), datetime):
                ev_copy["watch_time"] = ev_copy["watch_time"].isoformat()
            raw_events_serializable.append(ev_copy)
            
        db_raw = RawEvent(dataset_id=dataset_id, raw_data=raw_events_serializable)
        db.add(db_raw)
        
        # 2. NormEvent 저장
        for ev in normalized_events:
            db_norm = NormEvent(
                dataset_id=dataset_id,
                video_id=ev.get("video_id", ""),
                channel_id=ev.get("channel_id", ""),
                channel_name=ev.get("channel_name", ""),
                title=ev.get("title", ""),
                description=ev.get("description", ""),
                watch_time=ev.get("watch_time"),
                duration_watched=ev.get("duration_watched", 0),
                parse_status=ev.get("parse_status", "success")
            )
            db.add(db_norm)
            
        # 3. NLPResult 저장
        for s in sessions:
            db_nlp = NLPResult(
                dataset_id=dataset_id,
                session_id=s.get("session_id"),
                session_text=s.get("session_text"),
                analysis_data={
                    "keywords": s.get("keywords", []),
                    "category": s.get("category", "❓ 기타/미분류"),
                    "stability_factor": s.get("stability_factor", 1.0),
                    "safety_factor": s.get("safety_factor", 1.0)
                }
            )
            db.add(db_nlp)
            
        # 4. ScoreRun 저장
        db_score = ScoreRun(
            dataset_id=dataset_id,
            diversity=scores.get("diversity", 0.0),
            stability=scores.get("stability", 0.0),
            proactivity=scores.get("proactivity", 0.0),
            openness=scores.get("openness", 0.0),
            manipulation_index=scores.get("manipulation_index", 0.0),
            
            # 6-axis detailed values
            tds=scores.get("tds", 50.0),
            sbs=scores.get("sbs", 50.0),
            ebs=scores.get("ebs", 50.0),
            vos=scores.get("vos", 50.0),
            sms=scores.get("sms", 50.0),
            uas=scores.get("uas", 50.0),
            brs=scores.get("brs", 0.0),
            
            persona_type=scores.get("persona_type", "UNKN")
        )
        db.add(db_score)
        
        # 5. ReportSnapshot 저장
        db_report = ReportSnapshot(
            dataset_id=dataset_id,
            report_data=report_data
        )
        db.add(db_report)
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to save to database for dataset_id {dataset_id}: {e}")
        raise e
    finally:
        db.close()

def background_pipeline(dataset_id: str, file_content: bytes, filename: str):
    """
    백그라운드에서 실행될 전체 데이터 파이프라인 워커
    """
    try:
        # 1. 파싱 및 노이즈(5초 스킵) 필터링
        normalized_events = process_and_normalize(file_content, filename)
        
        # 2. 메타데이터 보강 (YouTube API)
        enriched_events = enrich_events_with_meta(normalized_events)
        
        # 3. 세션 묶음 (30분 / 검색어 기준)
        sessions = group_into_sessions(enriched_events)
        
        # 4. 4차원 점수 연산 및 페르소나 도출
        scores = calculate_detox_score(sessions)
        
        # 5. LLM(Gemini) 코멘트 및 미션 생성
        report_data = generate_report_and_missions(scores)
        
        # 6. DB 저장
        save_to_db(dataset_id, normalized_events, normalized_events, sessions, scores, report_data)
        
        print(f"[{dataset_id}] 파이프라인 처리 완료! 점수: {scores['persona_type']}")
        
    except Exception as e:
        print(f"[{dataset_id}] 파이프라인 에러 발생: {e}")

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """
    유튜브 시청 기록 파일을 업로드받아 분석 파이프라인을 실행하고 결과를 반환합니다.
    """
    try:
        content = await file.read()
        dataset_id = str(uuid.uuid4())
        
        # 실시간 반응성과 정확한 차트 연동을 위해 동기적으로 파이프라인을 수행합니다.
        normalized_events = process_and_normalize(content, file.filename)
        enriched_events = enrich_events_with_meta(normalized_events)
        sessions = group_into_sessions(enriched_events)
        scores = calculate_detox_score(sessions)
        report_data = generate_report_and_missions(scores)
        save_to_db(dataset_id, normalized_events, normalized_events, sessions, scores, report_data)
        
        # 조종 지수를 기반으로 도파민 점수 매핑 (0.0 ~ 1.0)
        dopamine_score = scores.get("manipulation_index", 72.0) / 100.0
        
        return {
            "dataset_id": dataset_id,
            "filename": file.filename, 
            "status": "success",
            "scores": {
                "dopamine_score": dopamine_score
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
