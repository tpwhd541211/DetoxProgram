from bs4 import BeautifulSoup
import pandas as pd
import re


def parse_youtube_history(html_file_path):
    print("=== HTML 시청 기록 파싱 시작 ===")

    # 1. HTML 파일 읽기
    with open(html_file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 2. 시청 기록이 담긴 div 태그 찾기
    cells = soup.find_all('div', class_='content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1')

    records = []

    for cell in cells:
        links = cell.find_all('a')
        if not links:
            continue

        video_link = links[0]
        title = video_link.text.strip()
        url = video_link['href']

        channel = links[1].text.strip() if len(links) > 1 else "알 수 없음"

        text_content = cell.get_text(separator='\n').strip()
        lines = text_content.split('\n')
        time_str = lines[-1].strip()

        records.append({
            'title': title,
            'channel': channel,
            'url': url,
            'time_str': time_str
        })

    df = pd.DataFrame(records)
    print(f"전체 HTML 기록 수: {len(df)}건")

    def clean_time_str(t_str):
        t_str = t_str.replace('KST', '').strip()
        match = re.match(r'(\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.)\s*(AM|PM)\s*(\d{1,2}:\d{2}:\d{2})', t_str)
        if match:
            date_part = match.group(1)
            ampm = match.group(2)
            time_part = match.group(3)
            return f"{date_part} {time_part} {ampm}"
        return t_str

    if not df.empty:
        df['time_str_clean'] = df['time_str'].apply(clean_time_str)
        df['time'] = pd.to_datetime(df['time_str_clean'], format='%Y. %m. %d. %I:%M:%S %p', errors='coerce')

        noise_count = df['time'].isna().sum()
        df_valid = df.dropna(subset=['time']).copy()

        print(f"걸러진 노이즈 데이터 수: {noise_count}건")
        print(f"분석용 유효 데이터 수: {len(df_valid)}건")
        print("=== HTML 시청 기록 전처리 완료 ===\n")

        return df_valid
    else:
        return df


# ===== 여기가 실제로 코드를 실행하는 부분입니다 =====
# 질
# 문자님의 파일 경로를 지정하여 함수를 호출합니다.
file_path = r"D:\2504110118이세종\PythonProject\시청 기록.html"
df_history = parse_youtube_history(file_path)

# 결과를 화면에 5줄만 출력해서 확인합니다.
print("결과 확인:")
print(df_history.head())