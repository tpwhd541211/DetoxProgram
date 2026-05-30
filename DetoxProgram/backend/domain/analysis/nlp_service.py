# -*- coding: utf-8 -*-
import os
import sys
import re
import unicodedata
from collections import Counter
from youtube_transcript_api import YouTubeTranscriptApi
from google.cloud import language_v2

# Expanded Category Dictionary containing Korean and English keywords
CATEGORY_DICT = {
    '📈 경제/금융': ['주식', '투자', '금리', '부동산', '비트코인', '경제', '삼성전자', '배당금', '재테크', '달러', '매수', '코스피', '금융', '자산', '은행', '부자', '재정', '재무', '환율', '나스닥', '코인', '매도', '펀드', '채권', '자본', '소득', '소비', '금융업', '경영', '마케팅', '비즈니스', '상장', '공매도', '계좌', '자산관리', '신용', '환전'],
    '💻 IT/테크': ['파이썬', '코딩', '개발', '스마트폰', '애플', '갤럭시', 'AI', '인공지능', '프로그래밍', '업데이트', '리뷰', '컴퓨터', '테크', '기술', '챗gpt', 'technology', 'programming', 'software', '반도체', '챗봇', '딥러닝', '머신러닝', '알고리즘', '디바이스', '윈도우', '서버', '클라우드', '자바', '맥북', '노트북', '아이폰', '아이패드', '소프트웨어', '하드웨어', '리눅스', '깃허브', '웹개발', '앱개발', '프로그래머', '엔지니어'],
    '🎮 게임': ['롤', '배그', '스팀', '공략', '티어', '패치', '닌텐도', '플레이', '게임', '스킬', '메이플', '마인크래프트', '게이머', 'game', 'playstation', 'xbox', '스위치', '모바일게임', '오버워치', 'RPG', 'fps', 'e스포츠', '클래시', '메타', '리그오브레전드', '로스트아크', '발로란트', '던파', '피파', '레이드', '스킨', '공략법', '클리어', '게임방', '오락'],
    '🔬 과학/지식': ['과학', '우주', '뇌', '물리', '역사', '심리', '지식', '다큐', '수학', '인류', '지구', '생명', 'science', 'history', 'physics', 'math', '생물', '화학', '철학', '진화', '행성', '은하', '다큐멘터리', '교육', '강의', '인문학', '뇌과학', '양자역학', '아인슈타인', '인류학', '진화론', '고고학', '천문학', '연구', '논문', '교양'],
    '🍿 엔터/예능': ['무한도전', '유재석', '아이돌', '가수', '뮤비', '노래', '예능', '먹방', '드라마', '영화', '유머', '썰', '숏츠', '연예인', 'kpop', 'entertainment', 'movie', 'show', '콘서트', '방송', '웃긴', '웹드라마', '영화리뷰', '음악', '댄스', '개그', '코미디', '가십', '루머', '시상식', '팬미팅', '유튜버', '틱톡', '리액션'],
    '🏋️ 건강/운동': ['다이어트', '운동', '헬스', '단백질', '루틴', '근육', '영양제', '피트니스', '비타민', '러닝', '식단', '칼로리', 'sports', 'run', 'health', 'fitness', '축구', '야구', '농구', '클라이밍', '스트레칭', '재활', '건강검진', '필라테스', '요가', '홈트', '웨이트', '단백질쉐이크', '보충제'],
    '🛠️ 취미/일상': ['woodworking', 'diyprojects', 'tips', 'diy', '만들기', '셀프', '가구', '목공', '꿀팁', '요리', '레시피', '일상', 'vlog', '브이로그', 'hobby', 'cooking', '여행', '캠핑', '맛집', '카페', '인테리어', '원예', '패션', '코디', '드로잉', '브이로그', '강아지', '고양이', '반려동물', '일상글', '휴가', '호캉스', '관광', '식물'],
    '⚖️ 뉴스/정치/사회': ['정치', '사회', '뉴스', '선거', '대통령', '국회', '시사', '사건', '사고', '검찰', '법원', '경찰', '외교', '북한', '이슈', '현안', '논란', '비판', '단독', '보도', '속보', '언론', '취재', '정부', '국민', '여당', '야당', '재판', '범죄', '법률', '시민', '국제사회', '전쟁', '갈등'],
    '🎤 연예/아이돌': ['연예', '아이돌', '연예인', '배우', '가수', 'bts', '방탄', '블랙핑크', '뉴진스', '에스파', '제니', '민희진', '하이브', 'SM', 'YG', 'JYP', '기획사', '콘서트', '팬미팅', '덕질', '드라마', '영화', '캐스팅', '시상식', '열애', '결별', '예능', '가십', '루머', '걸그룹', '보이그룹', '팬클럽', '컴백', '티저'],
    '🎵 음악': ['음악', '노래', '뮤직', '커버', '플레이리스트', '노래방', '라이브', 'ost', '뮤비', 'mv', '곡', '작곡', '작사', '피아노', '기타', '밴드', '보컬', '클래식', '재즈', '힙합', '발라드', '댄스', '음반', '노래방', '송', '멜로디', '연주', '악기', '바이올린', '음원', '차트'],
    '🍳 먹방/요리': ['먹방', '요리', '레시피', '맛집', 'ASMR', '쿡방', '베이킹', '디저트', '음식', '식사', '레스토랑', '카페', '푸드', '반찬', '찌개', '김치', '삼겹살', '라면', '치킨', '피자', '한식', '일식', '중식', '양식', '요리법', '간식', '베이커리', '베이킹', '맛집탐방', '식재료', '메뉴'],
    '💄 뷰티/패션': ['패션', '코디', '스타일', '옷', '쇼핑', '룩북', '하울', '화장', '메이크업', '스킨케어', '뷰티', '피부', '헤어', '미용', '네일', '향수', '트렌드', '아웃핏', '데일리룩', '원피스', '바지', '셔츠', '가방', '구두', '화장품', '립스틱', '파운데이션', '뷰티템'],
    '🚗 자동차': ['자동차', '시승기', '차', '휠', '시승', '내비게이션', '전기차', '하이브리드', '세단', 'suv', '모터쇼', '튜닝', '타이어', '현대차', '기아', '테슬라', 'bmw', '벤츠', '아우디', '주행', '급발진', '블랙박스', '블박', '사고영상', '운전', '배터리', '수입차', '중고차', '차량', '엔진'],
    '🏠 부동산': ['부동산', '아파트', '청약', '분양', '매매', '전세', '월세', '임대', '재개발', '재건축', '경매', '토지', '빌라', '상가', '임장', '집값', '호재', '악재', '갭투자', '신도시', '다주택', '내집마련', '시세', '분양가', '오피스텔', '상권'],
    '🌱 자기계발': ['동기부여', '자기계발', '성공', '독서', '습관', '성장', '멘토', '강연', '시간관리', '생산성', '도전', '마인드셋', '인생', '교훈', '조언', '성찰', '계획', '목표', '실천', '루틴', '끈기', '의지', '자기계발서', '책추천', '명언', '자극', '발전', '지혜', '시간표'],
    '📖 공부/입시': ['공부', '입시', '수능', '학습', '시험', '내신', '공시', '공무원', '토익', '영어', '수학', '국어', '과학', '역사', '인강', '강의', '문제집', '독서실', '스터디', '합격', '과외', '대학', '학원', '고3', '재수', '모의고사', '성적', '공부법', '열공', '스터디윗미'],
    '📦 리뷰/언박싱': ['리뷰', '언박싱', '내돈내산', '후기', '개봉기', '추천템', '비교', '솔직', '사용기', '구매', '제품', '가전', '스마트폰', '맥북', '노트북', '아이패드', '아이폰', '갤럭시', '다이소템', '꿀템', '실제후기', '장단점', '구매가이드', '추천제품'],
    '🎬 애니/웹툰': ['애니', '웹툰', '만화', '극장판', '원피스', '나루토', '귀멸', '주술회전', '일러스트', '스토리', '결말', '요약', '더빙', '코스프레', '피규어', '덕후', '오타쿠', '캐릭터', '네이버웹툰', '카카오페이지', '애니메이션', '성우', '원작', '단행본'],
    '⚽ 스포츠': ['스포츠', '축구', '야구', '농구', '배구', '골프', '테니스', '수영', '헬스', '피트니스', '손흥민', '이강인', 'epl', '챔스', 'k리그', 'kbo', '메이저리그', 'mlb', '올림픽', '경기', '하이라이트', '분석', '득점', '골인', '홈런', '경기결과', '국가대표'],
    '🛒 쇼핑/소비': ['쇼핑', '소비', '가성비', '다이소', '올리브영', '마트', '시장', '쿠팡', '추천템', '득템', '세일', '할인', '직구', '해외직구', '하울', '신상', '장보기', '언박싱', '내돈내산', '위시리스트', '코스트코', '이마트', '백화점', '소비일기', '지름신']
}

