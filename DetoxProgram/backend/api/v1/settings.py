from fastapi import APIRouter, HTTPException, Depends, status
from core.database import SessionLocal
from models.schemas import ScoreRun, ReportSnapshot, NLPResult, NormEvent, RawEvent, AnalysisJob, RawFile, ConsentLog, AuditLog, MissionLog, UserSession, UserStreak
from core.security import get_current_user

router = APIRouter()

@router.delete("/datasets/{dataset_id}")
async def delete_user_dataset(
    dataset_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Deletes all data (raw events, normalized events, NLP results, scores, reports)
    associated with the dataset_id, verifying that the dataset belongs to the current user.
    Logs the action to the AuditLog.
    """
    db = SessionLocal()
    try:
        # Verify ownership via ScoreRun or AnalysisJob
        score = db.query(ScoreRun).filter(
            ScoreRun.dataset_id == dataset_id,
            ScoreRun.user_id == current_user
        ).first()
        
        job = db.query(AnalysisJob).filter(
            AnalysisJob.dataset_id == dataset_id,
            AnalysisJob.user_id == current_user
        ).first()
        
        if not score and not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found or access denied"
            )
            
        # Delete related tables
        db.query(RawEvent).filter(RawEvent.dataset_id == dataset_id).delete(synchronize_session=False)
        db.query(NormEvent).filter(NormEvent.dataset_id == dataset_id).delete(synchronize_session=False)
        db.query(NLPResult).filter(NLPResult.dataset_id == dataset_id).delete(synchronize_session=False)
        db.query(ScoreRun).filter(ScoreRun.dataset_id == dataset_id).delete(synchronize_session=False)
        db.query(ReportSnapshot).filter(ReportSnapshot.dataset_id == dataset_id).delete(synchronize_session=False)
        db.query(AnalysisJob).filter(AnalysisJob.dataset_id == dataset_id).delete(synchronize_session=False)
        db.query(RawFile).filter(RawFile.dataset_id == dataset_id).delete(synchronize_session=False)
        db.query(UserSession).filter(UserSession.dataset_id == dataset_id).delete(synchronize_session=False)
        db.query(UserStreak).filter(UserStreak.user_id == current_user).delete(synchronize_session=False)
        db.query(MissionLog).filter(MissionLog.plan_id == current_user).delete(synchronize_session=False)
        
        # Also clean up ConsentLog for the user as part of full deletion/withdrawal
        db.query(ConsentLog).filter(ConsentLog.user_id == current_user).delete(synchronize_session=False)
        
        # Create AuditLog entry
        audit = AuditLog(
            event_type="DATA_DELETION",
            target_id=dataset_id,
            status_code=200
        )
        db.add(audit)
        
        db.commit()
        return {"status": "success", "message": f"Dataset {dataset_id} successfully deleted."}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete dataset: {str(e)}"
        )
    finally:
        db.close()


@router.post("/consent")
async def log_consent(
    current_user: str = Depends(get_current_user)
):
    """
    Records that the current user has agreed to the privacy policy/consent form.
    """
    db = SessionLocal()
    try:
        existing = db.query(ConsentLog).filter(ConsentLog.user_id == current_user).first()
        if not existing:
            consent = ConsentLog(
                user_id=current_user,
                consent_version="v2.0"
            )
            db.add(consent)
            db.commit()
        return {"status": "success", "message": "Consent logged successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save consent log: {str(e)}"
        )
    finally:
        db.close()


@router.get("/consent")
async def check_consent(
    current_user: str = Depends(get_current_user)
):
    """
    Checks if the current user has already signed the consent form.
    """
    db = SessionLocal()
    try:
        consent = db.query(ConsentLog).filter(ConsentLog.user_id == current_user).first()
        return {"consented": consent is not None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query consent: {str(e)}"
        )
    finally:
        db.close()


@router.delete("/reset")
async def reset_user_data(
    current_user: str = Depends(get_current_user)
):
    """
    Deletes all datasets, events, scores, reports, consent logs, and job history
    for the current user, while preserving the user account itself.
    """
    db = SessionLocal()
    try:
        # Find all dataset_ids for this user
        runs = db.query(ScoreRun).filter(ScoreRun.user_id == current_user).all()
        dataset_ids = [run.dataset_id for run in runs]
        
        jobs = db.query(AnalysisJob).filter(AnalysisJob.user_id == current_user).all()
        for j in jobs:
            if j.dataset_id not in dataset_ids:
                dataset_ids.append(j.dataset_id)
                
        files = db.query(RawFile).filter(RawFile.user_id == current_user).all()
        for f in files:
            if f.dataset_id not in dataset_ids:
                dataset_ids.append(f.dataset_id)

        # Delete from dependent tables using dataset_ids
        if dataset_ids:
            db.query(RawEvent).filter(RawEvent.dataset_id.in_(dataset_ids)).delete(synchronize_session=False)
            db.query(NormEvent).filter(NormEvent.dataset_id.in_(dataset_ids)).delete(synchronize_session=False)
            db.query(NLPResult).filter(NLPResult.dataset_id.in_(dataset_ids)).delete(synchronize_session=False)
            db.query(ScoreRun).filter(ScoreRun.dataset_id.in_(dataset_ids)).delete(synchronize_session=False)
            db.query(ReportSnapshot).filter(ReportSnapshot.dataset_id.in_(dataset_ids)).delete(synchronize_session=False)
            db.query(AnalysisJob).filter(AnalysisJob.dataset_id.in_(dataset_ids)).delete(synchronize_session=False)
            db.query(RawFile).filter(RawFile.dataset_id.in_(dataset_ids)).delete(synchronize_session=False)
            db.query(UserSession).filter(UserSession.dataset_id.in_(dataset_ids)).delete(synchronize_session=False)

        # Delete user-scoped tables
        db.query(MissionLog).filter(MissionLog.plan_id == current_user).delete(synchronize_session=False)
        db.query(UserStreak).filter(UserStreak.user_id == current_user).delete(synchronize_session=False)
            
        # Clean up consent logs
        db.query(ConsentLog).filter(ConsentLog.user_id == current_user).delete(synchronize_session=False)
        
        audit = AuditLog(
            event_type="DATA_RESET",
            target_id=current_user,
            status_code=200
        )
        db.add(audit)
        
        db.commit()
        return {"status": "success", "message": "All user data successfully reset. User account is preserved."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset user data: {str(e)}"
        )
    finally:
        db.close()


