from services.nlp_service import extract_keywords, classify_text_by_keywords, analyze_sentiment_and_stimulus
from collections import Counter
import math

def calculate_detox_score(sessions):
    """
    세션 데이터를 바탕으로 UDF 명세서에 따른 6가지 차원(TDS, SBS, EBS, VOS, SMS, UAS)과
    종합 편향 위험도(BRS)를 계산하고, 4글자 성향 유형을 도출합니다.
    """
    scores = {
        # Original keys (compatibility)
        "diversity": 0.0,
        "stability": 0.0,
        "proactivity": 0.0,
        "openness": 0.0,
        "manipulation_index": 0.0,
        
        # 6-axis keys (Strict UDF Spec)
        "tds": 50.0,
        "sbs": 50.0,
        "ebs": 50.0,
        "vos": 50.0,
        "sms": 50.0,
        "uas": 50.0,
        "brs": 0.0,
        
        "persona_type": "UNKN"
    }
    
    if not sessions:
        return scores
        
    total_videos = 0
    unique_channels = set()
    unique_topics = set()
    search_count = 0
    
    all_words = []
    total_stability = 0.0
    total_safety = 0.0
    
    topics_list = []
    channels_list = []
    
    for session in sessions:
        if session.get("query_text"):
            search_count += 1
            
        session_text = session.get("session_text", "")
        keywords = extract_keywords(session_text, num_keywords=10)
        session["keywords"] = keywords
        
        category = classify_text_by_keywords(keywords)
        session["category"] = category
        if category != "❓ 기타/미분류":
            topics_list.append(category)
        
        stability_factor, safety_factor = analyze_sentiment_and_stimulus(session_text)
        session["stability_factor"] = stability_factor
        session["safety_factor"] = safety_factor
        
        total_stability += stability_factor
        total_safety += safety_factor
        
        for word, count in keywords:
            all_words.extend([word] * count)
            
        for ev in session.get("events", []):
            if ev.get("event_type") == "watch":
                total_videos += 1
                if ev.get("channel_id"):
                    unique_channels.add(ev["channel_id"])
                    channels_list.append(ev["channel_id"])
                if category != "❓ 기타/미분류":
                    unique_topics.add(category)
                    
    # === 6-Axis UDF Formulas ===
    
    # 1. 주제 다양성 점수 (TDS): Entropy-based
    if not topics_list:
        tds = 50.0
    else:
        topic_counts = Counter(topics_list)
        N_topic = len(topics_list)
        p_k = [count / N_topic for count in topic_counts.values()]
        H = -sum(p * math.log(p) for p in p_k)
        
        unique_topic_count = len(topic_counts)
        Hmax = math.log(min(unique_topic_count, 8)) if min(unique_topic_count, 8) > 1 else 1.0
        coverage = min(1.0, N_topic / 30.0)
        tds = round(100 * (H / Hmax) * coverage, 1)
        
    # 2. 출처 균형 점수 (SBS): HHI-based
    if not channels_list:
        sbs = 50.0
    else:
        N_source = len(channels_list)
        channel_counts = Counter(channels_list)
        s_i = [count / N_source for count in channel_counts.values()]
        HHI = sum(s ** 2 for s in s_i)
        M = len(channel_counts)
        if M <= 1:
            sbs = 0.0
        else:
            sbs = round(100 * (1 - HHI) / (1 - 1 / M), 1)
        if M < 3 and N_source >= 20:
            sbs = min(sbs, 40.0)
            
    # 3. 감정 균형 점수 (EBS)
    ebs = round((total_stability / len(sessions)) * 100, 1) if sessions else 50.0
    
    # 4. 관점 개방성 점수 (VOS)
    unique_words = set(all_words)
    vos = min(100.0, round((len(unique_words) / 35.0) * 100, 1)) if unique_words else 50.0
    
    # 5. 유해/자극 안전 점수 (SMS)
    sms = round((total_safety / len(sessions)) * 100, 1) if sessions else 50.0
    
    # 6. 사용자 주도성 점수 (UAS)
    uas = round((search_count / len(sessions)) * 100, 1) if sessions else 0.0
    
    # 종합 편향 위험도 (BRS): Weighted health index subtraction
    weighted_health = 0.20 * tds + 0.15 * sbs + 0.15 * ebs + 0.20 * vos + 0.15 * sms + 0.15 * uas
    brs = round(100.0 - weighted_health, 1)
    
    # Assign values back to scores dict
    scores["tds"] = tds
    scores["sbs"] = sbs
    scores["ebs"] = ebs
    scores["vos"] = vos
    scores["sms"] = sms
    scores["uas"] = uas
    scores["brs"] = brs
    
    # Original keys compatibility mapping
    scores["diversity"] = tds
    scores["stability"] = ebs
    scores["proactivity"] = uas
    scores["openness"] = vos
    scores["manipulation_index"] = brs
    
    # 4-axis DSAO calculation
    # 1축 (Search Style): D (Director) if uas >= 50 else P (Passenger)
    t1 = "D" if uas >= 50 else "P"
    # 2축 (Scope): W (Wide) if tds >= 50 else N (Narrow)
    t2 = "W" if tds >= 50 else "N"
    # 3축 (Dopamine Intensity): S (Spicy) if sms < 50 else M (Mild)
    t3 = "S" if sms < 50 else "M"
    
    # 4축 (Viewing Pace/Length): F (Flash) if avg duration < 180s else L (Long)
    watch_durations = []
    for session in sessions:
        for ev in session.get("events", []):
            if ev.get("event_type") == "watch" and ev.get("duration_watched") is not None:
                watch_durations.append(ev.get("duration_watched"))
                
    avg_dur = sum(watch_durations) / len(watch_durations) if watch_durations else 300
    t4 = "F" if avg_dur < 180 else "L"
    
    scores["persona_type"] = f"{t1}{t2}{t3}{t4}"
    
    return scores