STOP_WORDS = [
    '정말', '진짜', '오늘', '저희', '여러분', '그냥', '가장', '지금', '생각', '사람', '우리', '영상', '구독', '좋아요', '이것', '저것', '그것', '때문', '정도', '이유', '소개', '방법', '시작', '하루', '이번', '이후', '요즘',
    '채널', '구독자', '조회수', '공식', '티저', '예고편', '다시보기', '비하인드', '풀버전', '정주행', '모음집', '모음', '추천', '설명', '링크', '사이트', '더보기', '댓글', '커뮤니티', '유튜브',
    'youtube', 'channel', 'video', 'subscribe', 'official', 'teaser', 'trailer', 'playlist', 'upload', 'watch', 'clip', 'full', 'part', 'episode', 'ep',
    '쇼츠', 'shorts', '조회', '이슈', '요약', '뉴스', '시청', '소식', '정보', '클립', '이야기', '내용', '기록', '최근', '리뷰', '꿀팁', '팁', '전체', '재생', '시청자', '비교', '정리', '랭킹', '순위', '인기', '반응', '특징', '분석', '상황', '체험', '소감',
    '질문', '답변', '해결', '방법', '원인', '문제', '이유', '결과', '사실', '진실', '비밀', '공개', '최초', '충격', '눈물', '웃음', '감동', '레전드', '소름', '드디어', '과연', '진짜로', '어떻게', '무슨', '무엇', '왜', '어디', '언제', '누가', '대해', '대한'
]
UNSTABLE_WORDS = ['불안', '분노', '슬픔', '눈물', '우울', '절망', '충격', '짜증', '괴롭', '외롭', '공포', '무섭', '스트레스', '피해']
STIMULUS_WORDS = ['경악', '폭로', '사건', '사고', '싸움', '막장', '충격', '논란', '레전드', '소름', '유출', '비밀', '막말', '혐오', '욕설', '쓰레기', '저격']

