# 1. 나만의 관심사 사전(Dictionary) 만들기
# 이 사전은 질문자님의 평소 관심사에 맞게 단어들을 계속 추가하고 수정하면 됩니다!
CATEGORY_DICT = {
    '📈 경제/금융': ['주식', '투자', '금리', '부동산', '비트코인', '경제', '삼성전자', '배당금', '재테크', '달러', '매수', '코스피'],
    '💻 IT/테크': ['파이썬', '코딩', '개발', '스마트폰', '애플', '갤럭시', 'AI', '인공지능', '프로그래밍', '업데이트', '리뷰'],
    '🎮 게임': ['롤', '배그', '스팀', '공략', '티어', '패치', '닌텐도', '플레이', '게임', '업데이트', '스킬'],
    '🔬 과학/지식': ['과학', '우주', '뇌', '물리', '역사', '심리', '불안', '상대성이론', '지식', '다큐'],
    '🍿 엔터/예능': ['무한도전', '유재석', '아이돌', '가수', '뮤비', '노래', '예능', '먹방', '드라마', '영화'],
    '🏋️ 건강/운동': ['다이어트', '운동', '헬스', '단백질', '루틴', '근육', '영양제']
}


def classify_video(keywords):
    """
    추출된 키워드 리스트를 바탕으로 가장 점수가 높은 카테고리를 찾아냅니다.
    keywords 형식 예시: [('주식', 3), ('투자', 3), ('금리', 2), ('오늘', 1)]
    """
    # 각 카테고리별 점수판을 0점으로 초기화
    scores = {category: 0 for category in CATEGORY_DICT.keys()}

    # 추출된 키워드를 하나씩 꺼내서 확인
    for word, count in keywords:
        # 우리가 만든 사전의 카테고리와 단어들을 뒤져봅니다
        for category, dict_words in CATEGORY_DICT.items():
            if word in dict_words:
                # 사전에 있는 단어가 나왔다면, 그 단어가 등장한 횟수만큼 점수를 더합니다!
                # (예: '주식'이 3번 나왔으면 경제/금융 카테고리에 +3점)
                scores[category] += count

                # 점수판 확인 (테스트용 출력)
    print(f"  [점수판] {scores}")

    # 점수가 가장 높은 카테고리를 찾습니다
    best_category = max(scores, key=scores.get)

    # 만약 최고 점수가 0점이라면 (우리 사전에 있는 단어가 하나도 안 나왔다면)
    if scores[best_category] == 0:
        return "❓ 기타/미분류"

    return best_category


# --- 테스트 실행 ---
# 이전 단계(KoNLPy 형태소 분석)에서 추출했다고 가정한 키워드 결과물들
test_video_1_keywords = [('주식', 3), ('투자', 3), ('금리', 2), ('배당금', 1), ('방법', 1)]
test_video_2_keywords = [('우주', 4), ('상대성이론', 2), ('물리', 2), ('시간', 1)]
test_video_3_keywords = [('스킬', 5), ('공략', 3), ('패치', 2), ('마우스', 1)]
test_video_4_keywords = [('점심', 2), ('날씨', 1), ('산책', 1)]  # 사전에 없는 일상어

print("=== 첫 번째 영상 분류 ===")
result1 = classify_video(test_video_1_keywords)
print(f"👉 최종 분류: {result1}\n")

print("=== 두 번째 영상 분류 ===")
result2 = classify_video(test_video_2_keywords)
print(f"👉 최종 분류: {result2}\n")

print("=== 세 번째 영상 분류 ===")
result3 = classify_video(test_video_3_keywords)
print(f"👉 최종 분류: {result3}\n")

print("=== 네 번째 영상 분류 ===")
result4 = classify_video(test_video_4_keywords)
print(f"👉 최종 분류: {result4}\n")