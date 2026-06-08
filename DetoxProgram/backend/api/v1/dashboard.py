from fastapi import APIRouter, HTTPException, Depends
from core.database import SessionLocal
from models.schemas import ScoreRun, NLPResult, ReportSnapshot, NormEvent, UserSession, UserStreak, MissionLog
from domain.analysis.nlp_service import CATEGORY_DICT, STOP_WORDS, clean_and_filter_keyword
from core.security import get_current_user
from collections import Counter
import math

router = APIRouter()

def get_latest_dataset_id_for_user(db, user_id: str):
    latest_run = db.query(ScoreRun).filter(ScoreRun.user_id == user_id).order_by(ScoreRun.created_at.desc()).first()
    return latest_run.dataset_id if latest_run else None

@router.get("/realtime")
async def get_realtime_data(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        dataset_id = get_latest_dataset_id_for_user(db, current_user)
        if not dataset_id:
            return {
                "time_distribution": [ {"hour": f"{h:02d}:00", "total": 0, "dopamine": 0} for h in range(24) ],
                "peak_message": "데이터가 부족하여 취약 시간대를 분석할 수 없습니다.",
                "binge_sessions": []
            }
            
        events = db.query(NormEvent).filter(NormEvent.dataset_id == dataset_id, NormEvent.parse_status == "success").all()
        # Sort events by watch_time
        events = [ev for ev in events if ev.watch_time]
        events.sort(key=lambda x: x.watch_time)
        
        # 1. 24시간 도파민 생체리듬
        hours_data = {h: {"total": 0, "dopamine": 0} for h in range(24)}
        for ev in events:
            hour = ev.watch_time.hour
            hours_data[hour]["total"] += 1
            
            title_lower = (ev.title or "").lower()
            is_high = ev.is_short or any(w in title_lower for w in ["shorts", "쇼츠", "먹방", "자극", "롤", "게임", "폭로", "사건", "사고", "레전드", "소름", "경악", "막장", "논란"])
            if is_high:
                hours_data[hour]["dopamine"] += 1
                
        time_distribution = [
            {"hour": f"{h:02d}:00", "total": hours_data[h]["total"], "dopamine": hours_data[h]["dopamine"]}
            for h in range(24)
        ]
        
        # Find peak dopamine hour block (e.g., sliding window of 2 hours)
        max_dopamine = -1
        peak_hour = 0
        for h in range(24):
            dopa_sum = hours_data[h]["dopamine"] + hours_data[(h+1)%24]["dopamine"]
            if dopa_sum > max_dopamine:
                max_dopamine = dopa_sum
                peak_hour = h
                
        if max_dopamine > 0:
            end_h = (peak_hour + 2) % 24
            peak_message = f"당신은 {peak_hour}시부터 {end_h}시 사이에 도파민성 콘텐츠 시청률이 가장 높게 치솟습니다! 루틴 관리가 필요해요."
        else:
            peak_message = "안정적인 시청 패턴을 보여주고 있습니다."
            
        # 2. 도파민 폭식 세션 분석 (간격 60분 이내)
        sessions = []
        if events:
            current_session = [events[0]]
            for ev in events[1:]:
                gap = (ev.watch_time - current_session[-1].watch_time).total_seconds() / 60.0
                if gap <= 60:
                    current_session.append(ev)
                else:
                    sessions.append(current_session)
                    current_session = [ev]
            if current_session:
                sessions.append(current_session)
                
        # Calculate duration and details for each session
        session_details = []
        for s in sessions:
            if len(s) < 3: continue # Ignore very short sessions
            duration_min = (s[-1].watch_time - s[0].watch_time).total_seconds() / 60.0 + 10 # add 10 mins buffer for the last video
            if duration_min < 30: continue
            
            # Find main culprit (most frequent channel)
            from collections import Counter
            ch_counter = Counter([ev.channel_name for ev in s if ev.channel_name and ev.channel_name != "알 수 없는 채널"])
            main_topic = ch_counter.most_common(1)[0][0] if ch_counter else "기타"
            
            session_details.append({
                "start_time": s[0].watch_time,
                "end_time": s[-1].watch_time,
                "duration_minutes": int(duration_min),
                "video_count": len(s),
                "main_keyword": main_topic
            })
            
        # Sort by duration and get top 3
        session_details.sort(key=lambda x: x["duration_minutes"], reverse=True)
        top_sessions = []
        for s in session_details[:3]:
            # format message
            date_str = s["start_time"].strftime("%Y년 %m월 %d일")
            start_h = s["start_time"].strftime("%H:%M")
            end_h = s["end_time"].strftime("%H:%M")
            hours = s["duration_minutes"] // 60
            mins = s["duration_minutes"] % 60
            dur_str = f"{hours}시간" if hours > 0 else ""
            if mins > 0: dur_str += f" {mins}분"
            
            top_sessions.append({
                "date": date_str,
                "time_range": f"{start_h} ~ {end_h}",
                "duration_str": dur_str,
                "video_count": s["video_count"],
                "main_keyword": s["main_keyword"],
                "message": f"무려 {dur_str} 동안 '{s['main_keyword']}' 위주로 연속 시청했습니다."
            })
            
        # 3. 타임라인 데이터 (유저의 전체 ScoreRun 분석 회차별 이력 연동)
        all_runs = db.query(ScoreRun).filter(ScoreRun.user_id == current_user).order_by(ScoreRun.created_at.asc()).all()
        
        timeline_data = []
        for i, run in enumerate(all_runs):
            run_date = run.created_at.strftime("%m/%d") if run.created_at else ""
            label = f"{i+1}회차 ({run_date})"
            
            # Get the top channel name for this analysis dataset
            ch_query = db.query(NormEvent.channel_name).filter(
                NormEvent.dataset_id == run.dataset_id,
                NormEvent.channel_name != None,
                NormEvent.channel_name != "",
                NormEvent.channel_name != "알 수 없는 채널"
            ).limit(100).all()
            if ch_query:
                from collections import Counter
                top_ch = Counter([r[0] for r in ch_query]).most_common(1)[0][0]
            else:
                top_ch = "기타"
                
            timeline_data.append({
                "date": label,
                "편향위험도": int(run.brs) if run.brs is not None else 0,
                "top_keyword": top_ch,
                "tds": int(run.tds) if run.tds is not None else 0,
                "sbs": int(run.sbs) if run.sbs is not None else 0,
                "ebs": int(run.ebs) if run.ebs is not None else 0,
                "vos": int(run.vos) if run.vos is not None else 0,
                "sms": int(run.sms) if run.sms is not None else 0,
                "uas": int(run.uas) if run.uas is not None else 0
            })
            
        return {
            "time_distribution": time_distribution,
            "peak_message": peak_message,
            "binge_sessions": top_sessions,
            "timeline_data": timeline_data
        }
    finally:
        db.close()

def to_int_or_none(val):
    if val is None:
        return None
    try:
        return int(val)
    except Exception:
        return None

@router.get("/persona")
async def get_persona_data(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        latest_run = db.query(ScoreRun).filter(ScoreRun.user_id == current_user).order_by(ScoreRun.created_at.desc()).first()
        if not latest_run:
            return {
                "type": "UNKN",
                "weakness": "데이터 업로드 후 분석이 완료되면 맞춤 페르소나와 분석 리포트가 이곳에 표시됩니다.",
                "ai_scores": {
                    "tds": 0, "sbs": 0, "ebs": 0, "vos": 0, "sms": 0, "uas": 0, "brs": 0
                },
                "history": [],
                "confidence": 0.0,
                "data_quality": "low",
                "comparison_statements": ["첫 번째 분석 완료 후 대시보드가 활성화됩니다."]
            }
            
        report = db.query(ReportSnapshot).filter(
            ReportSnapshot.dataset_id == latest_run.dataset_id,
            ReportSnapshot.user_id == current_user
        ).first()
        weakness = report.report_data.get("overall_summary", "") if report and isinstance(report.report_data, dict) else "충격 요법 리포트가 생성되지 않았습니다."
        
        all_runs = db.query(ScoreRun).filter(ScoreRun.user_id == current_user).order_by(ScoreRun.created_at.asc()).all()
        history = []
        for i, run in enumerate(all_runs[-5:]):
            month_str = f"분석 {i+1}회차"
            tds = run.tds
            vos = run.vos
            objectivity = int((tds + vos) / 2) if tds is not None and vos is not None else None
            history.append({"month": month_str, "objectivity": objectivity})
            
        # Generate comparative statements
        comparison_statements = []
        if len(all_runs) >= 2:
            prev_run = all_runs[-2]
            
            latest_tds = latest_run.tds
            prev_tds = prev_run.tds
            latest_sbs = latest_run.sbs
            prev_sbs = prev_run.sbs
            latest_ebs = latest_run.ebs
            prev_ebs = prev_run.ebs
            latest_vos = latest_run.vos
            prev_vos = prev_run.vos
            latest_sms = latest_run.sms
            prev_sms = prev_run.sms
            latest_uas = latest_run.uas
            prev_uas = prev_run.uas
            latest_brs = latest_run.brs
            prev_brs = prev_run.brs
            
            tds_diff = latest_tds - prev_tds if latest_tds is not None and prev_tds is not None else 0
            sbs_diff = latest_sbs - prev_sbs if latest_sbs is not None and prev_sbs is not None else 0
            ebs_diff = latest_ebs - prev_ebs if latest_ebs is not None and prev_ebs is not None else 0
            vos_diff = latest_vos - prev_vos if latest_vos is not None and prev_vos is not None else 0
            sms_diff = latest_sms - prev_sms if latest_sms is not None and prev_sms is not None else 0
            uas_diff = latest_uas - prev_uas if latest_uas is not None and prev_uas is not None else 0
            brs_diff = latest_brs - prev_brs if latest_brs is not None and prev_brs is not None else 0
            
            if tds_diff > 3:
                comparison_statements.append(f"📚 관심 주제 다양성(TDS)이 {tds_diff:+.1f}점 상승하여, 보다 넓은 범위의 관심사로 확장되었습니다.")
            elif tds_diff < -3:
                comparison_statements.append(f"📚 특정 관심 분야 위주로 시청이 좁아지는 양상을 보이고 있습니다 (TDS {tds_diff:+.1f}점).")
                
            if sbs_diff > 3:
                comparison_statements.append(f"📺 특정 유튜버나 소수 채널에 갇히지 않고 여러 출처를 균형 있게 소비하기 시작했습니다 (SBS {sbs_diff:+.1f}점).")
            elif sbs_diff < -3:
                comparison_statements.append(f"📺 특정 채널/크리에이터에 대한 의존도가 심화되었습니다 (SBS {sbs_diff:+.1f}점).")
                
            if ebs_diff > 3:
                comparison_statements.append(f"🧘 감정적으로 고요하고 안정감이 높은 힐링/교양 콘텐츠 시청 비중이 늘었습니다 (EBS {ebs_diff:+.1f}점).")
            elif ebs_diff < -3:
                comparison_statements.append(f"⚡ 논쟁적이고 감정을 자극하는 고자극 콘텐츠 시청 비중이 늘어났습니다 (EBS {ebs_diff:+.1f}점).")
                
            if vos_diff > 3:
                comparison_statements.append(f"🔑 새로운 관점을 다룬 지식 영상이나 균형 잡힌 해설을 개방적으로 시청하고 있습니다 (VOS {vos_diff:+.1f}점).")
            elif vos_diff < -3:
                comparison_statements.append(f"🔒 알고리즘 필터 버블에 가두어지는 확증편향 경향이 다소 상승했습니다 (VOS {vos_diff:+.1f}점).")
                
            if sms_diff > 3:
                comparison_statements.append(f"🛡️ 즉각적인 도파민 분비를 자극하는 숏폼이나 유해 자극물 소비가 유의미하게 줄어들었습니다 (SMS {sms_diff:+.1f}점).")
            elif sms_diff < -3:
                comparison_statements.append(f"⚠️ 말초적 자극이나 충격적 이슈를 쫓는 도파민성 콘텐츠 소비가 다소 늘었습니다 (SMS {sms_diff:+.1f}점).")
                
            if uas_diff > 3:
                comparison_statements.append(f"🧭 홈 추천 화면에 수동적으로 끌려가기보단, 검색창을 적극 활용하여 주도적으로 시청하고 있습니다 (UAS {uas_diff:+.1f}점).")
            elif uas_diff < -3:
                comparison_statements.append(f"🤖 알고리즘이 자동으로 띄워주는 추천 피드에 의존하는 수동적 시청 비중이 상승했습니다 (UAS {uas_diff:+.1f}점).")
                
            if brs_diff < -2:
                comparison_statements.append(f"🍀 종합 편향 위험도(BRS)가 {brs_diff:.1f}점 하락하여 디톡스 건강 상태가 개선되었습니다.")
            elif brs_diff > 2:
                comparison_statements.append(f"🚨 종합 편향 위험도(BRS)가 {brs_diff:+.1f}점 상승하여 알고리즘 중독 경보가 켜졌습니다.")
                
            if not comparison_statements:
                comparison_statements.append("이전 회차 대비 시청 습관의 큰 점수 변화는 없습니다. 꾸준히 건강한 디톡스를 이어가세요!")
        else:
            comparison_statements.append("첫 회차 분석 상태입니다. 다음 시청 데이터를 추가 업로드하시면 이전 대비 변화된 추이를 정밀 분석해 드립니다!")
            
        num_events = db.query(NormEvent).filter(NormEvent.dataset_id == latest_run.dataset_id, NormEvent.parse_status == "success").count()
        confidence = round(min(1.0, num_events / 200.0), 2)
        data_quality = "high" if num_events >= 200 else ("medium" if num_events >= 50 else "low")
            
        return {
            "type": latest_run.persona_type,
            "weakness": weakness,
            "dataset_id": latest_run.dataset_id,
            "confidence": confidence,
            "data_quality": data_quality,
            "ai_scores": {
                "tds": to_int_or_none(latest_run.tds),
                "sbs": to_int_or_none(latest_run.sbs),
                "ebs": to_int_or_none(latest_run.ebs),
                "vos": to_int_or_none(latest_run.vos),
                "sms": to_int_or_none(latest_run.sms),
                "uas": to_int_or_none(latest_run.uas),
                "brs": to_int_or_none(latest_run.brs)
            },
            "brs_factors": report.report_data.get("brs_factors", []) if report and isinstance(report.report_data, dict) else [],
            "history": history,
            "comparison_statements": comparison_statements
        }
    finally:
        db.close()

@router.get("/graph")
async def get_graph_data(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        dataset_id = get_latest_dataset_id_for_user(db, current_user)
        if not dataset_id:
            return {
                "state": "empty",
                "nodes": [],
                "edges": []
            }
            
        norm_events = db.query(NormEvent).filter(NormEvent.dataset_id == dataset_id).all()
        sessions = db.query(UserSession).filter(UserSession.dataset_id == dataset_id).all()
        nlp_results = db.query(NLPResult).filter(NLPResult.dataset_id == dataset_id).all()
        
        session_tags_map = {}
        for nr in nlp_results:
            tags = nr.analysis_data.get("youtube_tags", []) if isinstance(nr.analysis_data, dict) else []
            kws = nr.analysis_data.get("keywords", []) if isinstance(nr.analysis_data, dict) else []
            kw_words = [w for w, c in kws]
            cleaned_tags = [clean_and_filter_keyword(t) for t in tags]
            cleaned_kws = [clean_and_filter_keyword(w) for w in kw_words]
            session_tags_map[nr.session_id] = [t for t in cleaned_tags + cleaned_kws if t]
            
        channel_counts = Counter()
        channel_topics = {}
        
        for ev in norm_events:
            ch = ev.channel_name
            if not ch:
                continue
            channel_counts[ch] += 1
            if ch not in channel_topics:
                channel_topics[ch] = []
                
            for s in sessions:
                if s.session_start and s.session_end and ev.watch_time:
                    if s.session_start <= ev.watch_time <= s.session_end:
                        tags = session_tags_map.get(s.id, [])
                        channel_topics[ch].extend(tags)
                        break
                        
        top_channels = [ch for ch, count in channel_counts.most_common(10)]
        
        nodes = []
        edges = []
        node_id = 1
        channel_node_ids = {}
        
        max_ch_count = max(channel_counts.values()) if channel_counts else 1
        for ch in top_channels:
            ch_events = [ev for ev in norm_events if ev.channel_name == ch]
            shorts_count = 0
            long_count = 0
            for ev in ch_events:
                title_lower = ev.title.lower() if ev.title else ""
                is_evt_short = ev.is_short or title_lower.startswith("#shorts")
                if is_evt_short:
                    shorts_count += 1
                else:
                    long_count += 1
            
            total_ch = shorts_count + long_count
            if total_ch > 0:
                ratio = shorts_count / total_ch
                if ratio >= 0.8: channel_type = "쇼츠형"
                elif ratio <= 0.2: channel_type = "롱폼형"
                elif 0.2 < ratio <= 0.4: channel_type = "혼합형 (롱폼 선호)"
                elif 0.4 < ratio <= 0.6: channel_type = "혼합형"
                else: channel_type = "혼합형 (쇼츠 선호)"
            else:
                channel_type = "롱폼형"
                
            ch_display = ch[:12] + "..." if len(ch) > 12 else ch
            size = int(16 + (channel_counts[ch] / max_ch_count) * 12)
            nodes.append({
                "id": node_id,
                "label": f"📺 {ch_display}\n({channel_type})",
                "group": "channel",
                "size": min(30, size)
            })
            channel_node_ids[ch] = node_id
            node_id += 1
            
        all_graph_topics = set()
        for ch in top_channels:
            topic_counter = Counter(channel_topics[ch])
            top_topics_for_ch = [t for t, c in topic_counter.most_common(3)]
            all_graph_topics.update(top_topics_for_ch)
 
        keyword_categories = {}
        for nr in nlp_results:
            category = nr.analysis_data.get("category", "❓ 기타/미분류") if isinstance(nr.analysis_data, dict) else "❓ 기타/미분류"
            if category in ["❓ 기타/미분류", "기타/미분류"]:
                continue
            tags = nr.analysis_data.get("youtube_tags", []) if isinstance(nr.analysis_data, dict) else []
            kws = nr.analysis_data.get("keywords", []) if isinstance(nr.analysis_data, dict) else []
            kw_words = [w for w, c in kws]
            cleaned_tags = [clean_and_filter_keyword(t) for t in tags]
            cleaned_kws = [clean_and_filter_keyword(w) for w in kw_words]
            for word in set(cleaned_tags + cleaned_kws):
                if word:
                    if word not in keyword_categories:
                        keyword_categories[word] = Counter()
                    keyword_categories[word][category] += 1
 
        topic_to_category = {}
        for topic in all_graph_topics:
            matched_cat = None
            if topic in keyword_categories:
                most_common = keyword_categories[topic].most_common(1)
                if most_common:
                    matched_cat = most_common[0][0]
                    
            if not matched_cat or matched_cat in ["❓ 기타/미분류", "기타/미분류"]:
                t_lower = topic.lower()
                for cat, words in CATEGORY_DICT.items():
                    if topic in words or any(w.lower() in t_lower for w in words):
                        matched_cat = cat
                        break
                        
            if matched_cat and matched_cat not in ["❓ 기타/미분류", "기타/미분류"]:
                topic_to_category[topic] = matched_cat
 
        unclassified_topics = [t for t in all_graph_topics if t not in topic_to_category]
        if unclassified_topics:
            try:
                from infrastructure.llm_service import classify_topics_batch
                llm_mapped = classify_topics_batch(unclassified_topics)
                for topic, cat in llm_mapped.items():
                    if cat and cat not in ["❓ 기타/미분류", "기타/미분류"]:
                        topic_to_category[topic] = cat
            except Exception as e:
                print(f"Error calling classify_topics_batch: {e}")
 
        topic_nodes = {}
        for ch in top_channels:
            topic_counter = Counter(channel_topics[ch])
            top_topics_for_ch = [t for t, c in topic_counter.most_common(3)]
            
            for topic in top_topics_for_ch:
                if topic not in topic_nodes:
                    matched_cat = topic_to_category.get(topic, "❓ 기타/미분류")
                    group = "other"
                    if matched_cat:
                        raw_group = matched_cat.split()[-1]
                        if any(kw in raw_group for kw in ["테크", "금융", "리뷰", "쇼핑", "소비"]): group = "business_tech"
                        elif any(kw in raw_group for kw in ["예능", "엔터", "아이돌", "연예", "애니", "웹툰", "음악", "요리", "먹방", "패션", "뷰티"]): group = "entertainment"
                        elif any(kw in raw_group for kw in ["과학", "지식", "공부", "입시", "뉴스", "정치", "사회", "부동산", "자동차"]): group = "info_society"
                        elif any(kw in raw_group for kw in ["운동", "건강", "스포츠", "일상", "취미", "자기계발"]): group = "life_health"
                        elif "게임" in raw_group: group = "game"
                    
                    nodes.append({
                        "id": node_id,
                        "label": topic,
                        "group": group,
                        "size": 12
                    })
                    topic_nodes[topic] = node_id
                    node_id += 1
                    
                edges.append({
                    "source": channel_node_ids[ch],
                    "target": topic_nodes[topic],
                    "value": topic_counter[topic]
                })
        if not nodes:
            return {"state": "empty", "nodes": [], "edges": []}
        return {"state": "success", "nodes": nodes, "edges": edges}
    finally:
        db.close()

@router.get("/guide")
async def get_guide_data(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        dataset_id = get_latest_dataset_id_for_user(db, current_user)
        if not dataset_id:
            return {
                "streak_days": 0,
                "daily_missions": [],
                "streak_history": [],
                "completed_indices": []
            }
            
        report = db.query(ReportSnapshot).filter(
            ReportSnapshot.dataset_id == dataset_id,
            ReportSnapshot.user_id == current_user
        ).first()
        
        daily_missions = []
        if report and isinstance(report.report_data, dict) and "missions" in report.report_data:
            for idx, m in enumerate(report.report_data["missions"]):
                daily_missions.append({
                    "id": idx + 1,
                    "task": f"[{m.get('mission_type', '미션')}] {m.get('description', '')} - {m.get('success_condition', '')}",
                    "completed": False
                })
        else:
            score = db.query(ScoreRun).filter(ScoreRun.dataset_id == dataset_id).first()
            if score:
                dimensions = [
                    ("tds", score.tds, "주제 다양성", "다양한 분야의 시청이 부족합니다. 평소와 완전히 다른 새로운 주제를 시청해 보세요.", "새로운 카테고리 영상 10분 이상 시청 완료", "다큐멘터리"),
                    ("sbs", score.sbs, "출처 균형", "특정 소수 크리에이터 채널 시청 비중이 너무 높습니다. 다른 유익한 전문 채널을 탐색해 보세요.", "구독 외 추천 채널 영상 1개 시청 완료", "전문가 심층 분석"),
                    ("ebs", score.ebs, "감정 균형", "최근 감정적으로 자극되거나 편향된 영상을 많이 시청했습니다. 차분하고 안정된 교양 영상을 감상해 보세요.", "마음이 편안해지는 클래식/힐링 영상 시청 완료", "스트레스 완화 음악"),
                    ("vos", score.vos, "관점 개방", "확증 편향의 우려가 있습니다. 내가 가진 입장과 다른 관점의 해설이나 원본 사료를 검색하여 비교해 보세요.", "다른 입장을 담은 영상 시청 완료", "지식의 역사적 사실과 원인"),
                    ("sms", score.sms, "유해 안전", "도파민을 과도하게 자극하는 숏폼 위주의 시청이 우려됩니다. 10분 이상의 긴 호흡 영상을 시청해 보세요.", "10분 이상 롱폼 영상 시청 완료", "뇌 과학 도파민 비밀"),
                    ("uas", score.uas, "사용자 주도", "알고리즘 추천 피드에 끌려다니는 수동 시청 비율이 높습니다. 직접 알고 싶은 키워드를 검색해서 시청해 보세요.", "직접 검색창 키워드 검색 시청 완료", "나를 발전시키는 취미")
                ]
                sorted_dims = sorted(dimensions, key=lambda x: x[1])
                weak_dims = sorted_dims[:3]
                for idx, (code, val, name, desc, succ, query) in enumerate(weak_dims):
                    daily_missions.append({
                        "id": idx + 1,
                        "task": f"[{name} 회복] {desc} - {succ}",
                        "completed": False
                    })
            else:
                daily_missions = [
                    {"id": 1, "task": "[주도성 회복] 수동적인 자동재생 시청 대신 직접 검색하여 지식 영상 1개 끝까지 시청 - 영상 끝까지 시청 완료", "completed": False},
                    {"id": 2, "task": "[유해 안전] 말초적 자극을 주는 쇼츠 대신 10분 이상의 인문학 롱폼 영상 시청 - 롱폼 시청 완료", "completed": False}
                ]
            
        user_streak = db.query(UserStreak).filter(UserStreak.user_id == current_user).first()
        from datetime import datetime, date, timedelta, timezone
        KST = timezone(timedelta(hours=9))
        today = datetime.now(KST).date()
        yesterday = today - timedelta(days=1)
        
        def get_kst_date(dt):
            if not dt: return None
            if isinstance(dt, str):
                try:
                    dt = datetime.fromisoformat(dt)
                except ValueError:
                    dt = datetime.strptime(dt.split('.')[0], "%Y-%m-%d %H:%M:%S")
            return dt.replace(tzinfo=timezone.utc).astimezone(KST).date()
        
        if user_streak:
            if user_streak.last_completed_date:
                last_date = get_kst_date(user_streak.last_completed_date)
                if last_date < yesterday:
                    user_streak.current_streak = 0
                    user_streak.last_completed_date = None
                    db.commit()
            streak_days = user_streak.current_streak
        else:
            streak_days = 0
        
        today_logs = db.query(MissionLog).filter(
            MissionLog.plan_id == current_user, 
            MissionLog.completed_yn == True
        ).all()
        
        completed_indices = [int(log.mission_id) for log in today_logs if get_kst_date(log.completed_at) == today]
        
        seven_days_ago = today - timedelta(days=7)
        past_logs = db.query(MissionLog).filter(
            MissionLog.plan_id == current_user,
            MissionLog.completed_yn == True
        ).all()
        
        from collections import defaultdict
        date_counts = defaultdict(set)
        for log in past_logs:
            log_date = get_kst_date(log.completed_at)
            if log_date and log_date >= seven_days_ago:
                date_counts[log_date.strftime("%Y-%m-%d")].add(log.mission_id)
                
        streak_history = [d for d, m_set in date_counts.items() if len(m_set) >= 3]
            
        return {
            "streak_days": streak_days,
            "daily_missions": daily_missions,
            "streak_history": streak_history,
            "completed_indices": completed_indices
        }
    finally:
        db.close()

from pydantic import BaseModel
from typing import List
class SyncMissionsRequest(BaseModel):
    completed_indices: List[int]

@router.post("/guide/sync")
async def sync_missions(req: SyncMissionsRequest, current_user: str = Depends(get_current_user)):
    from datetime import datetime, date, timedelta, timezone
    KST = timezone(timedelta(hours=9))
    db = SessionLocal()
    try:
        today = datetime.now(KST).date()
        yesterday = today - timedelta(days=1)
        
        def get_kst_date(dt):
            if not dt: return None
            if isinstance(dt, str):
                try:
                    dt = datetime.fromisoformat(dt)
                except ValueError:
                    dt = datetime.strptime(dt.split('.')[0], "%Y-%m-%d %H:%M:%S")
            return dt.replace(tzinfo=timezone.utc).astimezone(KST).date()
        
        old_logs = db.query(MissionLog).filter(MissionLog.plan_id == current_user).all()
        for log in old_logs:
            if get_kst_date(log.completed_at) == today:
                db.delete(log)
        db.commit()
        
        for idx in req.completed_indices:
            new_log = MissionLog(
                plan_id=current_user,
                mission_id=str(idx),
                completed_yn=True,
                completed_at=datetime.utcnow()
            )
            db.add(new_log)
        db.commit()
        
        user_streak = db.query(UserStreak).filter(UserStreak.user_id == current_user).first()
        if not user_streak:
            user_streak = UserStreak(user_id=current_user, current_streak=0)
            db.add(user_streak)
            db.commit()
        else:
            if user_streak.last_completed_date:
                last_date = get_kst_date(user_streak.last_completed_date)
                if last_date < yesterday and last_date != today:
                    user_streak.current_streak = 0
                    user_streak.last_completed_date = None
                    db.commit()
            
        if len(req.completed_indices) >= 3:
            last_date = get_kst_date(user_streak.last_completed_date)
            if not last_date or last_date != today:
                user_streak.current_streak += 1
                user_streak.last_completed_date = datetime.utcnow()
                db.commit()
        else:
            last_date = get_kst_date(user_streak.last_completed_date)
            if last_date == today:
                user_streak.current_streak = max(0, user_streak.current_streak - 1)
                if user_streak.current_streak > 0:
                    user_streak.last_completed_date = datetime.utcnow() - timedelta(days=1)
                else:
                    user_streak.last_completed_date = None
                db.commit()
                
        return {"status": "ok", "current_streak": user_streak.current_streak}
    finally:
        db.close()

@router.get("/dashboard/{dataset_id}")
async def get_dashboard_data(dataset_id: str, current_user: str = Depends(get_current_user)):
    from datetime import datetime
    db = SessionLocal()
    try:
        score = db.query(ScoreRun).filter(
            ScoreRun.dataset_id == dataset_id,
            ScoreRun.user_id == current_user
        ).first()
        
        if not score:
            raise HTTPException(status_code=404, detail="Dataset not found or access denied")
            
        report = db.query(ReportSnapshot).filter(
            ReportSnapshot.dataset_id == dataset_id,
            ReportSnapshot.user_id == current_user
        ).first()
        
        raw_events = db.query(NormEvent).filter(NormEvent.dataset_id == dataset_id, NormEvent.parse_status == "success").all()
        events = [ev for ev in raw_events if ev.channel_name and ev.channel_name.strip() != "" and ev.channel_name != "알 수 없는 채널"]
        
        sorted_events = sorted(events, key=lambda x: x.watch_time if x.watch_time else datetime.min, reverse=True)
        
        history_list = []
        for ev in sorted_events[:15]:
            title_lower = ev.title.lower() if ev.title else ""
            is_high = any(w in title_lower for w in ["shorts", "쇼츠", "먹방", "자극", "롤", "게임", "폭로", "사건", "사고", "레전드", "소름", "경악", "막장", "논란"])
            history_list.append({
                "id": ev.id,
                "title": ev.title or "제목 없음",
                "channel_name": ev.channel_name,
                "watch_time": ev.watch_time.isoformat() if ev.watch_time else None,
                "video_id": ev.video_id,
                "dopamine_tag": "⚡ 고도파민" if is_high else "🧘 저도파민/유익"
            })
            
        channel_counts = Counter(ev.channel_name for ev in events)
        total_valid = sum(channel_counts.values()) or 1
        top_channels = []
        for name, count in channel_counts.most_common(5):
            top_channels.append({
                "name": name,
                "count": count,
                "percentage": round((count / total_valid) * 100, 1)
            })
            
        session_data = db.query(UserSession.total_events, NLPResult.analysis_data).join(
            NLPResult, UserSession.id == NLPResult.session_id
        ).filter(UserSession.dataset_id == dataset_id).all()
        
        total_videos = 0
        uncategorized_videos = 0
        category_event_counts = Counter()
        for total_events, analysis_data in session_data:
            events_count = total_events or 0
            total_videos += events_count
            if isinstance(analysis_data, dict):
                category = analysis_data.get("category", "❓ 기타/미분류")
                clean_cat = category.split()[-1] if len(category.split()) > 1 else category
                if clean_cat == "기타/미분류":
                    uncategorized_videos += events_count
                else:
                    category_event_counts[clean_cat] += events_count
                
        total_category_videos = sum(category_event_counts.values()) or 1
        top_interests = []
        category_color_map = {
            "경제/금융": "#3B82F6",
            "IT/테크": "#8B5CF6",
            "게임": "#EC4899",
            "과학/지식": "#06B6D4",
            "엔터/예능": "#F59E0B",
            "건강/운동": "#10B981",
            "취미/일상": "#0D9488",
            "뉴스/정치/사회": "#EF4444",
            "연예/아이돌": "#F43F5E",
            "음악": "#84CC16",
            "먹방/요리": "#F97316",
            "뷰티/패션": "#D946EF",
            "자동차": "#4B5563",
            "부동산": "#1E3A8A",
            "자기계발": "#6366F1",
            "공부/입시": "#14B8A6",
            "리뷰/언박싱": "#A855F7",
            "애니/웹툰": "#FF007F",
            "스포츠": "#0284C7",
            "쇼핑/소비": "#EAB308",
            "기타/미분류": "#64748B"
        }
        for cat, count in category_event_counts.most_common(5):
            pct = round((count / total_category_videos) * 100, 1)
            color = category_color_map.get(cat, "#64748B")
            top_interests.append({
                "name": cat,
                "percentage": pct,
                "color": color
            })
            
        uncategorized_pct = round((uncategorized_videos / (total_videos or 1)) * 100, 1)
        if uncategorized_pct > 50:
            uncat_msg = "분류되지 않은 시청 기록이 많습니다."
        elif uncategorized_pct > 20:
            uncat_msg = "일부 시청 기록이 분류되지 않았습니다."
        else:
            uncat_msg = "대부분의 시청 기록이 성공적으로 분류되었습니다."
            
        uncategorized_data = {
            "percentage": uncategorized_pct,
            "count": uncategorized_videos,
            "message": uncat_msg
        }
            
        num_events = len(raw_events)
        confidence = round(min(1.0, num_events / 200.0), 2)
        data_quality = "high" if num_events >= 200 else ("medium" if num_events >= 50 else "low")
            
        return {
            "dataset_id": dataset_id,
            "scores": {
                "tds": score.tds,
                "sbs": score.sbs,
                "ebs": score.ebs,
                "vos": score.vos,
                "sms": score.sms,
                "uas": score.uas,
                "brs": score.brs,
                "confidence": confidence,
                "data_quality": data_quality,
                "persona_type": score.persona_type
            },
            "report": report.report_data if report else None,
            "uncategorized": uncategorized_data,
            "contents": {
                "watch_history": history_list,
                "top_channels": top_channels,
                "top_interests": top_interests,
                "uncategorized": uncategorized_data
            }
        }
    finally:
        db.close()

from pydantic import BaseModel
class SurveyDataRequest(BaseModel):
    tds: int
    sbs: int
    ebs: int
    vos: int
    sms: int
    uas: int

@router.post("/survey")
async def save_survey_data(req: SurveyDataRequest, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        from models.schemas import SurveyResponse
        survey = db.query(SurveyResponse).filter(SurveyResponse.user_id == current_user).first()
        if not survey:
            survey = SurveyResponse(user_id=current_user)
            db.add(survey)
        
        survey.tds = req.tds
        survey.sbs = req.sbs
        survey.ebs = req.ebs
        survey.vos = req.vos
        survey.sms = req.sms
        survey.uas = req.uas
        db.commit()
        return {"status": "ok"}
    finally:
        db.close()

@router.get("/survey")
async def get_survey_data(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        from models.schemas import SurveyResponse
        survey = db.query(SurveyResponse).filter(SurveyResponse.user_id == current_user).first()
        if not survey:
            return {"tds": 50, "sbs": 50, "ebs": 50, "vos": 50, "sms": 50, "uas": 50}
        return {
            "tds": survey.tds,
            "sbs": survey.sbs,
            "ebs": survey.ebs,
            "vos": survey.vos,
            "sms": survey.sms,
            "uas": survey.uas
        }
    finally:
        db.close()