DATE_PATTERN = re.compile(r'^\d{1,4}[-./]\d{1,2}([-./]\d{1,4})?$')
ALLOWED_2LETTER_ENG = {"AI", "IT", "UI", "UX", "VR", "AR", "IP", "DB", "PC", "OS", "VS", "ML", "DL"}

def clean_and_filter_keyword(word: str) -> str:
    if not word:
        return ""
    word_clean = word.strip(" \t\n\r#?![](),. \"'_-|~*+:;/\\&@<>{}")
    if len(word_clean) <= 1:
        return ""
    if "=" in word_clean:
        return ""
    if re.match(r'^[a-zA-Z0-9_-]{11}$', word_clean):
        if not (word_clean.isalpha() and word_clean.islower()):
            return ""
    if any(char in word_clean for char in ["-", "|", ":", "/", "\\"]):
        return ""
    if len(word_clean.split()) >= 3:
        return ""
    if len(word_clean) > 20:
        return ""
    if len(word_clean) >= 3:
        particles = ['은', '는', '이', '가', '을', '를', '의', '에', '도', '만', '과', '와', '로', '으로']
        for p in particles:
            if word_clean.endswith(p):
                stem = word_clean[:-len(p)]
                if all(ord('가') <= ord(c) <= ord('힣') for c in stem):
                    word_clean = stem
                    break
    if len(word_clean) <= 1:
        return ""
    if DATE_PATTERN.match(word_clean):
        return ""
    if word_clean.isdigit():
        return ""
    try:
        float(word_clean)
        return ""
    except ValueError:
        pass
    word_lower = word_clean.lower()
    if any(domain in word_lower for domain in [".com", ".net", ".org", "http", "www", "youtube", "co.kr"]):
        return ""
    if len(word_clean) == 2 and word_clean.isalpha() and word_clean.isascii():
        if word_clean.upper() not in ALLOWED_2LETTER_ENG:
            return ""
    if word_clean in STOP_WORDS or word_lower in STOP_WORDS:
        return ""
    if re.match(r'^\d+[화회부편탄분초]$', word_clean):
        return ""
    return word_clean

