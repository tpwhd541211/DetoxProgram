from konlpy.tag import Okt
from collections import Counter

# 형태소 분석기 초기화
okt = Okt()


def extract_keywords(text, num_keywords=10):
    """
    텍스트에서 의미 있는 명사만 추출하여 가장 많이 등장한 키워드를 반환합니다.
    """
    print("텍스트 분석 중... (명사 추출)")

    # 1. 텍스트에서 명사만 추출
    nouns = okt.nouns(text)

    # 2. 불용어(Stopwords) 제거 및 한 글자 단어 제외
    # 분석에 의미가 없는 뻔한 단어들을 미리 걸러냅니다. (필요에 따라 계속 추가 가능)
    stop_words = ['정말', '진짜', '오늘', '저희', '여러분', '그냥', '가장', '지금', '생각', '사람', '우리', '영상', '구독', '좋아요']

    valid_nouns = []
    for noun in nouns:
        # 두 글자 이상인 단어만 가져오고, 불용어 사전에 없는 것만 취급
        if len(noun) >= 2 and noun not in stop_words:
            valid_nouns.append(noun)

    # 3. 단어별 빈도수 계산
    count = Counter(valid_nouns)

    # 4. 가장 많이 나온 단어 상위 N개 추출
    top_keywords = count.most_common(num_keywords)

    return top_keywords


# --- 테스트 실행 ---
# 이전 단계에서 뽑아냈다고 가정한 가상의 '영상 제목 + 앞/뒤 자막 텍스트' 입니다.
sample_text = """
안녕하세요 여러분! 오늘 영상에서는 최근 화제가 되고 있는 삼성전자 주식과 미국 금리 인상에 대해 알아보겠습니다. 
주식을 처음 하시는 분들은 정말 고민이 많으실 텐데요. 제가 진짜 확실하게 투자 전략을 짚어드릴게요.
(중략) 
결론적으로 현재 금리 상황을 볼 때, 단기적인 투자보다는 배당금을 노리는 장기 투자가 훨씬 유리합니다. 
여러분들의 성공적인 주식 투자를 응원합니다! 구독과 좋아요 부탁드려요!
"""

print("=== 분석 대상 텍스트 ===")
print(sample_text[:100] + "...\n")

keywords = extract_keywords(sample_text, num_keywords=5)

print("\n=== 🎯 추출된 핵심 키워드 TOP 5 ===")
for word, freq in keywords:
    print(f"- {word}: {freq}번 등장")