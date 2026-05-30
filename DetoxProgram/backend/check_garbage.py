import sys
import os
from unittest.mock import MagicMock

# Mock celery module to avoid ModuleNotFoundError
sys.modules['celery'] = MagicMock()

# Ensure the backend directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal
from models.schemas import NLPResult, NormEvent, AnalysisJob

def check_garbage_data():
    db = SessionLocal()
    try:
        print("=== Checking for garbage data in DB (Supabase/PostgreSQL) ===")
        
        # 1. Check NormEvent for URL titles
        print("\n1. Checking NormEvent titles for URL-like text...")
        url_events = db.query(NormEvent).filter(
            (NormEvent.title.like("http%")) | (NormEvent.title.like("%youtube.com%")) | (NormEvent.title.like("%watch?v=%"))
        ).all()
        print(f"Found {len(url_events)} NormEvent rows with URL-like titles.")
        for ev in url_events[:10]:
            print(f"  ID: {ev.id} | Dataset: {ev.dataset_id} | Title: {ev.title} | Channel: {ev.channel_name}")
            
        # 2. Check NLPResult for garbage keywords (like 'v=...')
        # Since analysis_data is stored as JSON, we'll fetch some recent rows and inspect them in python.
        print("\n2. Checking NLPResult for garbage keywords...")
        nlp_results = db.query(NLPResult).order_by(NLPResult.created_at.desc()).limit(100).all()
        
        garbage_nlp_count = 0
        example_garbage_nlp = []
        for nr in nlp_results:
            kws = nr.analysis_data.get("keywords", []) if isinstance(nr.analysis_data, dict) else []
            has_garbage = False
            garbage_list = []
            for word, count in kws:
                # Check if word contains '=' or has 11-digit video ID format
                if "=" in word or len(word) > 20 or any(c in word for c in ["-", "|", ":", "/", "\\"]):
                    has_garbage = True
                    garbage_list.append(word)
            if has_garbage:
                garbage_nlp_count += 1
                if len(example_garbage_nlp) < 5:
                    example_garbage_nlp.append((nr.id, nr.dataset_id, garbage_list))
                    
        print(f"Inspected latest 100 NLPResult rows. Found {garbage_nlp_count} rows containing garbage keywords.")
        for nid, did, gw in example_garbage_nlp:
            print(f"  NLPResult ID: {nid} | Dataset: {did} | Garbage Keywords: {gw}")
            
    except Exception as e:
        print("Error checking garbage data:", e)
    finally:
        db.close()

if __name__ == "__main__":
    check_garbage_data()