_okt = None

def get_okt():
    global _okt
    if _okt is None:
        try:
            import ctypes
            def get_short_path(long_path):
                try:
                    buf = ctypes.create_unicode_buffer(1024)
                    ctypes.windll.kernel32.GetShortPathNameW(long_path, buf, 1024)
                    return buf.value if buf.value else long_path
                except Exception:
                    return long_path
            new_paths = []
            for p in sys.path:
                if " " in p:
                    new_paths.append(get_short_path(p))
                else:
                    new_paths.append(p)
            sys.path = new_paths
            java_home = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot"
            if os.path.exists(java_home):
                short_java = get_short_path(java_home)
                os.environ["JAVA_HOME"] = short_java
                os.environ["PATH"] = (
                    os.path.join(short_java, "bin") + os.pathsep +
                    os.path.join(short_java, "bin", "server") + os.pathsep +
                    os.environ.get("PATH", "")
                )
            old_cwd = os.getcwd()
            try:
                os.chdir(r"C:\Users\Administrator")
                from konlpy.tag import Okt
                _okt = Okt()
            finally:
                os.chdir(old_cwd)
        except Exception as e:
            print(f"KoNLPy fallback initialization failed: {e}")
    return _okt

def extract_keywords_fallback(text, num_keywords=10):
    if not text:
        return []
    try:
        okt = get_okt()
        if okt is None:
            raw_words = text.split()
            valid_words = []
            for w in raw_words:
                cleaned = clean_and_filter_keyword(w)
                if cleaned:
                    valid_words.append(cleaned)
            return Counter(valid_words).most_common(num_keywords)
        nouns = okt.nouns(text)
        valid_nouns = []
        for noun in nouns:
            cleaned = clean_and_filter_keyword(noun)
            if cleaned:
                valid_nouns.append(cleaned)
        count = Counter(valid_nouns)
        return count.most_common(num_keywords)
    except Exception as e:
        print(f"Fallback keyword extraction failed: {e}")
        return []

def classify_text_by_keywords(keywords):
    if not keywords:
        return "❓ 기타/미분류"
    scores = {category: 0.0 for category in CATEGORY_DICT.keys()}
    for word, count in keywords:
        word_lower = word.lower()
        for category, dict_words in CATEGORY_DICT.items():
            for dw in dict_words:
                if dw.lower() in word_lower:
                    scores[category] += count
    best_category = max(scores, key=scores.get)
    if scores[best_category] < 0.1:
        return "❓ 기타/미분류"
    return best_category

def analyze_sentiment_and_stimulus_fallback(text):
    if not text:
        return 1.0, 1.0
    unstable_count = sum(text.count(word) for word in UNSTABLE_WORDS)
    stimulus_count = sum(text.count(word) for word in STIMULUS_WORDS)
    stability_factor = max(0.1, 1.0 - (unstable_count * 0.10))
    safety_factor = max(0.1, 1.0 - (stimulus_count * 0.12))
    return stability_factor, safety_factor

