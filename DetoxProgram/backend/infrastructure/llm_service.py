import json
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List
from core.config import settings

class MissionItem(BaseModel):
    mission_type: str
    description: str
    success_condition: str
    suggested_query: str

class ReportSchema(BaseModel):
    overall_summary: str
    axis_comments: List[str]
    key_findings: str
    recommendations: str
    caution_notes: str
    missions: List[MissionItem]

def generate_fallback_report(scores):
    tds = scores.get("tds", 50.0)
    sbs = scores.get("sbs", 50.0)
    ebs = scores.get("ebs", 50.0)
    vos = scores.get("vos", 50.0)
    sms = scores.get("sms", 50.0)
    uas = scores.get("uas", 50.0)
    brs = scores.get("brs", 50.0)
    persona = scores.get("persona_type", "DNSF")
    
    overall_summary = f"당신의 알고리즘 편향 위험도(BRS)는 {brs}%로, {persona} 유형에 속합니다. 특정 주제 및 채널에 고착된 시청 습관의 개선이 필요합니다."
    
    axis_comments = [
        f"주제 다양성(TDS): {tds}/100 - 특정 분야에 편향되지 않은 탐색 습관이 중요합니다.",
        f"출처 균형(SBS): {sbs}/100 - 소수 채널의 반복 시청으로 인한 정보 왜곡 가능성을 보여줍니다.",
        f"감정 균형(EBS): {ebs}/100 - 감정적으로 치우친 논조의 시청 비중을 조절해야 합니다.",
        f"관점 개방성(VOS): {vos}/100 - 다른 시각을 지닌 콘텐츠를 의도적으로 노출시킬 필요가 있습니다.",
        f"유해 안전(SMS): {sms}/100 - 도파민 분비를 강하게 유도하는 고자극성 자극물을 완화해야 합니다.",
        f"사용자 주도성(UAS): {uas}/100 - 홈 피드 추천에 수동적으로 끌려가기보다 검색창을 적극 활용해보세요."
    ]
    
    key_findings = "유튜브 추천 알고리즘의 무한 루프에 갇혀 특정 크리에이터의 논리를 비판 없이 학습하고 있는 패턴이 관찰됩니다."
    recommendations = "매일 아침 1회, 평소와 전혀 다른 카테고리의 채널을 키워드로 직접 검색하여 10분 이상 시청하는 '역방향 탐색' 루틴을 시도하십시오."
    caution_notes = "이러한 고착된 알고리즘 소비 습관이 계속되면 생각의 틀이 좁아지는 '필터 버블' 현상이 강화될 수 있습니다."
    
    # Ground missions on the top 3 weakest dimensions
    dimensions = [
        ("tds", tds, "역방향 쿼리", "평소 관심사와 반대되거나 낯선 분야의 지식 교양 콘텐츠 검색 후 시청", "직접 검색한 다큐멘터리/역사 영상 10분 시청 완료", "기후 변화 다큐멘터리"),
        ("sbs", sbs, "출처 전환", "반복 시청하던 메인 채널 대신 새로운 뉴스룸/인물 인터뷰 채널 시청", "신규 1차 출처 채널 콘텐츠 시청 완료", "글로벌 경제 심층 인터뷰"),
        ("ebs", ebs, "감정 균형", "자극적인 이슈에서 벗어나 평온하고 객관적인 힐링 교양 콘텐츠 시청", "차분한 힐링/교양 영상 시청 완료", "클래식 음악 15분"),
        ("vos", vos, "관점 개방", "확증 편향 예방을 위해 반대 시각을 가진 채널 혹은 다각적 분석 영상 시청", "다른 관점의 해설 영상 시청 완료", "지식의 객관성 비교 분석"),
        ("sms", sms, "숏폼 탈출", "말초적인 도파민을 끊어내기 위해 유튜브 쇼츠 대신 10분 이상의 긴 영상 시청", "10분 이상 롱폼 영상 시청 완료", "집중력을 올리는 10가지 방법"),
        ("uas", uas, "주도성 회복", "알고리즘 추천 피드에 의존하지 않고, 직접 관심 있는 분야를 검색해 시청", "추천 피드 대신 직접 검색 시청 완료", "내가 진짜 알고싶은 취미")
    ]
    sorted_dims = sorted(dimensions, key=lambda x: x[1])
    weak_dims = sorted_dims[:3]
    
    missions = []
    for code, score_val, m_type, desc, succ, query in weak_dims:
        missions.append({
            "mission_type": m_type,
            "description": desc,
            "success_condition": succ,
            "suggested_query": query
        })
        
    return {
        "overall_summary": overall_summary,
        "axis_comments": axis_comments,
        "key_findings": key_findings,
        "recommendations": recommendations,
        "caution_notes": caution_notes,
        "missions": missions
    }

