# 🌐 외부 공유 및 호스팅 가이드 (Share & Deployment Guide)

이 문서는 사용자의 PC를 서버로 활용하여 **Docker Compose**와 **Cloudflare Tunnels**를 통해 외부 사용자에게 보안 도메인 링크(HTTPS)를 무료로 신속하게 제공하는 방법을 설명합니다.

---

## 🛠️ 1. 사전 준비 사항

### ① Docker Desktop 설치
프로젝트가 Java(KoNLPy) 및 Nginx 웹 서버에 의존하므로, 개별 설치 과정 없이 한 번에 구동할 수 있도록 Docker가 필요합니다.
*   [Docker Desktop 공식 홈페이지](https://www.docker.com/products/docker-desktop/)에서 Windows용 버전을 설치하고 실행해 둡니다.

### ② 환경 변수 설정 점검
기본적으로 `.env` 파일과 `.env.local` 파일이 프로젝트 내에 존재하지만, 배포/공유 전 필요 시 예시 파일(`.env.example` 시리즈)을 참조해 아래 키들이 유효한지 확인합니다.
*   **백엔드 (`DetoxProgram/backend/.env`)**:
    *   `GEMINI_API_KEY`: Google AI Studio에서 발급받은 API 키
    *   `YOUTUBE_API_KEY`: Google Cloud Console에서 발급받은 유튜브 API 키
    *   `GOOGLE_APPLICATION_CREDENTIALS`: 구글 NLP 자연어 처리에 필요한 서비스 계정 JSON 파일 이름 (예: `gcp_creds.json`)
*   **프론트엔드 (`DetoxProgram/frontend_nextjs/.env.local`)**:
    *   `NEXT_PUBLIC_SUPABASE_URL`: Supabase 프로젝트 주소
    *   `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Supabase 익명 키

---

## ⚡ 2. Docker Compose로 로컬 통합 구동

Nginx가 프론트엔드와 백엔드를 묶어 하나의 주소(`http://localhost:8080`)로 서비스하게 됩니다.

1.  **터미널(PowerShell 또는 Command Prompt)을 열고 프로젝트 폴더로 이동합니다.**
    ```bash
    cd c:\Users\Administrator\Desktop\UnbelievableTeamProject\DetoxProgram
    ```

2.  **도커 컴포즈 빌드 및 실행 명령을 내립니다.**
    ```bash
    docker compose up --build
    ```
    *   *첫 실행 시 Node 패키지 다운로드 및 Java JRE 설치 등으로 인해 2~5분 정도 소요될 수 있습니다.*
    *   실행이 완료되면 터미널에 로그가 표시되며, 웹 브라우저를 열고 **`http://localhost:8080`**에 접속해 정상 작동하는지 확인합니다.

---

## 🚀 3. Cloudflare Tunnels로 인터넷에 즉시 배포하기

Cloudflare Tunnels를 사용하면 **포트 포워딩 설정 없이** 전 세계 어디서나 접속할 수 있는 안전한 임시 HTTPS URL을 발급받을 수 있습니다. 무료이며 회원가입이 필수가 아닙니다.

### ① cloudflared 설치
*   **방법 A (추천 - Windows 패키지 관리자)**: 새로운 터미널을 열고 아래 명령을 실행합니다.
    ```powershell
    winget install Cloudflare.cloudflared
    ```
*   **방법 B (수동 다운로드)**: [Cloudflare 다운로드 페이지](https://github.com/cloudflare/cloudflared/releases)에서 `cloudflared-windows-amd64.msi`를 다운로드하여 설치합니다.

### ② 터널 열기 (임시 도메인 무료 생성)
터미널을 열고 다음 명령어를 실행하여 Docker Compose가 열어둔 `8080` 포트를 바인딩합니다.
```bash
cloudflared tunnel --url http://localhost:8080
```

### ③ 주소 공유
명령어를 실행하면 터미널 출력 로그 중에 다음과 같은 주소가 생성됩니다.
```text
+-------------------------------------------------------------+
|  Your quick tunnel has been created! Visit it at:           |
|  https://some-random-words.trycloudflare.com                |
+-------------------------------------------------------------+
```
*   위의 **`https://~.trycloudflare.com`** 주소가 외부 접속용 주소입니다.
*   이 주소를 복사하여 스마트폰, 다른 사람의 PC 등에서 접속하면 본인의 컴퓨터가 켜져 있고 Docker가 구동 중인 동안 서비스가 안전하게 실시간으로 호스팅됩니다.
*   **종료 방법**: 터미널에서 `Ctrl + C`를 누르면 터널이 즉시 종료되고 외부 접근이 차단됩니다.
