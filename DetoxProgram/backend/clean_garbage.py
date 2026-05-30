import sys
import os
from unittest.mock import MagicMock

sys.modules['celery'] = MagicMock()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal
from models.schemas import NLPResult, NormEvent

def clean_garbage_data():
    db = SessionLocal()
    try:
        print("=== Cleaning garbage data in DB (Supabase/PostgreSQL) ===")
        
        url_events = db.query(NormEvent).filter(
            (NormEvent.title.like("http%")) | (NormEvent.title.like("%youtube.com%")) | (NormEvent.title.like("%watch?v=%"))
        ).all()
        print(f"Found {len(url_events)} NormEvent rows with URL-like titles.")
        for ev in url_events:
            db.delete(ev)
        
        nlp_results = db.query(NLPResult).all()
        garbage_nlp = []
        for nr in nlp_results:
            kws = nr.analysis_data.get("keywords", []) if isinstance(nr.analysis_data, dict) else []
            has_garbage = False
            for word, count in kws:
                if "=" in word or len(word) > 20 or any(c in word for c in ["-", "|", ":", "/", "\\"]):
                    has_garbage = True
                    break
            if has_garbage:
                garbage_nlp.append(nr)
                
        print(f"Found {len(garbage_nlp)} NLPResult rows containing garbage keywords.")
        for nr in garbage_nlp:
            db.delete(nr)
            
        db.commit()
        print("Garbage data successfully deleted from DB.")
    except Exception as e:
        db.rollback()
        print("Error cleaning garbage data:", e)
    finally:
        db.close()

if __name__ == "__main__":
    clean_garbage_data()
