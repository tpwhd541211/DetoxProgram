# 🧘 언블리버블 디톡스 프로그램 (Unbelievable Detox Program)

유튜브 알고리즘 분석 및 자가 진단형 도파민 디톡스 코칭 웹 서비스입니다.  
사용자의 유튜브 시청 기록(Google Takeout) 데이터를 기반으로 인공지능(NLP) 키워드 분석을 수행하고, **4축 DSAO 알고리즘**을 통해 개인별 알고리즘 성향 분석 및 맞춤형 디톡스 솔루션(AI 데일리 미션)을 제공합니다.

---

## 🚀 주요 기능 (Key Features)

1. **유튜브 시청 기록 데이터 파싱**
   * Google Takeout 서비스에서 다운로드한 `시청 기록.html` 파일을 즉각 파싱하여 시청 시간, 비디오 ID, 채널명을 분류 및 전처리합니다. (5초 이하 짧은 시청 건 자동 필터링 기능 내장)
2. **한국어 자연어 처리(NLP) 기반 관심사 분석**
   * KoNLPy(Okt) 형태소 분석기를 탑재하여 사용자가 시청한 영상 제목과 채널 정보로부터 유의미한 한국어 명사 키워드를 추출합니다.
3. **4축 DSAO 알고리즘 성향(페르소나) 진단**
   * **D/P (Director / Passenger)**: 주도성 지수 (이용 주도성 vs 알고리즘 유도성)
   * **W/N (Wide / Narrow)**: 관심 범위 (주제 다양성 및 탐색 범위)
   * **S/M (Spicy / Mild)**: 자극 감도 (자극성 지수 및 감정 영향도)
   * **F/L (Flash / Long)**: 시청 호흡 (영상 평균 길이)
   * 진단된 점수를 기반으로 16가지 맞춤 페르소나(예: `PNSF`)를 부여합니다.
4. **인터랙티브 분석 대시보드**
   * **도파민 추이 그래프**: 시간대별 고도파민 영상 시청 집중도 가시화
   * **관심사 관계망 네트워크 그래프**: 시청 주제의 연관성을 노드와 엣지로 구현
   * **선호 채널 Top 5** 및 최근 시청 상세 내역 제공
5. **AI 기반 디톡스 진단 보고서 & 행동 교정 미션**
   * Gemini API 연동을 통해 사용자의 취약점을 경고하는 "충격 요법 리포트" 및 맞춤형 데일리 미션 리스트를 제공합니다.

---

## 🛠️ 기술 스택 (Tech Stack)

### Backend
* **Language / Framework**: Python 3.10+, FastAPI
* **NLP**: KoNLPy (Okt 형태소 분석기)
* **Runtime Guard**: JPype1 (JVM 동적 환경 변수 바인딩)
* **Database**: SQLite, SQLAlchemy ORM
* **LLM**: Google AI Studio (Gemini 2.5)

### Frontend
* **Language / Framework**: React 18, Next.js (App Router), TypeScript
* **Styling**: TailwindCSS
* **Charts**: Recharts, Network Graph 시각화 컴포넌트

---

## 💻 실행 방법 (Getting Started)

### 1. 백엔드 실행 (FastAPI)
```bash
# 백엔드 디렉토리 이동
cd DetoxProgram/backend

# 가상환경 구축 및 활성화
python -m venv venv
source venv/Scripts/activate # Windows: venv\Scripts\activate

# 의존성 패키지 설치
pip install -r requirements.txt

# 데이터베이스 테이블 초기화
python init_db.py

# uvicorn 서버 실행
uvicorn main:app --reload
```
* **백엔드 주소**: `http://localhost:8000`

### 2. 프론트엔드 실행 (Next.js)
```bash
# 프론트엔드 디렉토리 이동
cd DetoxProgram/frontend_nextjs

# 의존성 패키지 설치
npm install

# 개발 서버 실행
npm run dev
```
* **프론트엔드 주소**: `http://localhost:3000`

---

## 📂 디렉토리 구조 (Directory Structure)
```text
언블리버블 프로젝트/
├── DetoxProgram/
│   ├── backend/            # FastAPI 백엔드 코드
│   │   ├── core/           # DB 설정 및 Config
│   │   ├── models/         # SQLAlchemy DB 스키마
│   │   ├── routers/        # API 엔드포인트 (upload, dashboard, detox)
│   │   └── services/       # NLP, Scoring, LLM, YouTube 파이프라인 서비스
│   ├── frontend_nextjs/    # Next.js 반응형 프론트엔드 코드
│   └── prototype/          # 초기 Streamlit 프로토타입
├── 데이터 파싱/             # 데이터 파싱 샘플 및 테스트 스크립트
└── README.md               # 프로젝트 매뉴얼
```
