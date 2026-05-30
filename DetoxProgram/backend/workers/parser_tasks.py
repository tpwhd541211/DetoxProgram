import traceback
from core.celery_app import celery_app
from core.database import SessionLocal
from models.schemas import AnalysisJob

from domain.events.parser_service import process_and_normalize
from domain.sessions.session_service import group_into_sessions
from infrastructure.youtube_service import enrich_events_with_meta
from domain.analysis.scoring_service import calculate_detox_score
from infrastructure.llm_service import generate_report_and_missions
# Upload functions mapped to avoid cyclic imports
from api.v1.upload import save_to_db, update_job_status

@celery_app.task(bind=True, max_retries=3)
def process_watch_history_task(self, dataset_id: str, file_content: bytes, filename: str, user_id: str):
    """
    Celery background worker task to process watch history file
    """
    try:
        # 1. Parsing & Validation
        update_job_status(dataset_id, "processing", "parsing")
        normalized_events = process_and_normalize(file_content, filename)
        
        if len(normalized_events) < 10:
            update_job_status(dataset_id, "failed", "P01_DATA_SHORT")
            return {"status": "failed", "reason": "Data too short"}
            
        # 2. Metadata Enrichment
        update_job_status(dataset_id, "processing", "enriching")
        enriched_events = enrich_events_with_meta(normalized_events)
        
        # 3. Session Grouping
        update_job_status(dataset_id, "processing", "scoring")
        sessions = group_into_sessions(enriched_events)
        
        # 4. Score Computation
        db = SessionLocal()
        try:
            scores = calculate_detox_score(sessions, db)
        finally:
            db.close()
        
        # 5. LLM Report Generation
        update_job_status(dataset_id, "processing", "report")
        report_data = generate_report_and_missions(scores)
        
        # 6. Save results to DB
        update_job_status(dataset_id, "processing", "saving")
        save_to_db(dataset_id, user_id, normalized_events, enriched_events, sessions, scores, report_data)
        
        # Done
        update_job_status(dataset_id, "completed", "completed")
        return {"status": "success", "dataset_id": dataset_id}
        
    except Exception as exc:
        traceback.print_exc()
        update_job_status(dataset_id, "failed", "error")
        # Retry logic for transient failures could go here
        raise self.retry(exc=exc, countdown=10)
