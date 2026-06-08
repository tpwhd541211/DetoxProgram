from collections import Counter
import math
import statistics

from domain.analysis.nlp_service import analyze_session_text, analyze_session_text_advanced
from models.schemas import NLPResult
from concurrent.futures import ThreadPoolExecutor, as_completed


BIT_TO_PERSONA = {
    "HHHH": {"code": "DWML", "name": "Balanced Explorer"},
    "HHHL": {"code": "DWSL", "name": "Self-led Deep Diver"},
    "HHLH": {"code": "PWSF", "name": "Recommendation Explorer"},
    "HHLL": {"code": "PNML", "name": "Narrow Bubble"},
    "HLHH": {"code": "DWSF", "name": "Stimulus Explorer"},
    "HLHL": {"code": "DNSL", "name": "Focused Deep Diver"},
    "HLLH": {"code": "PWMF", "name": "Recommendation Drifter"},
    "HLLL": {"code": "PNSF", "name": "Stimulus Bubble"},
    "LHHH": {"code": "DNMF", "name": "Quiet Specialist"},
    "LHHL": {"code": "DNML", "name": "Single-source Deep Diver"},
    "LHLH": {"code": "PNMF", "name": "Passive Specialist"},
    "LHLL": {"code": "PNSL", "name": "Single-source Bubble"},
    "LLHH": {"code": "DWMF", "name": "Anxious Explorer"},
    "LLHL": {"code": "PWML", "name": "Anxious Drifter"},
    "LLLH": {"code": "PWSL", "name": "Passive Deep Diver"},
    "LLLL": {"code": "DNSF", "name": "High-risk Loop"},
}


UNCATEGORIZED_LABELS = {
    "",
    "기타/미분류",
    "❓ 기타/미분류",
    "미분류/알수없음",
    "unknown",
    "other",
}


def _empty_scores(reason):
    return {
        "tds": None,
        "sbs": None,
        "ebs": None,
        "vos": None,
        "sms": None,
        "uas": None,
        "brs": None,
        "brs_base": None,
        "brs_penalty": 0.0,
        "brs_factors": [reason],
        "persona_type": "UNKN",
        "analysis_status": "insufficient_data",
        "data_quality": "insufficient",
    }


def _is_uncategorized(category, is_uncategorized):
    if is_uncategorized:
        return True
    if category is None:
        return True
    return str(category).strip().lower() in UNCATEGORIZED_LABELS


def _safe_datetime_gap_seconds(after, before):
    try:
        return (after - before).total_seconds()
    except Exception:
        return None


