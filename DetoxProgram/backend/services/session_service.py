from datetime import timedelta
import uuid

def group_into_sessions(normalized_events):
    """
    정제된 이벤트를 30분 단위 및 검색어 변경 기준으로 묶어 세션을 생성합니다.
    """
    sessions = []
    if not normalized_events:
        return sessions
        
    current_session = {
        "session_id": str(uuid.uuid4()),
        "events": [],
        "query_text": "",
        "start_time": normalized_events[0]["watch_time"],
        "end_time": normalized_events[0]["watch_time"],
        "session_text": ""
    }
    
    for event in normalized_events:
        # 가짜 도파민(스킵) 처리된 항목은 세션 텍스트에서 제외하거나 세션 묶음에서 제외
        if event.get("parse_status") == "reject":
            continue
            
        time_diff = event["watch_time"] - current_session["end_time"]
        is_new_session = False
        
        # 1. 30분 초과 시 새 세션
        if time_diff > timedelta(minutes=30):
            is_new_session = True
            
        # 2. 검색어가 바뀌면 새 세션
        if event["event_type"] == "search":
            if current_session["query_text"] != "" and current_session["query_text"] != event["query_text"]:
                is_new_session = True
            current_session["query_text"] = event["query_text"]
            
        if is_new_session and len(current_session["events"]) > 0:
            sessions.append(current_session)
            current_session = {
                "session_id": str(uuid.uuid4()),
                "events": [],
                "query_text": event.get("query_text", "") if event["event_type"] == "search" else "",
                "start_time": event["watch_time"],
                "end_time": event["watch_time"],
                "session_text": ""
            }
            
        current_session["events"].append(event)
        current_session["end_time"] = event["watch_time"]
        if event["event_type"] == "search" and not current_session["query_text"]:
            current_session["query_text"] = event["query_text"]
            
    # 마지막 세션 추가
    if len(current_session["events"]) > 0:
        sessions.append(current_session)
        
    # 3. 세션별 텍스트 연결 (title + description + tags + query_text)
    for session in sessions:
        texts = []
        if session["query_text"]:
            texts.append(f"Query: {session['query_text']}")
            
        for ev in session["events"]:
            if ev["event_type"] == "watch":
                title = ev.get("title", "")
                desc = ev.get("description", "")
                if title: texts.append(title)
                if desc: texts.append(desc)
                
        # 4. 20토큰 미만이면 최대 5개 결합 (단순화를 위해 글자 수 기준으로 처리)
        combined_text = " | ".join(texts)
        
        # 5. 1500자 초과 시 절단
        if len(combined_text) > 1500:
            combined_text = combined_text[:1500] + "..."
            
        session["session_text"] = combined_text
        
    return sessions
