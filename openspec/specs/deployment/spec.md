## ADDED Requirements

### Requirement: Local Development Environment
로컬 개발은 FastAPI + SQLite로 단일 서버에서 동작한다. 빌드 도구 없이 즉시 시작 가능해야 한다.

- 백엔드: `uvicorn main:app --reload` (포트 8000)
- DB: `sqlite:///./taskflow.db` (자동 생성)
- 프론트엔드: `frontend/` 정적 파일을 live-server 또는 `python -m http.server`로 서빙
- 환경변수: `.env` 파일에 `SECRET_KEY`, `DATABASE_URL` (기본값 SQLite)

#### Scenario: Local startup
- **WHEN** developer runs `uvicorn main:app --reload` in backend directory
- **THEN** server starts on port 8000 with SQLite database auto-created
- **THEN** all 18 API endpoints are accessible at http://localhost:8000

---

### Requirement: Database URL Switching
`DATABASE_URL` 환경변수 하나로 로컬(SQLite)과 운영(Neon PostgreSQL)을 전환한다.

- 로컬: `DATABASE_URL=sqlite+aiosqlite:///./taskflow.db`
- 운영: `DATABASE_URL=postgresql+asyncpg://...neon.tech/neondb`
- SQLAlchemy가 드라이버를 자동 선택

#### Scenario: Switch to Neon
- **WHEN** DATABASE_URL is set to Neon PostgreSQL connection string
- **THEN** application connects to Neon without code changes
- **THEN** all 4 tables are created via SQLAlchemy create_all on startup

---

### Requirement: Vercel Deployment
프론트엔드와 백엔드 모두 Vercel에 배포된다. `main` 브랜치 push 시 자동 배포.

- 프론트엔드: `frontend/` 정적 파일 → Vercel CDN
- 백엔드: FastAPI → Vercel Serverless Functions (`api/index.py` 진입점)
- `vercel.json`으로 라우팅 구성
- Vercel 환경변수에 `DATABASE_URL` (Neon), `SECRET_KEY` 설정

#### Scenario: Production deployment
- **WHEN** git push to main branch
- **THEN** Vercel automatically builds and deploys both frontend and backend
- **THEN** frontend is accessible at `https://taskflow.vercel.app`
- **THEN** API is accessible at `https://taskflow.vercel.app/api/*`

---

### Requirement: CORS Configuration
운영 배포 시 Vercel 도메인에서만 API 접근을 허용한다.

- 개발: `http://localhost:*` 허용
- 운영: `https://*.vercel.app` 허용
- FastAPI CORSMiddleware로 구성

#### Scenario: CORS on production
- **WHEN** frontend at taskflow.vercel.app makes API request
- **THEN** CORS headers allow the request

#### Scenario: CORS blocks unauthorized origin
- **WHEN** request from unknown origin to API
- **THEN** CORS headers block the request