def map_gcp_category_to_local(gcp_cat):
    if not gcp_cat:
        return "❓ 기타/미분류"
    gcp_cat = gcp_cat.lower()
    if "games" in gcp_cat:
        return "🎮 게임"
    elif "finance" in gcp_cat or "business" in gcp_cat:
        return "📈 경제/금융"
    elif "real estate" in gcp_cat:
        return "🏠 부동산"
    elif "computer" in gcp_cat or "internet" in gcp_cat or "technology" in gcp_cat:
        return "💻 IT/테크"
    elif "science" in gcp_cat:
        return "🔬 과학/지식"
    elif "education" in gcp_cat or "reference" in gcp_cat or "books" in gcp_cat:
        return "📖 공부/입시"
    elif "health" in gcp_cat or "fitness" in gcp_cat:
        return "🏋️ 건강/운동"
    elif "sports" in gcp_cat:
        return "⚽ 스포츠"
    elif "music" in gcp_cat or "singing" in gcp_cat:
        return "🎵 음악"
    elif "autos" in gcp_cat or "vehicle" in gcp_cat:
        return "🚗 자동차"
    elif "beauty" in gcp_cat or "fashion" in gcp_cat:
        return "💄 뷰티/패션"
    elif "food" in gcp_cat or "cooking" in gcp_cat:
        return "🍳 먹방/요리"
    elif "news" in gcp_cat or "politics" in gcp_cat or "society" in gcp_cat:
        return "⚖️ 뉴스/정치/사회"
    elif "movie" in gcp_cat or "television" in gcp_cat or "entertainment" in gcp_cat:
        return "🍿 엔터/예능"
    elif "lifestyle" in gcp_cat or "hobbies" in gcp_cat or "pets" in gcp_cat:
        return "🛠️ 취미/일상"
    elif "shopping" in gcp_cat:
        return "🛒 쇼핑/소비"
    return "❓ 기타/미분류"

def get_summary_transcript(video_id, front_mins=1.5, back_mins=1.0):
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
        return ""

def analyze_text_with_gcp(text, language_hint="ko"):
    if not text or not text.strip():
        return None
    try:
        client = language_v2.LanguageServiceClient()
        document = language_v2.Document(
            content=text,
            type_=language_v2.Document.Type.PLAIN_TEXT
        )
        word_count = len(text.split())
        features = {
            "extract_entities": True,
            "extract_document_sentiment": True,
            "moderate_text": True,
            "classify_text": word_count >= 20
        }
        response = client.annotate_text(
            request={
                "document": document,
                "features": features
            }
        )
        res_dict = type(response).to_dict(response)
        sentiment_data = res_dict.get("document_sentiment", {})
        sentiment_score = sentiment_data.get("score", 0.0)
        sentiment_magnitude = sentiment_data.get("magnitude", 0.0)
        entities = [
            {"name": e.get("name"), "type": e.get("type"), "salience": e.get("salience", 0.0)}
            for e in res_dict.get("entities", [])
        ]
        categories = [
            {"name": c.get("name"), "confidence": c.get("confidence", 0.0)}
            for c in res_dict.get("categories", [])
        ]
        moderation_categories = [
            {"name": m.get("name"), "confidence": m.get("confidence", 0.0)}
            for m in res_dict.get("moderation_categories", [])
        ]
        return {
            "documentSentiment": {
                "score": sentiment_score,
                "magnitude": sentiment_magnitude
            },
            "entities": entities,
            "categories": categories,
            "moderationCategories": moderation_categories,
            "language_code": res_dict.get("language_code", "ko")
        }
    except Exception as e:
        print(f"GCP NLP API call failed: {e}")
        return None

def analyze_session_text(text):
    gcp_res = analyze_text_with_gcp(text)
    if gcp_res:
        entities = gcp_res["entities"]
        keywords = []
        for e in entities:
            name = e["name"]
            if e.get("type") in ["NUMBER", "PRICE", "DATE", "PHONE_NUMBER"]:
                continue
            cleaned = clean_and_filter_keyword(name)
            if not cleaned:
                continue
            keywords.append((cleaned, int(e["salience"] * 100)))
            if len(keywords) >= 10:
                break
        category = "❓ 기타/미분류"
        if gcp_res["categories"]:
            sorted_cats = sorted(gcp_res["categories"], key=lambda x: x["confidence"], reverse=True)
            category = map_gcp_category_to_local(sorted_cats[0]["name"])
        else:
            category = classify_text_by_keywords(keywords)
        score = gcp_res["documentSentiment"]["score"]
        stability_factor = max(0.1, 1.0 - max(0.0, -score) * 0.8)
        max_mod_confidence = 0.0
        bad_categories = ["Toxic", "Insult", "Profanity", "Violence", "Hate Speech", "Harassment", "Derogatory", "Sexual"]
        for cat in gcp_res["moderationCategories"]:
            if cat["name"] in bad_categories:
                max_mod_confidence = max(max_mod_confidence, cat["confidence"])
        safety_factor = max(0.1, 1.0 - max_mod_confidence * 1.2)
        return keywords, category, stability_factor, safety_factor, gcp_res
    else:
        keywords = extract_keywords_fallback(text)
        category = classify_text_by_keywords(keywords)
        stability_factor, safety_factor = analyze_sentiment_and_stimulus_fallback(text)
        return keywords, category, stability_factor, safety_factor, None

