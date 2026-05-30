import asyncio
import os
import sys
from unittest.mock import MagicMock
from fastapi import UploadFile
from fastapi.testclient import TestClient
import uuid

# 1. Mock celery module so the import doesn't fail if celery is missing
if 'celery' not in sys.modules:
    sys.modules['celery'] = MagicMock()

# Define temp database file path
DB_FILE = "./test_temp.db"
DB_URL = f"sqlite:///{DB_FILE}"

# Pre-clean any leftover database file
if os.path.exists(DB_FILE):
    try:
        os.remove(DB_FILE)
    except Exception:
        pass

# 2. Mock core.config BEFORE importing main to use a file-based SQLite database
class MockSettings:
    PROJECT_NAME = "언블리버블 v2 Test"
    DATABASE_URL = DB_URL
    GEMINI_API_KEY = "dummy"
    GOOGLE_APPLICATION_CREDENTIALS = ""
    SUPABASE_URL = "https://example.supabase.co"
    SUPABASE_ANON_KEY = "dummy"

mock_config = MagicMock()
mock_config.settings = MockSettings()
sys.modules['core.config'] = mock_config

# 3. Now safe to import main and core.security
from main import app  # Imports cleanly and creates schema on the SQLite DB
from core.security import get_current_user
from core.database import engine

# 4. Override FastAPI dependency to bypass live Supabase token check
app.dependency_overrides[get_current_user] = lambda: "test-user-id"

client = TestClient(app)

def test_upload():
    try:
        # Create a dummy JSON file content
        content = b"[]"
        files = {"file": ("test.json", content, "application/json")}
        
        # Send request
        response = client.post(
            "/api/upload/",
            files=files,
            headers={"Authorization": "Bearer dummy"}
        )
        print("Response status:", response.status_code)
        print("Response json:", response.json())
        
        # Assertions to ensure it behaves correctly
        assert response.status_code == 200
        res_json = response.json()
        assert "dataset_id" in res_json
        assert res_json["status"] == "queued"
        print("SUCCESS: test_upload passed successfully!")
    finally:
        # Dispose the engine to release file locks on test_temp.db
        engine.dispose()
        # Clean up database file
        if os.path.exists(DB_FILE):
            try:
                os.remove(DB_FILE)
            except Exception as e:
                print(f"Failed to clean up {DB_FILE}: {e}")

if __name__ == "__main__":
    test_upload()
