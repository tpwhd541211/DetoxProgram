# -*- coding: utf-8 -*-
import sys
import os
import traceback
import json
from datetime import datetime

# Fix stdout encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

# Celery mock
from unittest.mock import MagicMock
sys.modules['celery'] = MagicMock()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv(encoding="utf-8", override=True)

from domain.events.parser_service import process_and_normalize
from domain.sessions.session_service import group_into_sessions
from infrastructure.youtube_service import enrich_events_with_meta
from domain.analysis.nlp_service import analyze_session_text

def run_whitebox_test():
    filepath = r"C:\Users\Administrator\Desktop\UnbelievableTeamProject\others\시청 기록.html"
    print(f"Loading file: {filepath}", flush=True)
    with open(filepath, "rb") as f:
        file_content = f.read()

    print("\n--- 1. Parsing & Normalizing ---", flush=True)
    normalized_events = process_and_normalize(file_content, "시청 기록.html")
    print(f"Total parsed events: {len(normalized_events)}", flush=True)
    
    print("\n--- 2. Metadata Enrichment (YouTube API) ---", flush=True)
    # limit to 50 events for quick testing
    test_events = normalized_events[:50]
    enriched_events = enrich_events_with_meta(test_events)
    print(f"Enriched {len(enriched_events)} events.", flush=True)

    print("\n--- 3. Session Grouping ---", flush=True)
    sessions = group_into_sessions(enriched_events)
    print(f"Total sessions generated: {len(sessions)}", flush=True)
    
    print("\n--- 4. GCP NLP API Test ---", flush=True)
    for s in sessions:
        if s.get("session_text", "").strip():
            print(f"Testing session text: {s['session_text'][:100]}...", flush=True)
            keywords, category, stability_factor, safety_factor, gcp_res = analyze_session_text(s["session_text"])
            print(f"Category: {category}", flush=True)
            print(f"Keywords: {keywords}", flush=True)
            print(f"YouTube Tags included: {s.get('youtube_tags', [])[:5]}", flush=True)
            print(f"GCP Result Used: {gcp_res is not None}", flush=True)
            break
            
    print("\n✅ Whitebox test completed successfully!", flush=True)

if __name__ == "__main__":
    run_whitebox_test()