def extract_keywords(text, num_keywords=10):
    return extract_keywords_fallback(text, num_keywords)

def analyze_sentiment_and_stimulus(text):
    return analyze_sentiment_and_stimulus_fallback(text)

# --- Dynamic Category Multi-Source Classifier v2.0 ---

YOUTUBE_CATEGORY_MAP = {
    "1": "🎬 애니/웹툰",
    "2": "🚗 자동차",
    "10": "🎵 음악",
    "15": "🛠️ 취미/일상",
    "17": "⚽ 스포츠",
    "19": "🛠️ 취미/일상",
    "20": "🎮 게임",
    "22": "🛠️ 취미/일상",
    "23": "🍿 엔터/예능",
    "24": "🍿 엔터/예능",
    "25": "⚖️ 뉴스/정치/사회",
    "26": "💄 뷰티/패션",
    "27": "🔬 과학/지식",
    "28": "💻 IT/테크",
    "29": "⚖️ 뉴스/정치/사회"
}

def map_topic_category_url(url: str) -> str:
    url_lower = url.lower()
    if "gaming" in url_lower or "game" in url_lower:
        return "🎮 게임"
    elif "music" in url_lower or "singing" in url_lower or "song" in url_lower:
        return "🎵 음악"
    elif "sport" in url_lower or "football" in url_lower or "baseball" in url_lower or "basketball" in url_lower or "cricket" in url_lower:
        return "⚽ 스포츠"
    elif "politics" in url_lower or "society" in url_lower or "news" in url_lower or "social" in url_lower:
        return "⚖️ 뉴스/정치/사회"
    elif "technology" in url_lower or "computing" in url_lower or "software" in url_lower or "hardware" in url_lower:
        return "💻 IT/테크"
    elif "finance" in url_lower or "economics" in url_lower or "business" in url_lower:
        return "📈 경제/금융"
    elif "real_estate" in url_lower or "property" in url_lower:
        return "🏠 부동산"
    elif "automotive" in url_lower or "car" in url_lower or "vehicle" in url_lower:
        return "🚗 자동차"
    elif "fashion" in url_lower or "beauty" in url_lower or "cosmetics" in url_lower or "clothing" in url_lower:
        return "💄 뷰티/패션"
    elif "food" in url_lower or "cooking" in url_lower or "recipe" in url_lower or "cuisine" in url_lower:
        return "🍳 먹방/요리"
    elif "entertainment" in url_lower or "variety" in url_lower or "television" in url_lower or "comedy" in url_lower or "humor" in url_lower:
        return "🍿 엔터/예능"
    elif "science" in url_lower or "education" in url_lower or "history" in url_lower or "philosophy" in url_lower or "academic" in url_lower:
        return "🔬 과학/지식"
    elif "lifestyle" in url_lower or "hobby" in url_lower or "pet" in url_lower or "animal" in url_lower or "travel" in url_lower:
        return "🛠️ 취미/일상"
    return None

