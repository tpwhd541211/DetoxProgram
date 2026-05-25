from youtube_transcript_api import YouTubeTranscriptApi


def get_summary_transcript(video_id, front_mins=1.5, back_mins=1.0):
    """
    영상 ID를 받아 초반(front_mins)과 후반(back_mins) 분량의 자막만 추출하여 결합합니다.
    """
    try:
        # 영상의 모든 자막 목록을 가져옵니다 (자동생성 자막 포함)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # 한국어('ko') 자막을 찾습니다. (수동 자막 우선, 없으면 자동 자막)
        transcript = transcript_list.find_transcript(['ko']).fetch()

        if not transcript:
            return "자막 내용이 없습니다."

        # 전체 영상 길이 계산 (마지막 자막의 시작 시간 + 지속 시간)
        last_entry = transcript[-1]
        total_duration = last_entry['start'] + last_entry['duration']

        # 초 단위로 변환
        front_seconds = front_mins * 60
        back_start_time = total_duration - (back_mins * 60)

        extracted_text = []

        for entry in transcript:
            start_time = entry['start']

            # 조건 1: 시작 시간이 지정된 초반 시간(예: 90초) 이하일 때
            # 조건 2: 시작 시간이 전체 길이에서 후반 지정 시간(예: 60초)을 뺀 시간보다 클 때
            if start_time <= front_seconds or start_time >= back_start_time:
                # 불필요한 줄바꿈 제거 후 리스트에 추가
                clean_text = entry['text'].replace('\n', ' ')
                extracted_text.append(clean_text)

        # 추출된 자막 조각들을 띄어쓰기로 연결하여 하나의 문장으로 만듦
        return " ".join(extracted_text)

    except Exception as e:
        return f"자막 없음 또는 오류: {e}"


# --- 테스트 실행 ---
# 질문자님의 시청 기록에 있던 영상 ID 예시입니다. ([Full] 취미는 과학 - 6화 불안, 내가 문제인가? 뇌가 문제인가?)
test_video_id = "YG778dm5ZBs"

print(f"영상({test_video_id}) 자막 추출 중... (초반 1.5분 + 후반 1분)")
result_text = get_summary_transcript(test_video_id, front_mins=1.5, back_mins=1.0)

print("\n=== 추출된 핵심 요약 텍스트 ===")
print(result_text)