import os
import requests
from core.config import settings

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

def chunk_list(lst, n):
    """리스트를 n개씩 자릅니다."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def fetch_youtube_meta(video_ids):
    """
    YouTube Data API v3를 호출하여 누락된 메타데이터(카테고리, 태그, 설명 등)를 보강합니다.
    API 쿼타를 아끼기 위해 최대 50개씩 일괄(Batch) 요청합니다.
    """
    if not YOUTUBE_API_KEY:
        print("Warning: YOUTUBE_API_KEY가 설정되지 않아 API 호출을 건너뜁니다.")
        return {}
        
    # 중복 제거 및 유효한 ID만 추출
    unique_ids = list(set([vid for vid in video_ids if vid]))
    meta_data = {}
    
    for batch in chunk_list(unique_ids, 50):
        ids_str = ",".join(batch)
        url = f"{YOUTUBE_API_BASE}/videos?part=snippet,topicDetails&id={ids_str}&key={YOUTUBE_API_KEY}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("items", []):
                    vid = item["id"]
                    snippet = item.get("snippet", {})
                    topic_details = item.get("topicDetails", {})
                    
                    meta_data[vid] = {
                        "description": snippet.get("description", ""),
                        "tags": snippet.get("tags", []),
                        "categoryId": snippet.get("categoryId", ""),
                        "topicCategories": topic_details.get("topicCategories", [])
                    }
            else:
                print(f"YouTube API Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"YouTube API Request failed: {e}")
            
    return meta_data

def enrich_events_with_meta(events):
    """
    파싱된 이벤트 배열을 받아 YouTube 메타데이터를 채워넣습니다.
    """
    video_ids = [ev.get("video_id") for ev in events if ev.get("event_type") == "watch"]
    meta_dict = fetch_youtube_meta(video_ids)
    
    for ev in events:
        vid = ev.get("video_id")
        if vid and vid in meta_dict:
            ev["description"] = meta_dict[vid]["description"]
            ev["tags"] = meta_dict[vid]["tags"]
            ev["categoryId"] = meta_dict[vid]["categoryId"]
            ev["topicCategories"] = meta_dict[vid]["topicCategories"]
            
    return events
