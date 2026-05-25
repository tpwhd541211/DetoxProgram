from fastapi import APIRouter, HTTPException
from core.database import SessionLocal
from models.schemas import ScoreRun, NLPResult, ReportSnapshot, NormEvent
from services.nlp_service import CATEGORY_DICT
from collections import Counter
import math

router = APIRouter()

def get_latest_dataset_id(db):
    latest_run = db.query(ScoreRun).order_by(ScoreRun.created_at.desc()).first()
    return latest_run.dataset_id if latest_run else None

@router.get("/realtime")
async def get_realtime_data():
    db = SessionLocal()
    try:
        dataset_id = get_latest_dataset_id(db)
        if not dataset_id:
            # Fallback mock if no upload has happened yet
            return {
                "today_trend": [
                    {"time": "09:00", "dopamine": 40},
                    {"time": "12:00", "dopamine": 65},
                    {"time": "15:00", "dopamine": 85},
                    {"time": "18:00", "dopamine": 92},
                    {"time": "Now", "dopamine": 45}
                ]
            }
            
        events = db.query(NormEvent).filter(NormEvent.dataset_id == dataset_id, NormEvent.parse_status == "success").all()
        
        # 3시간 단위 블록으로 집계
        hour_counts = {9: 0, 12: 0, 15: 0, 18: 0, 21: 0, 0: 0}
        for ev in events:
            if ev.watch_time:
                hour = ev.watch_time.hour
                closest = min([9, 12, 15, 18, 21, 24], key=lambda x: abs(x - hour))
                if closest == 24:
                    closest = 0
                hour_counts[closest] += 1
                
        max_count = max(hour_counts.values()) if hour_counts.values() else 1
        if max_count == 0:
            max_count = 1
            
        trend = [
            {"time": "09:00", "dopamine": int(30 + (hour_counts[9] / max_count) * 60)},
            {"time": "12:00", "dopamine": int(30 + (hour_counts[12] / max_count) * 60)},
            {"time": "15:00", "dopamine": int(30 + (hour_counts[15] / max_count) * 60)},
            {"time": "18:00", "dopamine": int(30 + (hour_counts[18] / max_count) * 60)},
            {"time": "21:00", "dopamine": int(30 + (hour_counts[21] / max_count) * 60)},
            {"time": "Now", "dopamine": int(30 + (hour_counts[0] / max_count) * 60)}
        ]
        return {"today_trend": trend}
    finally:
        db.close()

@router.get("/persona")
async def get_persona_data():
    db = SessionLocal()
    try:
        latest_run = db.query(ScoreRun).order_by(ScoreRun.created_at.desc()).first()
        if not latest_run:
            return {
                "type": "INTJ-A",
                "weakness": "특정 분야에 과도하게 매몰되어 다른 관점을 수용하지 못할 위험(확증편향)이 큽니다.",
                "ai_scores": { "div": 38, "sta": 76, "ini": 56, "ope": 41 },
                "history": [ {"month": "1월", "objectivity": 70}, {"month": "3월", "objectivity": 65}, {"month": "5월", "objectivity": 56} ]
            }
            
        report = db.query(ReportSnapshot).filter(ReportSnapshot.dataset_id == latest_run.dataset_id).first()
        weakness = report.report_data.get("overall_summary", "") if report and isinstance(report.report_data, dict) else "충격 요법 리포트가 생성되지 않았습니다."
        
        # 역사적 업로드 이력으로 차트 그리기
        all_runs = db.query(ScoreRun).order_by(ScoreRun.created_at.asc()).all()
        history = []
        for i, run in enumerate(all_runs[-5:]):
            month_str = f"분석 {i+1}회차"
            objectivity = int((run.diversity + run.openness) / 2)
            history.append({"month": month_str, "objectivity": objectivity})
            
        return {
            "type": latest_run.persona_type,
            "weakness": weakness,
            "ai_scores": {
                "div": int(latest_run.diversity),
                "sta": int(latest_run.stability),
                "ini": int(latest_run.proactivity),
                "ope": int(latest_run.openness),
                "tds": int(latest_run.tds or latest_run.diversity),
                "sbs": int(latest_run.sbs or latest_run.diversity),
                "ebs": int(latest_run.ebs or latest_run.stability),
                "vos": int(latest_run.vos or latest_run.openness),
                "sms": int(latest_run.sms or latest_run.stability),
                "uas": int(latest_run.uas or latest_run.proactivity),
                "brs": int(latest_run.brs or latest_run.manipulation_index)
            },
            "history": history
        }
    finally:
        db.close()

