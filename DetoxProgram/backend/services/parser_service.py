import json
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup
import re

def validate_uploaded_file(file_content: bytes, filename: str):
    """
    업로드된 파일의 확장자, 필수 컬럼 등을 검증합니다.
    """
    if not (filename.endswith(".json") or filename.endswith(".html")):
        raise ValueError("JSON 또는 HTML 형식의 시청 기록 파일만 지원합니다.")
    return True

def parse_takeout_time(t_str: str) -> datetime:
    t_str = t_str.strip()
    # ISO 형식 먼저 파싱 시도 (JSON 용)
    try:
        return datetime.fromisoformat(t_str.replace("Z", "+00:00"))
    except ValueError:
        pass
    
    # HTML 형식 타임스탬프 전처리
    tz = "+0000"
    if "KST" in t_str:
        tz = "+0900"
        t_str = t_str.replace("KST", "").strip()
    elif "UTC" in t_str:
        tz = "+0000"
        t_str = t_str.replace("UTC", "").strip()
        
    if "오후" in t_str:
        t_str = t_str.replace("오후", "").strip()
        if "PM" not in t_str:
            t_str = t_str + " PM"
    elif "오전" in t_str:
        t_str = t_str.replace("오전", "").strip()
        if "AM" not in t_str:
            t_str = t_str + " AM"

    # AM/PM 위치 정규화 (예: "PM 2:21:20" -> "2:21:20 PM")
    t_str = re.sub(r'\b(AM|PM)\b\s*(\d{1,2}:\d{2}:\d{2})', r'\2 \1', t_str)
    
    try:
        import dateutil.parser
        return dateutil.parser.parse(t_str + " " + tz)
    except Exception:
        try:
            t_str_clean = re.sub(r'\s+', ' ', t_str)
            return datetime.strptime(t_str_clean + " " + tz, "%Y. %m. %d. %I:%M:%S %p %z")
        except Exception:
            pass
    return datetime.now()

def extract_raw_data_json(file_content: bytes):
    """
    구글 테이크아웃의 시청 기록(JSON)에서 데이터를 추출합니다.
    """
    data = json.loads(file_content)
    events = []
    
    for item in data:
        title = item.get("title", "")
        
        event_type = "unknown"
        query_text = ""
        video_id = ""
        clean_title = ""
        
        is_watch = title.startswith("Watched ") or "을(를) 시청했습니다." in title
        is_search = title.startswith("Searched for ") or "을(를) 검색했습니다." in title
        
        if is_watch:
            event_type = "watch"
            video_url = item.get("titleUrl", "")
            if "watch?v=" in video_url:
                parsed_url = urllib.parse.urlparse(video_url)
                video_id = urllib.parse.parse_qs(parsed_url.query).get("v", [None])[0]
            
            if title.startswith("Watched "):
                clean_title = title.replace("Watched ", "", 1)
            elif "을(를) 시청했습니다." in title:
                clean_title = title.split(" 을(를) 시청했습니다.")[0].strip()
                
        elif is_search:
            event_type = "search"
            if title.startswith("Searched for "):
                query_text = title.replace("Searched for ", "").strip()
            elif "을(를) 검색했습니다." in title:
                query_text = title.split(" 을(를) 검색했습니다.")[0].strip()
        else:
            continue
            
        subtitles = item.get("subtitles", [])
        channel_name = subtitles[0].get("name", "") if subtitles else ""
        channel_url = subtitles[0].get("url", "") if subtitles else ""
        channel_id = channel_url.split("/")[-1] if channel_url else ""
        
        time_str = item.get("time", "")
        watch_time = parse_takeout_time(time_str)
            
        events.append({
            "event_type": event_type,
            "video_id": video_id,
            "query_text": query_text,
            "title": clean_title,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "watch_time": watch_time,
            "description": "", 
        })
        
    return events

def extract_raw_data_html(file_content: bytes):
    """
    구글 테이크아웃의 시청 기록(HTML)에서 데이터를 추출합니다.
    """
    events = []
    # HTML 파싱
    soup = BeautifulSoup(file_content, "lxml")
    # 'content-cell' 클래스가 포함된 모든 div 탐색
    cells = soup.find_all("div", class_=lambda c: c and "content-cell" in c)
    
    for cell in cells:
        text_content = cell.get_text(separator=" ", strip=True)
        links = cell.find_all("a")
        
        event_type = "unknown"
        video_id = ""
        query_text = ""
        title = ""
        channel_name = ""
        channel_id = ""
        watch_time = None
        
        is_watch = (text_content.startswith("Watched ") or "을(를) 시청했습니다." in text_content) and len(links) >= 1
        is_search = (text_content.startswith("Searched for ") or "을(를) 검색했습니다." in text_content) and len(links) >= 1
        
        if is_watch:
            event_type = "watch"
            title_node = links[0]
            title = title_node.text.strip()
            video_url = title_node.get("href", "")
            if "watch?v=" in video_url:
                parsed_url = urllib.parse.urlparse(video_url)
                video_id = urllib.parse.parse_qs(parsed_url.query).get("v", [None])[0]
            
            if len(links) >= 2:
                channel_node = links[1]
                channel_name = channel_node.text.strip()
                channel_url = channel_node.get("href", "")
                channel_id = channel_url.split("/")[-1] if channel_url else ""
                
        elif is_search:
            event_type = "search"
            query_node = links[0]
            query_text = query_node.text.strip()
        else:
            continue
            
        try:
            time_text = list(cell.stripped_strings)[-1]
            watch_time = parse_takeout_time(time_text)
        except Exception:
            watch_time = datetime.now()
            
        events.append({
            "event_type": event_type,
            "video_id": video_id,
            "query_text": query_text,
            "title": title,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "watch_time": watch_time,
            "description": "", 
        })
        
    return events

def extract_raw_data(file_content: bytes, filename: str):
    """
    파일 확장자에 따라 JSON 또는 HTML 파서를 호출합니다.
    """
    if filename.endswith(".json"):
        events = extract_raw_data_json(file_content)
    elif filename.endswith(".html"):
        events = extract_raw_data_html(file_content)
    else:
        events = []
        
    events.sort(key=lambda x: x["watch_time"])
    return events

def filter_fake_dopamine(events):
    """
    시청 시간이 5초 이하인 스킵 영상 등 가짜 도파민(노이즈 데이터)을 걸러냅니다.
    """
    filtered_events = []
    
    for i in range(len(events)):
        current_event = events[i]
        
        if i == len(events) - 1:
            current_event["duration_watched"] = 60
            current_event["parse_status"] = "success"
            filtered_events.append(current_event)
            continue
            
        next_event = events[i + 1]
        time_diff = (next_event["watch_time"] - current_event["watch_time"]).total_seconds()
        current_event["duration_watched"] = int(time_diff)
        
        if time_diff <= 5:
            current_event["parse_status"] = "reject"
        else:
            current_event["parse_status"] = "success"
            
        filtered_events.append(current_event)
        
    return filtered_events

def process_and_normalize(file_content: bytes, filename: str):
    """
    위 함수들을 조합하여 최종적으로 DB에 적재할 정제된 데이터 배열을 반환합니다.
    """
    validate_uploaded_file(file_content, filename)
    raw_events = extract_raw_data(file_content, filename)
    normalized_events = filter_fake_dopamine(raw_events)
    
    return normalized_events
