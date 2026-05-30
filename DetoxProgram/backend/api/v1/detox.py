from fastapi import APIRouter, HTTPException, Depends
from core.database import SessionLocal
from models.schemas import ScoreRun, ReportSnapshot
from core.security import get_current_user

router = APIRouter()

@router.get("/missions/{dataset_id}")
async def get_detox_missions(dataset_id: str, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        score = db.query(ScoreRun).filter(
            ScoreRun.dataset_id == dataset_id,
            ScoreRun.user_id == current_user
        ).first()
        if not score:
            raise HTTPException(status_code=404, detail="Dataset not found or access denied")
            
        report = db.query(ReportSnapshot).filter(
            ReportSnapshot.dataset_id == dataset_id,
            ReportSnapshot.user_id == current_user
        ).first()
        
        missions = report.report_data.get("missions", []) if report and isinstance(report.report_data, dict) else []
        return {"dataset_id": dataset_id, "missions": missions}
    finally:
        db.close()
