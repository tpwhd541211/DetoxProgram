from domain.analysis.nlp_service import analyze_session_text, analyze_session_text_advanced
from collections import Counter
import math
from models.schemas import NLPResult

BIT_TO_PERSONA = {
    "HHHH": {"code": "DWML", "name": "균형 탐험형"},
    "HHHL": {"code": "DWSL", "name": "자기주도 고착형"},
    "HHLH": {"code": "PWSF", "name": "수동 개방형"},
    "HHLL": {"code": "PNML", "name": "잠복 버블형"},
    "HLHH": {"code": "DWSF", "name": "감정 과열 탐험형"},
    "HLHL": {"code": "DNSL", "name": "주도 과열 고착형"},
    "HLLH": {"code": "PWMF", "name": "수동 과열 개방형"},
    "HLLL": {"code": "PNSF", "name": "과열 버블형"},
    "LHHH": {"code": "DNMF", "name": "좁은 탐험형"},
    "LHHL": {"code": "DNML", "name": "주도 단일출처형"},
    "LHLH": {"code": "PNMF", "name": "수동 단일주제형"},
    "LHLL": {"code": "PNSL", "name": "단일출처 버블형"},
    "LLHH": {"code": "DWMF", "name": "불안정 탐색형"},
    "LLHL": {"code": "PWML", "name": "불안정 고착형"},
    "LLLH": {"code": "PWSL", "name": "흔들리는 수동형"},
    "LLLL": {"code": "DNSF", "name": "고위험 폐쇄형"}
}

def calculate_detox_score(sessions, db=None):
    """
    Calculates the 6-axis scores (TDS, SBS, EBS, VOS, SMS, UAS), BRS,
    and maps the results to one of the 16 UDF personality types.
    Utilizes NLPResult cache to skip GCP NLP calls for already analyzed session texts.
    """
    scores = {
        "diversity": 0.0,
        "stability": 0.0,
        "proactivity": 0.0,
        "openness": 0.0,
        "manipulation_index": 0.0,
        
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
        
    # Bulk query NLPResult cache if db session is provided
    cache_dict = {}
    if db is not None:
        try:
            session_texts = [s.get("session_text", "") for s in sessions if s.get("session_text")]
            session_texts = list(set([t for t in session_texts if t.strip()]))
            if session_texts:
                cached_results = []
                for i in range(0, len(session_texts), 500):
                    chunk = session_texts[i:i+500]
                    results = db.query(NLPResult).filter(NLPResult.session_text.in_(chunk)).all()
                    cached_results.extend(results)
                
                for r in cached_results:
                    if r.session_text not in cache_dict and isinstance(r.analysis_data, dict):
                        cache_dict[r.session_text] = r.analysis_data
                print(f"Loaded {len(cache_dict)} cached session NLP results from DB.")
        except Exception as e:
            print(f"Error querying NLPResult cache: {e}")

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
        
        if session_text in cache_dict:
            c_data = cache_dict[session_text]
            keywords = c_data.get("keywords", [])
            category = c_data.get("category", "❓ 기타/미분류")
            stability_factor = c_data.get("stability_factor", 1.0)
            safety_factor = c_data.get("safety_factor", 1.0)
            gcp_res = c_data.get("gcp_nlp_raw")
            youtube_tags = c_data.get("youtube_tags", session.get("youtube_tags", []))
            youtube_categories = c_data.get("youtube_categories", session.get("youtube_categories", []))
            
            category_confidence = c_data.get("category_confidence", 0.0)
            category_source = c_data.get("category_source", "fallback_failed")
            category_candidates = c_data.get("category_candidates", [])
            is_uncategorized = c_data.get("is_uncategorized", True if category in ["❓ 기타/미분류", "기타/미분류"] else False)
            fallback_reason = c_data.get("fallback_reason", "no_metadata_or_keyword_match" if is_uncategorized else None)
            category_version = c_data.get("category_version", "2.0")
        else:
            # Fallback to actual analysis
            keywords, res, stability_factor, safety_factor, gcp_res = analyze_session_text_advanced(session)
            category = res.get("category", "❓ 기타/미분류")
            category_confidence = res.get("category_confidence", 0.0)
            category_source = res.get("category_source", "fallback_failed")
            category_candidates = res.get("category_candidates", [])
            is_uncategorized = res.get("is_uncategorized", True)
            fallback_reason = res.get("fallback_reason", "no_metadata_or_keyword_match")
            category_version = res.get("category_version", "2.0")
            
            youtube_tags = session.get("youtube_tags", [])
            youtube_categories = session.get("youtube_categories", [])
            cache_dict[session_text] = {
                "keywords": keywords,
                "category": category,
                "stability_factor": stability_factor,
                "safety_factor": safety_factor,
                "gcp_nlp_raw": gcp_res,
                "youtube_tags": youtube_tags,
                "youtube_categories": youtube_categories,
                "category_confidence": category_confidence,
                "category_source": category_source,
                "category_candidates": category_candidates,
                "is_uncategorized": is_uncategorized,
                "fallback_reason": fallback_reason,
                "category_version": category_version
            }
            
        session["keywords"] = keywords
        session["category"] = category
        session["stability_factor"] = stability_factor
        session["safety_factor"] = safety_factor
        session["gcp_nlp_raw"] = gcp_res
        session["youtube_tags"] = youtube_tags
        session["youtube_categories"] = youtube_categories
        
        session["category_confidence"] = category_confidence
        session["category_source"] = category_source
        session["category_candidates"] = category_candidates
        session["is_uncategorized"] = is_uncategorized
        session["fallback_reason"] = fallback_reason
        session["category_version"] = category_version
        
        is_uncat = (category == "❓ 기타/미분류" or category == "기타/미분류" or is_uncategorized)
        
        if not is_uncat:
            topics_list.append(category)
        
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
                if not is_uncat:
                    unique_topics.add(category)
                    
    # === 6-Axis UDF Calculations ===
    
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
    
    # 4-axis UDF classification thresholds:
    # 1. D/P (Director / Passenger): uas >= 55.0 -> D, else P
    # 2. W/N (Wide / Narrow): (tds + sbs) / 2.0 >= 60.0 -> W, else N
    # 3. S/M (Spicy / Mild): (ebs + sms) / 2.0 >= 60.0 -> M, else S
    # 4. F/L (Flash / Long): vos >= 55.0 -> L, else F
    char1 = "D" if uas >= 55.0 else "P"
    char2 = "W" if ((tds + sbs) / 2.0) >= 60.0 else "N"
    char3 = "M" if ((ebs + sms) / 2.0) >= 60.0 else "S"
    char4 = "L" if vos >= 55.0 else "F"
    
    persona_type = f"{char1}{char2}{char3}{char4}"
    scores["persona_type"] = persona_type
    
    return scores