def calculate_detox_score(sessions, db=None):
    """
    Calculate 6-axis detox scores.

    Missing evidence is kept as None instead of being converted into neutral
    looking 50 point scores. That prevents empty or partial uploads from looking
    like normal analysis results.
    """
    if not sessions:
        return _empty_scores("분석할 세션이 없습니다")

    watch_events = [
        ev
        for session in sessions
        for ev in session.get("events", [])
        if ev.get("event_type") == "watch"
    ]
    if not watch_events:
        return _empty_scores("시청 이벤트가 없어 6축 점수를 산출할 수 없습니다")

    cache_dict = {}
    if db is not None:
        try:
            session_texts = [s.get("session_text") or "" for s in sessions if s.get("session_text")]
            session_texts = list({t for t in session_texts if t.strip()})
            for i in range(0, len(session_texts), 500):
                chunk = session_texts[i:i + 500]
                results = db.query(NLPResult).filter(NLPResult.session_text.in_(chunk)).all()
                for row in results:
                    if row.session_text not in cache_dict and isinstance(row.analysis_data, dict):
                        adata = row.analysis_data
                        # Skip cache if it's a failed fallback to allow retrying it
                        if adata.get("category_source") == "fallback_failed" or adata.get("gcp_nlp_raw") is None:
                            continue
                        cache_dict[row.session_text] = adata
            if cache_dict:
                print(f"Loaded {len(cache_dict)} cached session NLP results from DB.")
        except Exception as exc:
            print(f"Error querying NLPResult cache: {exc}")

    # Pre-process uncached sessions sequentially to avoid GCP NLP API rate limits and errors
    uncached_sessions = [s for s in sessions if (s.get("session_text") or "") not in cache_dict]
    if uncached_sessions:
        print(f"Processing {len(uncached_sessions)} GCP NLP calls sequentially...")
        for session in uncached_sessions:
            session_text = session.get("session_text") or ""
            if session_text in cache_dict:
                continue
            if not session_text.strip():
                cache_dict[session_text] = {
                    "keywords": [],
                    "category": "기타/미분류",
                    "stability_factor": 1.0,
                    "safety_factor": 1.0,
                    "gcp_nlp_raw": None,
                    "youtube_tags": [],
                    "youtube_categories": [],
                    "category_confidence": 0.0,
                    "category_source": "fallback_failed",
                    "category_candidates": [],
                    "is_uncategorized": True,
                    "fallback_reason": "empty_session_text",
                    "category_version": "2.0",
                }
                continue
            try:
                keywords, res, stability_factor, safety_factor, gcp_res = analyze_session_text_advanced(session)
                category = res.get("category", "기타/미분류")
                category_confidence = res.get("category_confidence", 0.0)
                category_source = res.get("category_source", "fallback_failed")
                category_candidates = res.get("category_candidates", [])
                is_uncategorized = res.get("is_uncategorized", _is_uncategorized(category, False))
                fallback_reason = res.get("fallback_reason")
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
                    "category_version": category_version,
                }
            except Exception as exc:
                print(f"Error processing session sequentially: {exc}")

    total_videos = 0
    short_videos = 0
    binge_sessions = 0
    uncategorized_count = 0
    topics_list = []
    channels_list = []
    all_words = []

    for session in sessions:
        session_text = session.get("session_text") or ""

        # Now everything should be in cache_dict (or fallback to defaults if it failed)
        if session_text in cache_dict:
            cached = cache_dict[session_text]
            keywords = cached.get("keywords", [])
            category = cached.get("category", "기타/미분류")
            stability_factor = cached.get("stability_factor", 1.0)
            safety_factor = cached.get("safety_factor", 1.0)
            gcp_res = cached.get("gcp_nlp_raw")
            youtube_tags = cached.get("youtube_tags", session.get("youtube_tags", []))
            youtube_categories = cached.get("youtube_categories", session.get("youtube_categories", []))
            category_confidence = cached.get("category_confidence", 0.0)
            category_source = cached.get("category_source", "fallback_failed")
            category_candidates = cached.get("category_candidates", [])
            is_uncategorized = cached.get("is_uncategorized", _is_uncategorized(category, False))
            fallback_reason = cached.get("fallback_reason")
            category_version = cached.get("category_version", "2.0")
        else:
            # Fallback if preprocessing failed for this session
            keywords = []
            category = "기타/미분류"
            stability_factor = 1.0
            safety_factor = 1.0
            gcp_res = None
            youtube_tags = []
            youtube_categories = []
            category_confidence = 0.0
            category_source = "fallback_failed"
            category_candidates = []
            is_uncategorized = True
            fallback_reason = "thread_pool_failed"
            category_version = "2.0"

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

        is_uncat = _is_uncategorized(category, is_uncategorized)
        if is_uncat:
            uncategorized_count += 1
        else:
            topics_list.append(category)

        for word, count in keywords:
            all_words.extend([word] * count)

        if session.get("is_binge", False):
            binge_sessions += 1

        for ev in session.get("events", []):
            if ev.get("event_type") != "watch":
                continue
            total_videos += 1
            if ev.get("is_short", False):
                short_videos += 1
            if ev.get("channel_id"):
                channels_list.append(ev["channel_id"])

    # TDS: topic diversity.
    if not topics_list:
        tds = None
    else:
        topic_counts = Counter(topics_list)
        p_k = [count / len(topics_list) for count in topic_counts.values()]
        entropy = -sum(p * math.log2(p + 1e-9) for p in p_k)
        dynamic_max = math.log2(min(15, len(topic_counts) + 4))
        tds = min(100.0, round((entropy / dynamic_max) * 100, 1)) if dynamic_max > 0 else None

    # EBS: emotional balance (Attention Span & Rest Time)
    time_gaps = []
    rest_gaps = []
    
    sorted_sessions_for_ebs = sorted(sessions, key=lambda s: s.get("start_time"))
    for i in range(1, len(sorted_sessions_for_ebs)):
        prev_end = sorted_sessions_for_ebs[i-1].get("end_time")
        curr_start = sorted_sessions_for_ebs[i].get("start_time")
        if prev_end and curr_start:
            rest_gap = _safe_datetime_gap_seconds(curr_start, prev_end)
            if rest_gap is not None and rest_gap > 0:
                rest_gaps.append(rest_gap)

    short_gaps_count = 0
    total_gaps_count = 0
    
    for session in sessions:
        evs = sorted(
            [e for e in session.get("events", []) if e.get("event_type") == "watch" and e.get("watch_time")],
            key=lambda x: x["watch_time"],
        )
        for i in range(1, len(evs)):
            gap = _safe_datetime_gap_seconds(evs[i]["watch_time"], evs[i - 1]["watch_time"])
            if gap is not None and gap > 0:
                time_gaps.append(gap)
                total_gaps_count += 1
                if gap <= 60: # Under 1 min is considered a short gap (popcorn brain/shorts)
                    short_gaps_count += 1

    if total_gaps_count == 0:
        ebs = None
    else:
        ebs_score = 100.0
        quick_bounce_ratio = short_gaps_count / total_gaps_count
        ebs_score -= (quick_bounce_ratio * 100.0)
        
        if time_gaps:
            mean_gap = statistics.mean(time_gaps)
            if mean_gap < 120:
                ebs_score = min(ebs_score, 60.0)
            elif mean_gap > 600:
                ebs_score = min(100.0, ebs_score + 10.0)
                
        if rest_gaps:
            mean_rest = statistics.mean(rest_gaps)
            if mean_rest < 3600:
                ebs_score -= 20.0
            elif mean_rest > 14400:
                ebs_score = min(100.0, ebs_score + 15.0)
                
        ebs = max(10.0, round(ebs_score, 1))

    # SBS: source balance (Base 0 model)
    # Target only the recent 30% of sessions to analyze the user's recent consumption habit
    # If there are fewer than 3 sessions, use all sessions.
    if len(sessions) >= 3:
        sorted_sessions_for_sbs = sorted(sessions, key=lambda s: s.get("start_time"))
        split_idx_sbs = max(1, int(len(sorted_sessions_for_sbs) * 0.70))
        recent_sessions_for_sbs = sorted_sessions_for_sbs[split_idx_sbs:]
    else:
        recent_sessions_for_sbs = sessions
    
    recent_channels_list = []
    for session in recent_sessions_for_sbs:
        for ev in session.get("events", []):
            if ev.get("event_type") == "watch" and ev.get("channel_id"):
                recent_channels_list.append(ev["channel_id"])
                
    if not recent_channels_list:
        sbs = None
    else:
        channel_counts = Counter(recent_channels_list)
        total_views = len(recent_channels_list)
        
        # 1. Diversity Bonus (Max 50 points)
        # Use active channels (views >= 5) to filter out 1-time scroll/click noise
        # +2.5 points per active channel up to 20 channels (20 * 2.5 = 50 points)
        active_channels = sum(1 for count in channel_counts.values() if count >= 5)
        diversity_bonus = min(50.0, active_channels * 2.5)
        
        # 2. Equality Bonus (Max 50 points)
        # Calculate Concentration Ratio of top 5 channels (CR_5)
        top_5_counts = [count for _, count in channel_counts.most_common(5)]
        cr_5 = sum(top_5_counts) / total_views if total_views > 0 else 0.0
        
        if cr_5 <= 0.15:
            equality_bonus = 50.0
        elif cr_5 >= 0.45:
            equality_bonus = 0.0
        else:
            # Linear scaling from 15% (50 pts) to 45% (0 pts)
            equality_bonus = 50.0 * (0.45 - cr_5) / 0.30
            
        sbs_score = diversity_bonus + equality_bonus
        sbs = max(20.0, min(100.0, round(sbs_score, 1)))

    # Explicit search signal. Search history helps UAS but is not required.
    search_events = [
        ev
        for session in sessions
        for ev in session.get("events", [])
        if ev.get("event_type") == "search"
    ]
    search_queries = [e.get("query_text", "") for e in search_events if e.get("query_text")]
    duplicate_search_penalty = max(0, sum(count - 1 for count in Counter(search_queries).values()) * 5)
    proactivity_signal = round(min(100.0, max(0.0, len(search_events) * 12.0 - duplicate_search_penalty)), 1)

    # VOS: new channels/categories/keywords in the recent slice.
    if len(sessions) <= 1:
        # 단일 세션 이하인 경우 비교군 생성이 불가하므로 기본값 50.0점을 부여합니다.
        vos = 50.0
    elif len(sessions) < 3:
        vos = None
    else:
        sorted_sessions = sorted(sessions, key=lambda s: s.get("start_time"))
        split_idx = max(1, int(len(sorted_sessions) * 0.70))
        history_sessions = sorted_sessions[:split_idx]
        recent_sessions = sorted_sessions[split_idx:]

        def collect(session_group):
            cats, chans, kws = set(), set(), set()
            for item in session_group:
                if not _is_uncategorized(item.get("category"), item.get("is_uncategorized", False)):
                    cats.add(item.get("category"))
                for ev in item.get("events", []):
                    if ev.get("channel_id"):
                        chans.add(ev["channel_id"])
                for kw, _ in item.get("keywords", []):
                    kws.add(kw)
            return cats, chans, kws

        hist_cats, hist_chans, hist_kws = collect(history_sessions)
        rec_cats, rec_chans, rec_kws = collect(recent_sessions)
        cat_ratio = len(rec_cats - hist_cats) / len(rec_cats) if rec_cats else 0.0
        chan_ratio = len(rec_chans - hist_chans) / len(rec_chans) if rec_chans else 0.0
        kw_ratio = len(rec_kws - hist_kws) / len(rec_kws) if rec_kws else 0.0
        
        # Scoring with Scaling Caps (Threshold raised to prevent score inflation)
        cat_score = min(100.0, (cat_ratio / 0.45) * 100.0)
        chan_score = min(100.0, (chan_ratio / 0.60) * 100.0)
        kw_score = min(100.0, (kw_ratio / 0.70) * 100.0)
        vos = round((cat_score * 0.3) + (chan_score * 0.4) + (kw_score * 0.3), 1)

    # SMS: safety/stimulation moderation (Base 0 model)
    rewatch_counts = Counter()
    valid_nlp_sessions = 0
    sms_reliability = "high"
    sms_issue = ""
    
    total_safety_factors = 0.0
    total_stability_factors = 0.0
    
    for session in sessions:
        safety_factor = session.get("safety_factor")
        stability_factor = session.get("stability_factor")
        
        # Count sessions that have text and didn't fail analysis
        if session.get("session_text") and session.get("fallback_reason") != "thread_pool_failed":
            valid_nlp_sessions += 1
            if (
                isinstance(safety_factor, (int, float))
                and isinstance(stability_factor, (int, float))
            ):
                total_safety_factors += safety_factor
                total_stability_factors += stability_factor
                    
        for ev in session.get("events", []):
            if ev.get("event_type") == "watch" and ev.get("title"):
                rewatch_counts[ev["title"]] += 1

    shorts_ratio = short_videos / total_videos if total_videos else 0.0
    long_video_ratio = 1.0 - shorts_ratio
    
    # Check reliability
    if len(sessions) > 0 and valid_nlp_sessions < len(sessions) / 2:
        sms_reliability = "low"
        sms_issue = "일부 텍스트 분석 실패 (데이터 부족)"
        
    # 1. Long-form focus bonus (Max 50 points)
    long_form_bonus = long_video_ratio * 50.0
    
    # 2. Safety bonus (Max 50 points with continuous steep scaling)
    if valid_nlp_sessions > 0:
        avg_safety = total_safety_factors / valid_nlp_sessions
        avg_stability = total_stability_factors / valid_nlp_sessions
        safety_bonus = 50.0 * max(0.0, (avg_safety * avg_stability - 0.4) / 0.6)
    else:
        # If absolutely no NLP data, assign 0.0 safety bonus to avoid inflating score
        safety_bonus = 0.0
        sms_reliability = "low"
        sms_issue = "NLP 텍스트 분석 완전 실패 (데이터 없음)"
        
    sms_score = long_form_bonus + safety_bonus
    sms = max(20.0, min(100.0, round(sms_score, 1)))

    # UAS: user agency from duration, controlled exits, search, binges and shorts.
    session_durations = []
    controlled_escapes = 0
    for session in sessions:
        has_watch = any(ev.get("event_type") == "watch" for ev in session.get("events", []))
        if not has_watch:
            continue
        duration_seconds = _safe_datetime_gap_seconds(session.get("end_time"), session.get("start_time"))
        duration_minutes = max(0.0, duration_seconds / 60.0) if duration_seconds is not None else 5.0
        if duration_minutes <= 0.5:
            duration_minutes = 5.0
        session_durations.append(duration_minutes)
        if duration_minutes <= 30.0:
            controlled_escapes += 1

    if not session_durations:
        uas = None
    else:
        avg_session_minutes = statistics.mean(session_durations)
        duration_score = max(0.0, 100.0 - (avg_session_minutes * 2.0))
        escape_bonus = min(15.0, controlled_escapes * 5.0)
        search_bonus = min(20.0, len(search_events) * 8.0)
        binge_penalty = min(20.0, (binge_sessions / len(sessions)) * 20.0)
        shorts_penalty = min(20.0, shorts_ratio * 20.0)
        uas = max(0.0, min(100.0, round(duration_score + escape_bonus + search_bonus - binge_penalty - shorts_penalty, 1)))

    axes = {
        "tds": (tds, 0.20),
        "sbs": (sbs, 0.15),
        "ebs": (ebs, 0.15),
        "vos": (vos, 0.20),
        "sms": (sms, 0.15),
        "uas": (uas, 0.15),
    }
    available_axes = [(value, weight) for value, weight in axes.values() if value is not None]
    if len(available_axes) < 3:
        scores = _empty_scores("분석 가능한 축이 3개 미만입니다")
        scores.update({
            "tds": tds,
            "sbs": sbs,
            "ebs": ebs,
            "vos": vos,
            "sms": sms,
            "uas": uas,
        })
        return scores

    total_weight = sum(weight for _, weight in available_axes)
    weighted_health = sum(value * weight for value, weight in available_axes) / total_weight
    base_risk = round(100.0 - weighted_health, 1)

    risk_penalty = 0.0
    brs_factors = []
    if shorts_ratio > 0.4:
        risk_penalty += 10.0
        brs_factors.append("숏폼 비율 높음")
    if uas is not None and uas < 40.0:
        risk_penalty += 10.0
        brs_factors.append("사용자 주도성 낮음")
    if proactivity_signal < 40.0:
        risk_penalty += 5.0
        brs_factors.append("직접 탐색 신호 부족")
    if sbs is not None and sbs < 35.0:
        risk_penalty += 6.0
        brs_factors.append("특정 채널 집중도 높음")
    if uncategorized_count / len(sessions) > 0.3:
        risk_penalty += 5.0
        brs_factors.append("미분류/저신뢰 분석 비율 높음")

    risk_penalty = min(35.0, risk_penalty)
    brs = min(100.0, round(base_risk + risk_penalty, 1))

    persona_type = "UNKN"
    valid_count = sum(1 for v in [tds, sbs, ebs, vos, sms, uas] if v is not None)
    if valid_count >= 3:
        safe_uas = uas if uas is not None else 50.0
        safe_tds = tds if tds is not None else 50.0
        safe_sbs = sbs if sbs is not None else 50.0
        safe_ebs = ebs if ebs is not None else 50.0
        safe_sms = sms if sms is not None else 50.0
        safe_vos = vos if vos is not None else 50.0

        char1 = "D" if safe_uas >= 55.0 else "P"
        char2 = "W" if ((safe_tds + safe_sbs) / 2.0) >= 60.0 else "N"
        char3 = "M" if ((safe_ebs + safe_sms) / 2.0) >= 60.0 else "S"
        char4 = "L" if safe_vos >= 55.0 else "F"
        persona_type = f"{char1}{char2}{char3}{char4}"

    return {
        "tds": tds,
        "sbs": sbs,
        "ebs": ebs,
        "vos": vos,
        "sms": sms,
        "sms_reliability": sms_reliability if 'sms_reliability' in locals() else "high",
        "sms_issue": sms_issue if 'sms_issue' in locals() else "",
        "uas": uas,
        "brs": brs,
        "brs_base": base_risk,
        "brs_penalty": risk_penalty,
        "brs_factors": brs_factors,
        "persona_type": persona_type,
        "analysis_status": "ok",
        "data_quality": "low" if total_videos < 10 else ("medium" if total_videos < 50 else "high"),
    }
