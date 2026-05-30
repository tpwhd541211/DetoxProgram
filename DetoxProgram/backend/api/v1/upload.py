from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
import uuid
from datetime import datetime

from domain.events.parser_service import process_and_normalize
from domain.sessions.session_service import group_into_sessions
from infrastructure.youtube_service import enrich_events_with_meta
from domain.analysis.scoring_service import calculate_detox_score
from infrastructure.llm_service import generate_report_and_missions

from core.database import SessionLocal
from models.schemas import RawEvent, NormEvent, NLPResult, ScoreRun, ReportSnapshot, AnalysisJob, UserSession
from core.security import get_current_user

router = APIRouter()

def save_to_db(dataset_id: str, user_id: str, raw_events, normalized_events, sessions, scores, report_data):
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
                    "safety_factor": s.get("safety_factor", 1.0),
                    "gcp_nlp_raw": s.get("gcp_nlp_raw"),
                    "youtube_tags": s.get("youtube_tags", []),
                    "youtube_categories": s.get("youtube_categories", []),
                    "category_confidence": s.get("category_confidence", 0.0),
                    "category_source": s.get("category_source", "fallback_failed"),
                    "category_candidates": s.get("category_candidates", []),
                    "is_uncategorized": s.get("is_uncategorized", True),
                    "fallback_reason": s.get("fallback_reason", "no_metadata_or_keyword_match"),
                    "category_version": s.get("category_version", "2.0")
                }
            )
            db.add(db_nlp)
            
        # 3.5 UserSession 저장
        for s in sessions:
            db_session = UserSession(
                id=s.get("session_id"),
                user_id=user_id,
                dataset_id=dataset_id,
                session_start=s.get("start_time"),
                session_end=s.get("end_time"),
                total_events=s.get("total_events", 0),
                is_binge=s.get("is_binge", False),
                session_type=s.get("session_type", "normal")
            )
            db.add(db_session)
            
        # 4. ScoreRun 저장
        db_score = ScoreRun(
            dataset_id=dataset_id,
            user_id=user_id,
            diversity=scores.get("diversity", 0.0),
            stability=scores.get("stability", 0.0),
            proactivity=scores.get("proactivity", 0.0),
            openness=scores.get("openness", 0.0),
            manipulation_index=scores.get("manipulation_index", 0.0),
            
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
            user_id=user_id,
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

def update_job_status(dataset_id: str, status: str, stage: str):
    db = SessionLocal()
    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.dataset_id == dataset_id).first()
        if job:
            job.status = status
            job.current_stage = stage
            db.commit()
    except Exception as e:
        print(f"Failed to update job status: {e}")
    finally:
        db.close()

@router.post("/")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """
    Uploads a watch history file, initializes a background job using Celery, and returns the job reference immediately.
    """
    try:
        content = await file.read()
        dataset_id = str(uuid.uuid4())
        
        db = SessionLocal()
        try:
            job = AnalysisJob(
                analysis_id=dataset_id,
                dataset_id=dataset_id,
                status="queued",
                current_stage="queued",
                user_id=current_user
            )
            db.add(job)
            db.commit()
        except Exception as je:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to initialize analysis job: {je}")
        finally:
            db.close()
            
        from workers.parser_tasks import process_watch_history_task
        
        # Use FastAPI BackgroundTasks to process asynchronously since Celery might not be available
        background_tasks.add_task(process_watch_history_task, None, dataset_id, content, file.filename, current_user)
        
        return {
            "dataset_id": dataset_id,
            "filename": file.filename,
            "status": "queued"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{dataset_id}")
async def get_job_status(
    dataset_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Secure endpoint to retrieve the status of an active or completed background analysis job.
    """
    db = SessionLocal()
    try:
        job = db.query(AnalysisJob).filter(
            AnalysisJob.dataset_id == dataset_id,
            AnalysisJob.user_id == current_user
        ).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Analysis job not found")
            
        return {
            "dataset_id": job.dataset_id,
            "status": job.status,
            "current_stage": job.current_stage
        }
    finally:
        db.close()
