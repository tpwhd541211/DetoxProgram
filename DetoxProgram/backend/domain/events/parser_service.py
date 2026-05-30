# -*- coding: utf-8 -*-
import json
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup
import re
import unicodedata

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
    
    # Unicode NFC 정규화 수행 (macOS NFD 자소 분리 대응)
    t_str = unicodedata.normalize('NFC', t_str)
    
    # 정규식 기반 날짜 추출 (예: "2024. 01. 02.", "2024-01-02", "2024/01/02")
    date_match = re.search(r'(\d{4})[-.\s/]+(\d{1,2})[-.\s/]+(\d{1,2})', t_str)
    if not date_match:
        return datetime.now()
    
    year = int(date_match.group(1))
    month = int(date_match.group(2))
    day = int(date_match.group(3))

    # 정규식 기반 시간 추출 (예: "3:04:05" 또는 "3:04" 초 생략 대응)
    time_match = re.search(r'(\d{1,2}):(\d{2})(?::(\d{2}))?', t_str)
    if not time_match:
        return datetime.now()
    
    hour = int(time_match.group(1))
    minute = int(time_match.group(2))
    second = int(time_match.group(3)) if time_match.group(3) else 0

    # 오전/오후 및 AM/PM 대소문자 검출 (로케일 독립 및 소스 코드 인코딩 세이프 유니코드 시퀀스 매칭)
    is_pm = any(x in t_str for x in ["\uc624\ud6c4", "PM", "pm"])
    is_am = any(x in t_str for x in ["\uc624\uc804", "AM", "am"])

    if is_pm and hour < 12:
        hour += 12
    elif is_am and hour == 12:
        hour = 0

    # 타임존 오프셋 직접 파싱 및 대입
    from datetime import timezone, timedelta
    
    # 시간 오프셋 직접 검출 (예: +0900, +09:00, -0500 등)
    tz_match = re.search(r'([+-])(\d{2}):?(\d{2})', t_str)
    if tz_match:
        sign = 1 if tz_match.group(1) == '+' else -1
        h_offset = int(tz_match.group(2))
        m_offset = int(tz_match.group(3))
        tz = timezone(sign * timedelta(hours=h_offset, minutes=m_offset))
    elif "KST" in t_str:
        tz = timezone(timedelta(hours=9))
    else:
        tz = timezone.utc

    try:
        return datetime(year, month, day, hour, minute, second, tzinfo=tz)
    except Exception:
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
                
            if clean_title.startswith("http://") or clean_title.startswith("https://") or "youtube.com" in clean_title or "watch?v=" in clean_title:
                clean_title = ""
                
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
            if title.startswith("http://") or title.startswith("https://") or "youtube.com" in title or "watch?v=" in title:
                title = ""
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
