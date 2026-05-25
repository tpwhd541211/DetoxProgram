import json
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List
from core.config import settings

# Gemini가 반환해야 할 정확한 JSON 구조(Schema)를 Pydantic으로 정의합니다.
class MissionItem(BaseModel):
    mission_type: str
    description: str
    success_condition: str

class ReportSchema(BaseModel):
    overall_summary: str
    axis_comments: List[str]
    key_findings: str
    recommendations: str
    caution_notes: str
    missions: List[MissionItem]

def generate_report_and_missions(scores, nlp_data_summary=""):
    """
    Gemini 2.5 Flash를 사용하여 분석 결과에 대한 코멘트와 디톡스 미션(역방향 쿼리 등)을 생성합니다.
    """
    if not settings.GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY가 없어 LLM 호출을 건너뜁니다.")
        return {
            "overall_summary": f"당신의 알고리즘 위험도는 {scores.get('manipulation_index', 72.0)}%로 다소 편향된 시청 습관을 보이고 있습니다.",
            "axis_comments": [
                f"주제 다양성(TDS)은 {scores.get('diversity', 38.0)}/100으로 특정 장르에 편중되어 있습니다.",
                f"출처 균형(SBS)은 {scores.get('stability', 76.0)}/100으로 비교적 다양한 채널을 시청하고 있습니다.",
                f"감정 균형(EBS)은 {scores.get('proactivity', 56.0)}/100으로 약간 자극적인 감정 톤의 소비가 있습니다.",
                f"관점 개방성(VOS)은 {scores.get('openness', 41.0)}/100으로 새로운 관점을 수용할 여지가 큽니다."
            ],
            "key_findings": "최근 시청 기록에서 기술/IT 및 예능 영상 시청 비중이 70% 이상을 차지하여 필터 버블 발생 가능성이 높습니다.",
            "recommendations": "알고리즘 추천 영상 시청 비중을 줄이고 직접 검색(UAS 향상)을 통한 반대 성향 및 새로운 주제 탐색을 권장합니다.",
            "caution_notes": "편향된 콘텐츠 소비 습관이 지속되면 정보 고립 및 확증 편향이 강화될 위험이 있으므로 정기적인 디톡스가 필요합니다.",
            "missions": [
                {"mission_type": "역방향 쿼리", "description": "인공지능 윤리 및 일자리 대체 관련 비판적 영상을 1개 시청해보세요.", "success_condition": "비판적 논조의 테크 영상 10분 이상 시청 완료"},
                {"mission_type": "출처 다양화", "description": "평소 보지 않던 새로운 관점을 다루는 신규 미디어 채널 1곳을 구독해보세요.", "success_condition": "새로운 주제 채널 영상 시청 및 구독"},
                {"mission_type": "주도적 탐색", "description": "홈 화면 추천 대신 직접 검색어로 검색하여 원하는 지식 다큐멘터리를 찾아보세요.", "success_condition": "다큐멘터리 검색 후 시청"}
            ]
        }

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    prompt = f"""
    사용자의 유튜브 시청 기록 분석 결과입니다. 이 데이터를 바탕으로 사용자에게 충격 요법(거울 치료)과 
    건강한 디톡스 미션을 제공하는 리포트를 작성해주세요. 
    
    [분석 점수]
    - 다양성: {scores['diversity']}/100
    - 안정성: {scores['stability']}/100
    - 주도성: {scores['proactivity']}/100
    - 개방성: {scores['openness']}/100
    - 조종 지수(위험도): {scores['manipulation_index']}/100
    - 사용자 페르소나: {scores['persona_type']}
    
    [요구사항]
    1. overall_summary: 사용자의 현재 시청 습관에 대한 직관적이고 뼈때리는 요약.
    2. axis_comments: 4가지 차원과 조종 지수에 대한 짤막한 코멘트 배열.
    3. missions: 추천하는 알고리즘 디톡스 미션(역방향 쿼리 검색 등) 3가지.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ReportSchema,
                temperature=0.7
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"LLM Generation failed: {e}")
        return {"error": str(e)}
