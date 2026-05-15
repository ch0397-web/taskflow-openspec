## 1. 프로젝트 초기 설정

- [ ] 1.1 디렉토리 구조 생성 (`backend/`, `frontend/`, `vercel.json`, `.env`)
- [ ] 1.2 백엔드 의존성 설치 (`fastapi`, `uvicorn`, `sqlalchemy`, `aiosqlite`, `asyncpg`, `python-jose`, `bcrypt`, `python-dotenv`)
- [ ] 1.3 `backend/main.py` 생성 — FastAPI 앱, CORSMiddleware 설정 (localhost + vercel.app)
- [ ] 1.4 `backend/database.py` — SQLAlchemy async 엔진, DATABASE_URL 환경변수로 SQLite/Neon 전환
- [ ] 1.5 `backend/models.py` — ORM 모델 4개 정의 (users, teams, tasks, messages) + 인덱스
- [ ] 1.6 DB 테이블 자동 생성 (`create_all` on startup) 확인

## 2. 인증 API (Auth 4개)

- [ ] 2.1 `POST /auth/signup` — 이메일 형식 검증, bcrypt 해싱, users INSERT, JWT 발급 (201)
- [ ] 2.2 `POST /auth/login` — 이메일+비밀번호 검증, JWT 발급 (200), 실패 시 401 INVALID_CREDENTIALS
- [ ] 2.3 JWT 미들웨어 (`get_current_user` 의존성) — Bearer 토큰 검증, 만료 시 401 TOKEN_EXPIRED
- [ ] 2.4 `GET /auth/me` — 현재 사용자 정보 반환
- [ ] 2.5 `POST /auth/logout` — 200만 반환 (stateless)
- [ ] 2.6 에러 응답 표준화 — 모든 4xx/5xx에 `{ error: { code, message } }` 형태 적용

## 3. 팀 API (Team 5개)

- [ ] 3.1 `POST /teams` — 팀 생성, invite_code 자동 생성 (`AAAA-9999` 형식), owner_id=current_user, users.team_id UPDATE (201)
- [ ] 3.2 `POST /teams/join` — 초대코드 형식 검증, 팀 조회, users.team_id UPDATE; 404/409 처리
- [ ] 3.3 `GET /teams/{id}` — 팀 정보 반환, 비멤버 403 FORBIDDEN
- [ ] 3.4 `GET /teams/{id}/members` — 멤버 목록 반환 (is_owner 필드 포함)
- [ ] 3.5 `DELETE /teams/{id}/leave` — 본인 탈퇴, users.team_id=NULL; owner는 403

## 4. 칸반 API (Task 6개)

- [ ] 4.1 `GET /teams/{id}/tasks` — 태스크 목록, `?assignee=me|unassigned` 필터, created_at DESC 정렬
- [ ] 4.2 `POST /teams/{id}/tasks` — 태스크 생성, title(1-100자), assignee_id nullable, status=TODO (201)
- [ ] 4.3 `GET /tasks/{id}` — 태스크 상세 (creator_email, assignee_email 포함)
- [ ] 4.4 `PATCH /tasks/{id}/status` — 상태만 변경 (TODO|DOING|DONE), 팀 멤버 누구나 가능
- [ ] 4.5 `PUT /tasks/{id}` — title + assignee_id 수정, 팀 멤버 누구나 가능
- [ ] 4.6 `DELETE /tasks/{id}` — creator 또는 team owner만; 그 외 403 FORBIDDEN

## 5. 채팅 API (Chat 3개)

- [ ] 5.1 `GET /teams/{id}/messages` — 메시지 목록, `?since=ISO_timestamp` 증분 조회, 기본 최근 50개
- [ ] 5.2 `POST /teams/{id}/messages` — 메시지 전송, content 1-1000자 (클라+서버 검증); 초과 시 400 TOO_LONG
- [ ] 5.3 `DELETE /messages/{id}` — 본인 메시지만 삭제; 타인 403 NOT_OWNER

## 6. 프론트엔드 — 로그인/회원가입 (login.html)

