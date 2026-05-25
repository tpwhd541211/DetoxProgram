import sys
import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# 백엔드 모듈을 가져오기 위해 경로 추가
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(backend_path)

from services.parser_service import process_and_normalize
from services.session_service import group_into_sessions
from services.scoring_service import calculate_detox_score
# 유튜브 API와 LLM은 프로토타입에서 속도를 위해 가짜 데이터로 대체하거나 생략합니다.

app = FastAPI(title="임시 프로토타입 서버")

# 프론트엔드 정적 파일 서빙
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend_vanilla'))
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join(frontend_path, "index.html"), "r", encoding="utf-8") as f:
        html_content = f.read()
    # 경로 보정 (style.css, app.js -> /static/...)
    html_content = html_content.replace('href="style.css"', 'href="/static/style.css"')
    html_content = html_content.replace('src="app.js"', 'src="/static/app.js"')
    return html_content

@app.post("/api/upload")
async def upload_for_prototype(file: UploadFile = File(...)):
    """
    프로토타입용 동기화 API. 파일을 받아서 백엔드 파이프라인의 핵심(파싱, 세션, 연산)을
    즉시 실행하고 결과를 반환합니다.
    """
    try:
        content = await file.read()
        
        # 1. 실제 백엔드 로직: 파싱 및 5초 스킵 필터링
        normalized_events = process_and_normalize(content, file.filename)
        
        # 2. 실제 백엔드 로직: 세션 묶음
        sessions = group_into_sessions(normalized_events)
        
        # 3. 실제 백엔드 로직: 점수 계산
        scores = calculate_detox_score(sessions)
        
        # 4. 임시 LLM 결과 (API 키 없이 테스트 가능하도록 하드코딩)
        mock_report = {
            "summary": "AI가 분석한 결과, 알고리즘이 추천하는 특정 주제의 영상만 시청하는 경향이 매우 강합니다. " + 
                       f"(분석된 총 영상 수: {len(normalized_events)}개, 세션 수: {len(sessions)}개)",
            "missions": [
                {
                    "type": "역방향 쿼리",
                    "desc": "평소 전혀 보지 않던 새로운 주제(예: 다큐멘터리, 과학)를 직접 검색해보세요.",
                    "cond": "새로운 주제의 영상 3개 끝까지 시청"
                },
                {
                    "type": "주도성 회복",
                    "desc": "유튜브 메인화면(추천)을 통하지 않고 오직 검색을 통해서만 영상을 시청하세요.",
                    "cond": "3일 동안 검색 시청 비율 80% 달성"
                }
            ]
        }
        
        return {
            "scores": scores,
            "report": mock_report
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/realtime")
async def get_realtime_data():
    """오늘 하루(가상)의 실시간 도파민 수치 추이 데이터 반환"""
    return {
        "today_trend": [
            {"time": "09:00", "dopamine": 40},
            {"time": "12:00", "dopamine": 65},
            {"time": "15:00", "dopamine": 85},
            {"time": "18:00", "dopamine": 92},
            {"time": "21:00", "dopamine": 70},
            {"time": "Now", "dopamine": 45}
        ],
        "current_status": "위험 구역 이탈 중",
        "current_video": "자연 다큐멘터리 (긍정적 영향)"
    }

@app.get("/api/persona")
async def get_persona_data():
    """과거 대비 심층 성향 변화 분석 데이터 반환"""
    return {
        "type": "DSPO",
        "title": "능동적 탐험가형",
        "weakness": "다양한 주제를 능동적으로 탐색하지만, 한 분야에 깊게 몰입하지 못할 수 있습니다.",
        "ai_scores": { "div": 75, "sta": 80, "ini": 85, "ope": 70 },
        "history": [
            {"month": "1월", "objectivity": 70},
            {"month": "3월", "objectivity": 65},
            {"month": "5월", "objectivity": 78}
        ]
    }

@app.get("/api/graph")
async def get_graph_data():
    """심층 지식 네트워크 노드 및 엣지 데이터 반환"""
    return {
        "nodes": [
            {"id": 1, "label": '인공지능', "group": 'tech', "value": 30},
            {"id": 2, "label": '기술/IT', "group": 'tech', "value": 25},
            {"id": 3, "label": '경제/금융', "group": 'economy', "value": 20},
            {"id": 4, "label": '딥러닝', "group": 'tech', "value": 15},
            {"id": 5, "label": '챗GPT', "group": 'tech', "value": 15},
            {"id": 6, "label": '예술/디자인', "group": 'art', "value": 5}, # 편향을 깨기 위한 추천 노드
        ],
        "edges": [
            {"from": 1, "to": 4}, {"from": 1, "to": 5}, {"from": 1, "to": 2},
            {"from": 2, "to": 3}
        ]
    }

@app.get("/api/guide")
async def get_guide_data():
    """디톡스 미션 달성 기록 및 연속 달성(Streak) 데이터 반환"""
    return {
        "streak_days": 12,
        "daily_missions": [
            {"id": 1, "task": "[탐색 확장] 평소에 보지 않던 예술 카테고리 영상 시청", "completed": True},
            {"id": 2, "task": "[출처 전환] 구독하지 않은 새로운 채널에서 정보 습득", "completed": True},
            {"id": 3, "task": "[관점 전환] 알고리즘 추천 대신 직접 검색해서 시청", "completed": False}
        ],
        "streak_history": [
            "2026-05-10", "2026-05-11", "2026-05-12", "2026-05-13", 
            "2026-05-14", "2026-05-15", "2026-05-16", "2026-05-17"
        ] # 잔디 심기용 날짜 데이터
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
