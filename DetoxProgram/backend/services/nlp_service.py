import os
import sys

# KoNLPy Okt용 JAVA_HOME 및 DLL PATH 설정
java_home = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot"
os.environ["JAVA_HOME"] = java_home
os.environ["PATH"] = (
    os.path.join(java_home, "bin") + os.pathsep +
    os.path.join(java_home, "bin", "server") + os.pathsep +
    os.environ.get("PATH", "")
)

from collections import Counter
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Lazy-loaded Okt analyzer to avoid startup delay
_okt = None

def get_okt():
    global _okt
    if _okt is None:
        print("KoNLPy Okt 형태소 분석기 초기화 중...")
        old_cwd = os.getcwd()
        try:
            os.chdir(r"C:\Users\Administrator")
            from konlpy.tag import Okt
            _okt = Okt()
        finally:
            os.chdir(old_cwd)
    return _okt

CATEGORY_DICT = {
    '📈 경제/금융': ['주식', '투자', '금리', '부동산', '비트코인', '경제', '삼성전자', '배당금', '재테크', '달러', '매수', '코스피', '금융', '자산', '은행', '부자'],
    '💻 IT/테크': ['파이썬', '코딩', '개발', '스마트폰', '애플', '갤럭시', 'AI', '인공지능', '프로그래밍', '업데이트', '리뷰', '컴퓨터', '테크', '기술', '챗gpt'],
    '🎮 게임': ['롤', '배그', '스팀', '공략', '티어', '패치', '닌텐도', '플레이', '게임', '스킬', '메이플', '마인크래프트', '게이머'],
    '🔬 과학/지식': ['과학', '우주', '뇌', '물리', '역사', '심리', '불안', '상대성이론', '지식', '다큐', '수학', '인류', '지구', '생명'],
    '🍿 엔터/예능': ['무한도전', '유재석', '아이돌', '가수', '뮤비', '노래', '예능', '먹방', '드라마', '영화', '유머', '썰', '숏츠', '연예인'],
    '🏋️ 건강/운동': ['다이어트', '운동', '헬스', '단백질', '루틴', '근육', '영양제', '피트니스', '비타민', '러닝', '식단', '칼로리']
}

STOP_WORDS = ['정말', '진짜', '오늘', '저희', '여러분', '그냥', '가장', '지금', '생각', '사람', '우리', '영상', '구독', '좋아요', '이것', '저것', '그것', '때문', '정도', '이유', '소개', '방법', '시작', '영상', '하루', '이번', '이후', '요즘']

# 감정/자극성 분석을 위한 키워드 정의
UNSTABLE_WORDS = ['불안', '분노', '슬픔', '눈물', '우울', '절망', '충격', '짜증', '괴롭', '외롭', '공포', '무섭', '스트레스', '피해']
STIMULUS_WORDS = ['경악', '폭로', '사건', '사고', '싸움', '막장', '충격', '논란', '레전드', '소름', '유출', '비밀', '막말', '혐오', '욕설', '쓰레기', '저격']

def get_summary_transcript(video_id, front_mins=1.5, back_mins=1.0):
    """
    영상 ID를 받아 초반과 후반 분량의 자막만 추출하여 결합합니다.
    """
    if not video_id:
        return ""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['ko']).fetch()

        if not transcript:
            return ""

        last_entry = transcript[-1]
        total_duration = last_entry['start'] + last_entry['duration']

        front_seconds = front_mins * 60
        back_start_time = total_duration - (back_mins * 60)

        extracted_text = []
        for entry in transcript:
            start_time = entry['start']
            if start_time <= front_seconds or start_time >= back_start_time:
                clean_text = entry['text'].replace('\n', ' ')
                extracted_text.append(clean_text)

        return " ".join(extracted_text)
    except Exception as e:
        # 실시간 분석 중 자막이 없거나 API 실패 시 조용히 넘어감
        return ""

def extract_keywords(text, num_keywords=10):
    """
    텍스트에서 Okt 명사 분석 후 불용어를 제외한 상위 키워드와 빈도수를 반환합니다.
    """
    if not text:
        return []
    try:
        okt = get_okt()
        nouns = okt.nouns(text)
        
        valid_nouns = []
        for noun in nouns:
            if len(noun) >= 2 and noun not in STOP_WORDS:
                valid_nouns.append(noun)
                
        count = Counter(valid_nouns)
        return count.most_common(num_keywords)
    except Exception as e:
        print(f"Keyword extraction failed: {e}")
        return []

def classify_text_by_keywords(keywords):
    """
    추출된 키워드를 바탕으로 CATEGORY_DICT에 매칭해 가중치가 가장 높은 카테고리를 분류합니다.
    """
    if not keywords:
        return "❓ 기타/미분류"
        
    scores = {category: 0 for category in CATEGORY_DICT.keys()}
    
    for word, count in keywords:
        for category, dict_words in CATEGORY_DICT.items():
            if word in dict_words:
                scores[category] += count
                
    best_category = max(scores, key=scores.get)
    if scores[best_category] == 0:
        return "❓ 기타/미분류"
        
    return best_category

def analyze_sentiment_and_stimulus(text):
    """
    세션 혹은 전체 텍스트에 포함된 불안/분노 등 부정 감정 단어 및 자극성 단어를 파악하여
    안정성(EBS) 감점률 및 유해/자극 안전(SMS) 감점률을 반환합니다.
    """
    if not text:
        return 1.0, 1.0  # 기본값: 100% 안전/안정
        
    unstable_count = 0
    stimulus_count = 0
    
    for word in UNSTABLE_WORDS:
        unstable_count += text.count(word)
        
    for word in STIMULUS_WORDS:
        stimulus_count += text.count(word)
        
    # 점수 모델링 (출현당 10% 감점, 최소 0점)
    stability_factor = max(0.1, 1.0 - (unstable_count * 0.10))
    safety_factor = max(0.1, 1.0 - (stimulus_count * 0.12))
    
    return stability_factor, safety_factor
