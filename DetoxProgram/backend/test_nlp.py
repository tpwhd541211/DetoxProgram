import sys
import os
import json
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from infrastructure.youtube_service import fetch_youtube_meta
from domain.analysis.nlp_service import analyze_text_with_gcp

print("Testing YouTube API...")
meta = fetch_youtube_meta(["dQw4w9WgXcQ"])
with open("test_out.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print("YouTube Meta written to test_out.json")

print("\nTesting GCP NLP API...")
text = "이것은 테스트 문장입니다. 인공지능과 머신러닝에 대해 이야기해 봅시다."
res = analyze_text_with_gcp(text)
with open("test_out2.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)
print("GCP NLP Result written to test_out2.json")