def classify_session_advanced(events, session_text):
    tags = []
    topic_categories = []
    category_ids = []
    channel_names = []
    titles = []
    
    for ev in events:
        if ev.get("event_type") == "watch":
            if ev.get("tags"):
                tags.extend(ev["tags"])
            if ev.get("topicCategories"):
                topic_categories.extend(ev["topicCategories"])
            if ev.get("categoryId"):
                category_ids.append(str(ev["categoryId"]))
            if ev.get("channel_name"):
                channel_names.append(ev["channel_name"])
            if ev.get("title"):
                titles.append(ev["title"])
                
    tags = [unicodedata.normalize('NFC', str(t)) for t in tags]
    topic_categories = [unicodedata.normalize('NFC', str(tc)) for tc in topic_categories]
    category_ids = [unicodedata.normalize('NFC', str(cid)) for cid in category_ids]
    channel_names = [unicodedata.normalize('NFC', str(cn)) for cn in channel_names]
    titles = [unicodedata.normalize('NFC', str(t)) for t in titles]
    session_text = unicodedata.normalize('NFC', session_text)
    
    candidates = {}
    
    def add_score(cat_name, amount):
        candidates[cat_name] = candidates.get(cat_name, 0.0) + amount

    # Step 1: YouTube categoryId
    for cid in category_ids:
        mapped = YOUTUBE_CATEGORY_MAP.get(cid)
        if mapped:
            add_score(mapped, 3.0)
            
    # Step 2: YouTube topicCategories
    for url in topic_categories:
        mapped = map_topic_category_url(url)
        if mapped:
            add_score(mapped, 2.5)
            
    # Step 3: YouTube tags matching against CATEGORY_DICT
    for tag in tags:
        tag_lower = tag.lower()
        for cat, dict_words in CATEGORY_DICT.items():
            for dw in dict_words:
                if dw.lower() in tag_lower:
                    add_score(cat, 0.8)
                    
    # Step 4: Video title keywords matching against CATEGORY_DICT
    keywords = extract_keywords_fallback(session_text, num_keywords=15)
    for word, count in keywords:
        word_lower = word.lower()
        for cat, dict_words in CATEGORY_DICT.items():
            for dw in dict_words:
                if dw.lower() in word_lower:
                    add_score(cat, 0.5 * count)
                    
    # Step 5: Channel names matching against CATEGORY_DICT
    for cn in channel_names:
        cn_lower = cn.lower()
        for cat, dict_words in CATEGORY_DICT.items():
            for dw in dict_words:
                if dw.lower() in cn_lower:
                    add_score(cat, 0.6)

    sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    
    if sorted_candidates and sorted_candidates[0][1] > 0.1:
        best_cat = sorted_candidates[0][0]
        total_score = sum(candidates.values())
        confidence = round(sorted_candidates[0][1] / total_score, 2) if total_score > 0 else 1.0
        candidate_list = [{"name": name, "score": round(score, 2)} for name, score in sorted_candidates[:3]]
        
        return {
            "category": best_cat,
            "category_confidence": confidence,
            "category_source": "rule_based_metadata",
            "category_candidates": candidate_list,
            "is_uncategorized": False,
            "fallback_reason": None,
            "category_version": "2.0"
        }
    
    return {
        "category": "❓ 기타/미분류",
        "category_confidence": 0.0,
        "category_source": "fallback_failed",
        "category_candidates": [],
        "is_uncategorized": True,
        "fallback_reason": "no_metadata_or_keyword_match",
        "category_version": "2.0"
    }

def analyze_session_text_advanced(session):
    session_text = session.get("session_text", "")
    events = session.get("events", [])
    
    res = classify_session_advanced(events, session_text)
    
    gcp_res = analyze_text_with_gcp(session_text)
    if gcp_res:
        score = gcp_res["documentSentiment"]["score"]
        stability_factor = max(0.1, 1.0 - max(0.0, -score) * 0.8)
        max_mod_confidence = 0.0
        bad_categories = ["Toxic", "Insult", "Profanity", "Violence", "Hate Speech", "Harassment", "Derogatory", "Sexual"]
        for cat in gcp_res["moderationCategories"]:
            if cat["name"] in bad_categories:
                max_mod_confidence = max(max_mod_confidence, cat["confidence"])
        safety_factor = max(0.1, 1.0 - max_mod_confidence * 1.2)
    else:
        stability_factor, safety_factor = analyze_sentiment_and_stimulus_fallback(session_text)
        
    keywords = []
    if gcp_res:
        entities = gcp_res["entities"]
        for e in entities:
            name = e["name"]
            if e.get("type") in ["NUMBER", "PRICE", "DATE", "PHONE_NUMBER"]:
                continue
            cleaned = clean_and_filter_keyword(name)
            if not cleaned:
                continue
            keywords.append((cleaned, int(e["salience"] * 100)))
            if len(keywords) >= 10:
                break
    else:
        keywords = extract_keywords_fallback(session_text)
        
    return keywords, res, stability_factor, safety_factor, gcp_res
