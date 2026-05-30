import sys
import os
from unittest.mock import MagicMock

# Mock celery module to avoid ModuleNotFoundError
sys.modules['celery'] = MagicMock()

# Ensure the backend directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal
from models.schemas import NLPResult

def check_old():
    db = SessionLocal()
    try:
        old_dataset_id = "c58ca782-facc-4de4-9ec6-9794fa68d730"
        print(f"=== Checking old dataset: {old_dataset_id} ===")
        
        nlp_results = db.query(NLPResult).filter(NLPResult.dataset_id == old_dataset_id).all()
        print(f"Found {len(nlp_results)} NLPResult rows for this old dataset.")
        
        for nr in nlp_results:
            kws = nr.analysis_data.get("keywords", []) if isinstance(nr.analysis_data, dict) else []
            for word, count in kws:
                if "v=" in word or "gZetUU" in word:
                    print(f"  🚨 Found Garbage Word in old dataset: '{word}' (NLPResult ID: {nr.id})")
                    
    except Exception as e:
        print("Error checking old dataset:", e)
    finally:
        db.close()

if __name__ == "__main__":
    check_old()