def generate_report_and_missions(scores, nlp_data_summary=""):
    """
    Calls Gemini 2.5 Flash API with a schema to get structured analysis,
    falling back cleanly if the API fails or is not configured.
    """
    if not settings.GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY가 없어 Fallback 리포트를 생성합니다.")
        return generate_fallback_report(scores)

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Calculate weak dimensions to pass to the LLM
        dimensions = [
            ("주제 다양성(TDS)", scores.get("tds", 50.0)),
            ("출처 균형(SBS)", scores.get("sbs", 50.0)),
            ("감정 균형(EBS)", scores.get("ebs", 50.0)),
            ("관점 개방성(VOS)", scores.get("vos", 50.0)),
            ("유해/자극 안전(SMS)", scores.get("sms", 50.0)),
            ("사용자 주도성(UAS)", scores.get("uas", 50.0))
        ]
        sorted_dims = sorted(dimensions, key=lambda x: x[1])
        weak_names = [d[0] for d in sorted_dims[:3]]
        
        prompt = f"""
        사용자의 유튜브 시청 기록 분석 결과입니다. 이 데이터를 바탕으로 사용자에게 충격 요법(거울 치료)과 
        건강한 디톡스 미션을 제공하는 리포트를 작성해주세요. 
        
        [분석 점수 (6축)]
        - 주제 다양성(TDS): {scores['tds']}/100
        - 출처 균형(SBS): {scores['sbs']}/100
        - 감정 균형(EBS): {scores['ebs']}/100
        - 관점 개방성(VOS): {scores['vos']}/100
        - 유해/자극 안전(SMS): {scores['sms']}/100
        - 사용자 주도성(UAS): {scores['uas']}/100
        - 종합 편향 위험도(BRS): {scores['brs']}/100
        - 사용자 페르소나: {scores['persona_type']}
        
        [가장 취약한 3대 지표]
        {', '.join(weak_names)}
        
        [요구사항]
        1. overall_summary: 사용자의 현재 시청 습관에 대한 직관적이고 뼈때리는 요약.
        2. axis_comments: 6가지 차원과 편향 위험도에 대한 짤막한 코멘트 배열(정확히 6개 요소를 채워주세요).
        3. missions: 추천하는 알고리즘 디톡스 미션 3가지. 
           반드시 가장 취약한 3대 지표({', '.join(weak_names)}) 각각에 1:1로 대응되는 맞춤형 미션을 3개 설계해주세요.
           각 미션에는 사용자가 유튜브에 직접 검색해볼 만한 구체적이고 구미가 당기는 검색어(suggested_query)를 반드시 포함하세요 (예: '도파민 디톡스 원리', '우주 다큐멘터리').
        """
        
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
        print(f"LLM Generation failed: {e}. Falling back to structured default template.")
        return generate_fallback_report(scores)


# In-memory cache for dynamic keyword classifications to prevent redundant Gemini API calls
_keyword_classification_cache = {}

def classify_topics_batch(topics: List[str]) -> dict:
    """
    Classifies a list of topics into one of the 20 pre-defined categories using Gemini.
    Utilizes an in-memory cache to prevent repetitive network requests.
    """
    global _keyword_classification_cache
    
    if not topics:
        return {}
        
    # Filter out topics that are already cached
    uncached_topics = [t for t in topics if t not in _keyword_classification_cache]
    if not uncached_topics:
        return {t: _keyword_classification_cache[t] for t in topics}
        
    if not settings.GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY is not configured. Cannot perform dynamic LLM categorization.")
        return {t: _keyword_classification_cache.get(t, "❓ 기타/미분류") for t in topics}

    categories = [
        "📈 경제/금융", "💻 IT/테크", "🎮 게임", "🔬 과학/지식", "🍿 엔터/예능",
        "🏋️ 건강/운동", "🛠️ 취미/일상", "⚖️ 뉴스/정치/사회", "🎤 연예/아이돌", "🎵 음악",
        "🍳 먹방/요리", "💄 뷰티/패션", "🚗 자동차", "🏠 부동산", "🌱 자기계발",
        "📖 공부/입시", "📦 리뷰/언박싱", "🎬 애니/웹툰", "⚽ 스포츠", "🛒 쇼핑/소비"
    ]
    
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        prompt = f"""
        당신은 오직 단어의 분류만 담당하는 기계적인 분류기입니다.
        주어진 단어(Topic) 리스트를 아래 20가지 관심사 카테고리 중 가장 적합한 하나로 매핑하여 JSON 형태로 응답해 주세요.
        
        [카테고리 목록]
        {', '.join(categories)}
        
        [주의사항]
        - 반드시 위의 20가지 목록에 있는 카테고리명 중 하나로만 매핑해야 하며, 임의의 다른 문자나 이모지를 덧붙이거나 누락하지 마세요. (예: "티원" -> "🎮 게임")
        - 만약 도저히 분류할 수 없는 단어거나 사람 이름 등 일반적인 관심사 범주에 포함되기 힘든 단어라면 "❓ 기타/미분류"로 매핑하십시오.
        - 응답은 오직 단어와 카테고리의 1:1 매핑을 나타내는 JSON 객체여야 합니다. 예시:
          {{"티원": "🎮 게임", "트럼프": "⚖️ 뉴스/정치/사회", "funny": "🍿 엔터/예능"}}
        
        [분류할 단어 리스트]
        {json.dumps(uncached_topics, ensure_ascii=False)}
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        
        raw_res = json.loads(response.text)
        if isinstance(raw_res, dict):
            for k, v in raw_res.items():
                if v in categories or v == "❓ 기타/미분류":
                    _keyword_classification_cache[k] = v
                else:
                    # Clean response or fallback
                    _keyword_classification_cache[k] = "❓ 기타/미분류"
                    
        # Fill in any missing keys in the response just in case
        for t in uncached_topics:
            if t not in _keyword_classification_cache:
                _keyword_classification_cache[t] = "❓ 기타/미분류"
                
    except Exception as e:
        print(f"Failed to batch classify topics with Gemini: {e}")
        for t in uncached_topics:
            if t not in _keyword_classification_cache:
                _keyword_classification_cache[t] = "❓ 기타/미분류"
                
    return {t: _keyword_classification_cache.get(t, "❓ 기타/미분류") for t in topics}