@router.get("/graph")
async def get_graph_data():
    db = SessionLocal()
    try:
        dataset_id = get_latest_dataset_id(db)
        if not dataset_id:
            # Fallback mock
            return {
                "nodes": [
                    { "id": 1, "label": "인공지능", "group": "tech", "size": 30 },
                    { "id": 2, "label": "기술/IT", "group": "tech", "size": 25 },
                    { "id": 3, "label": "경제/금융", "group": "economy", "size": 20 }
                ],
                "edges": [
                    { "source": 1, "target": 2 }
                ]
            }
            
        nlp_results = db.query(NLPResult).filter(NLPResult.dataset_id == dataset_id).all()
        
        kw_counter = Counter()
        session_kws = []
        for nr in nlp_results:
            kws = nr.analysis_data.get("keywords", []) if isinstance(nr.analysis_data, dict) else []
            session_words = [item[0] for item in kws]
            session_kws.append(session_words)
            for word, count in kws:
                kw_counter[word] += count
                
        top_kws = [w for w, _ in kw_counter.most_common(12)]
        nodes = []
        for idx, kw in enumerate(top_kws):
            group = "other"
            for cat, words in CATEGORY_DICT.items():
                if kw in words:
                    group = cat.split()[-1] # e.g. "테크" or "금융"
                    break
            max_val = max(kw_counter.values()) if kw_counter.values() else 1
            nodes.append({
                "id": idx + 1,
                "label": kw,
                "group": group,
                "size": int(15 + (kw_counter[kw] / max_val) * 20)
            })
            
        edges = []
        for i in range(len(top_kws)):
            for j in range(i+1, len(top_kws)):
                w1, w2 = top_kws[i], top_kws[j]
                co_count = sum(1 for s in session_kws if w1 in s and w2 in s)
                if co_count > 0:
                    edges.append({
                        "source": i + 1,
                        "target": j + 1,
                        "value": co_count
                    })
        return {"nodes": nodes, "edges": edges}
    finally:
        db.close()

@router.get("/guide")
async def get_guide_data():
    db = SessionLocal()
    try:
        dataset_id = get_latest_dataset_id(db)
        if not dataset_id:
            return {
                "streak_days": 3,
                "daily_missions": [
                    {"id": 1, "task": "반대 성향 영상 1개 시청", "completed": False}
                ],
                "streak_history": []
            }
            
        report = db.query(ReportSnapshot).filter(ReportSnapshot.dataset_id == dataset_id).first()
        daily_missions = []
        if report and isinstance(report.report_data, dict) and "missions" in report.report_data:
            for idx, m in enumerate(report.report_data["missions"]):
                daily_missions.append({
                    "id": idx + 1,
                    "task": f"[{m.get('mission_type', '미션')}] {m.get('description', '')} - {m.get('success_condition', '')}",
                    "completed": False
                })
        else:
            daily_missions = [
                {"id": 1, "task": "반대 성향 영상 1개 끝까지 시청", "completed": True},
                {"id": 2, "task": "숏폼 영상 30분 미만 시청", "completed": False}
            ]
            
        return {
            "streak_days": len(daily_missions) + 2,
            "daily_missions": daily_missions,
            "streak_history": ["2026-05-21", "2026-05-22"]
        }
    finally:
        db.close()

@router.get("/dashboard/{dataset_id}")
async def get_dashboard_data(dataset_id: str):
    from datetime import datetime
    db = SessionLocal()
    try:
        score = db.query(ScoreRun).filter(ScoreRun.dataset_id == dataset_id).first()
        report = db.query(ReportSnapshot).filter(ReportSnapshot.dataset_id == dataset_id).first()
        if not score:
            raise HTTPException(status_code=404, detail="Dataset not found")
            
        # 추가 콘텐츠 데이터를 위한 NormEvent 조회
        events = db.query(NormEvent).filter(NormEvent.dataset_id == dataset_id, NormEvent.parse_status == "success").all()
        
        # 1. 최근 시청 내역 리스트 (최대 15개)
        sorted_events = sorted(events, key=lambda x: x.watch_time if x.watch_time else datetime.min, reverse=True)
        
        history_list = []
        for ev in sorted_events[:15]:
            title_lower = ev.title.lower() if ev.title else ""
            is_high = any(w in title_lower for w in ["shorts", "쇼츠", "먹방", "자극", "롤", "게임", "폭로", "사건", "사고", "레전드", "소름", "경악", "막장", "논란"])
            history_list.append({
                "id": ev.id,
                "title": ev.title or "제목 없음",
                "channel_name": ev.channel_name or "알 수 없는 채널",
                "watch_time": ev.watch_time.isoformat() if ev.watch_time else None,
                "video_id": ev.video_id,
                "dopamine_tag": "⚡ 고도파민" if is_high else "🧘 저도파민/유익"
            })
            
        # 2. 선호 채널 탑 5
        channel_counts = Counter(ev.channel_name for ev in events if ev.channel_name)
        total_valid = sum(channel_counts.values()) or 1
        top_channels = []
        for name, count in channel_counts.most_common(5):
            top_channels.append({
                "name": name,
                "count": count,
                "percentage": round((count / total_valid) * 100, 1)
            })
            
        return {
            "dataset_id": dataset_id,
            "scores": {
                "diversity": score.diversity,
                "stability": score.stability,
                "proactivity": score.proactivity,
                "openness": score.openness,
                "manipulation_index": score.manipulation_index,
                "persona_type": score.persona_type,
                "tds": score.tds,
                "sbs": score.sbs,
                "ebs": score.ebs,
                "vos": score.vos,
                "sms": score.sms,
                "uas": score.uas,
                "brs": score.brs
            },
            "report": report.report_data if report else None,
            "contents": {
                "watch_history": history_list,
                "top_channels": top_channels
            }
        }
    finally:
        db.close()
