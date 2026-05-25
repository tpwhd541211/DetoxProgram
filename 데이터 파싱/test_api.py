from googleapiclient.discovery import build

# !!! 발급받은 API 키를 아래에 문자열로 넣어주세요 !!!
API_KEY = "여기에_본인의_API_KEY를_붙여넣으세요"

# 유튜브 API 클라이언트 생성
youtube = build('youtube', 'v3', developerKey=API_KEY)


def get_video_metadata(video_id):
    """
    영상 ID를 받아 제목, 태그, 설명, 카테고리 ID를 딕셔너리로 반환합니다.
    """
    try:
        # API에 정보 요청 (snippet에 주요 정보가 들어있음)
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()

        # 검색된 영상이 없다면 None 반환
        if not response['items']:
            return Nones

        snippet = response['items'][0]['snippet']

        return {
            'title': snippet.get('title', ''),
            'tags': snippet.get('tags', []),  # 태그는 리스트 형태로 반환됨
            'description': snippet.get('description', ''),
            'category_id': snippet.get('categoryId', '')
        }

    except Exception as e:
        return f"API 호출 오류: {e}"


# --- 테스트 실행 ---
test_video_id = "YG778dm5ZBs"

print("메타데이터 가져오는 중...")
metadata = get_video_metadata(test_video_id)

print("\n=== 추출된 메타데이터 ===")
if isinstance(metadata, dict):
    print(f"제목: {metadata['title']}")
    print(f"카테고리 ID: {metadata['category_id']}")
    print(f"태그: {metadata['tags']}")
    # 설명은 너무 길 수 있으니 100자만 출력
    print(f"설명(일부): {metadata['description'][:100]}...")
else:
    print(metadata)