- [ ] 6.1 `frontend/login.html` 생성 — Tailwind CDN, 로그인 폼 (이메일, 비밀번호, 버튼)
- [ ] 6.2 회원가입 탭 — 이메일 형식 + 비밀번호 8자 클라이언트 검증
- [ ] 6.3 `POST /auth/signup` 호출 → JWT localStorage 저장 → team.html redirect
- [ ] 6.4 `POST /auth/login` 호출 → JWT 저장 → team_id 분기 (NULL → team.html, 있음 → kanban.html)
- [ ] 6.5 에러 메시지 인라인 표시 (EMAIL_TAKEN, INVALID_CREDENTIALS)
- [ ] 6.6 이미 로그인 상태면 kanban.html로 자동 redirect

## 7. 프론트엔드 — 팀 선택 (team.html)

- [ ] 7.1 `frontend/team.html` 생성 — JWT 없으면 login.html redirect
- [ ] 7.2 팀 만들기 폼 — 팀 이름 입력, `POST /teams` 호출, 초대코드 표시 + 복사 버튼
- [ ] 7.3 초대코드 합류 폼 — 형식 검증(클라), `POST /teams/join` 호출
- [ ] 7.4 합류 성공 시 kanban.html redirect, 에러 케이스 인라인 표시

## 8. 프론트엔드 — 칸반 (kanban.html)

- [ ] 8.1 `frontend/kanban.html` 생성 — JWT + team_id 없으면 redirect
- [ ] 8.2 3컬럼 레이아웃 (TODO/DOING/DONE), `GET /teams/{id}/tasks` 로드
- [ ] 8.3 필터 탭 (전체/@me/미할당) — 클라이언트 필터링
- [ ] 8.4 각 컬럼 `+` 버튼 → 인라인 입력 폼 → `POST /teams/{id}/tasks`
- [ ] 8.5 HTML5 Drag & Drop — dragstart/dragover/drop 이벤트, drop 시 `PATCH /tasks/{id}/status`
- [ ] 8.6 카드 클릭 → 수정 모달 — 제목/상태/assignee 수정, `PUT /tasks/{id}` 호출
- [ ] 8.7 삭제 버튼 — 확인 다이얼로그, `DELETE /tasks/{id}`, 권한 없으면 버튼 숨김
- [ ] 8.8 헤더 네비게이션 (칸반/채팅/멤버 탭), 로그아웃 버튼
- [ ] 8.9 모바일 반응형 — breakpoint <768px에서 1컬럼 스와이프 (Tailwind sm: 클래스)

## 9. 프론트엔드 — 채팅 (chat.html)

- [ ] 9.1 `frontend/chat.html` 생성 — JWT + team_id 없으면 redirect
- [ ] 9.2 메시지 목록 렌더링 — 본인/타인 말풍선 구분, 발신자+시각 표시
- [ ] 9.3 초기 로드 `GET /teams/{id}/messages` (최근 50개), 이후 5초 `setInterval` 폴링
- [ ] 9.4 since= 파라미터 증분 폴링 — 마지막 메시지 created_at 추적
- [ ] 9.5 메시지 입력창 — 1000자 카운터, 초과 시 전송 버튼 비활성화
- [ ] 9.6 `POST /teams/{id}/messages` 전송, 전송 후 즉시 목록 갱신
- [ ] 9.7 본인 메시지 hover → 삭제 아이콘, `DELETE /messages/{id}` 호출
- [ ] 9.8 네트워크 끊김 표시 — 폴링 실패 시 "연결 끊김" 배너, exponential backoff 재시도

## 10. 배포 설정

- [ ] 10.1 `vercel.json` 작성 — FastAPI Serverless Function 라우팅 (`/api/*` → `api/index.py`)
- [ ] 10.2 `api/index.py` 생성 — FastAPI 앱을 ASGI 핸들러로 노출
- [ ] 10.3 `requirements.txt` 작성 — Vercel Python 런타임용
- [ ] 10.4 Vercel 프로젝트 연결 (`vercel link`), 환경변수 설정 (`DATABASE_URL`, `SECRET_KEY`)
- [ ] 10.5 Neon 데이터베이스 생성, DATABASE_URL 확인, Vercel에 주입
- [ ] 10.6 `git push origin main` → Vercel 자동 배포 확인
- [ ] 10.7 배포된 URL에서 회원가입 → 팀 생성 → 칸반 → 채팅 전체 흐름 수동 검증
