## Context

신규 프로젝트. 기존 코드 없음. 소규모 팀(3-5인)이 칸반+채팅을 한 화면에서 쓸 수 있는 MVP를 Day 2 내에 완성한다. 학습 목적이므로 단순성을 최우선으로 하되, Vercel + Neon을 통해 실전 배포 패턴을 경험한다.

**제약:**
- Vanilla JS + Tailwind (프레임워크 없음)
- FastAPI (Python)
- DB: 로컬 SQLite / 운영 Neon PostgreSQL
- 배포: Vercel (FE 정적 + BE Serverless Functions)
- 자동화 테스트 없음 (수동 동작 확인)

## Goals / Non-Goals

**Goals:**
- API 18개 (Auth 4 + Team 5 + Task 6 + Chat 3) 완전 동작
- DB 4테이블 + 인덱스 적용
- JWT 인증 미들웨어로 모든 보호 라우트 커버
- 비멤버 403, 삭제 권한 검증 완전 구현
- 로컬(SQLite) → 운영(Neon) DATABASE_URL 한 줄 전환
- Vercel 자동 배포 (main push → 배포)

**Non-Goals:**
- WebSocket 실시간 통신
- 자동화 테스트
- 파일 업로드, 이메일 인증, 토큰 갱신
- 다국어, 페이지별 권한, 전문 검색

## Decisions

### 1. MPA (Multi-Page Application) — SPA 아님

Vanilla JS에서 클라이언트 라우터를 구현하면 복잡도가 급격히 증가한다. 화면이 4개(로그인, 팀선택, 칸반, 채팅)이고 각각 독립적이므로 HTML 파일 4개로 분리한다.

```
frontend/
├── login.html       (회원가입 + 로그인)
├── team.html        (팀 선택 + 초대코드)
├── kanban.html      (칸반 보드)
└── chat.html        (채팅)
```

페이지 전환은 `window.location.href`로 처리. JWT 없으면 login.html로 redirect.

**대안 고려:** Hash-based SPA (`#/kanban`) — 라우터 구현 부담으로 기각.

### 2. Tailwind CSS CDN — 빌드 도구 없음

MVP Day 2 범위에서 빌드 파이프라인(Node.js, PostCSS) 설정은 불필요한 복잡성이다.  
`<script src="https://cdn.tailwindcss.com">` 한 줄로 사용.

**대안 고려:** Vite + Tailwind — 빌드 최적화는 필요하나 MVP 범위 외로 기각.

### 3. SQLAlchemy ORM + DATABASE_URL 전환

```python
# 로컬: sqlite:///./taskflow.db
# 운영: postgresql+asyncpg://...neon.tech/neondb
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")
```

SQLAlchemy 2.0 async 엔진으로 양쪽 호환. 로컬은 aiosqlite, 운영은 asyncpg 드라이버.

### 4. FastAPI → Vercel Serverless Functions

`vercel.json`에 FastAPI를 ASGI 핸들러로 등록. `api/index.py`를 진입점으로 사용.

```json
{
  "builds": [{"src": "api/index.py", "use": "@vercel/python"}],
  "routes": [{"src": "/api/(.*)", "dest": "api/index.py"}]
}
```

프론트엔드 정적 파일은 Vercel이 자동 서빙.

### 5. 5초 폴링 — WebSocket 대체

WebSocket은 Vercel Serverless에서 지원되지 않는다. 5초 `setInterval` + `?since=<ISO_timestamp>` 증분 조회로 대체. 네트워크 끊김 시 exponential backoff(5s→10s→20s→40s→60s 고정).

### 6. JWT localStorage — stateless 로그아웃

JWT 블랙리스트 없음. 로그아웃 시 클라이언트가 localStorage에서 토큰 삭제. 24시간 만료. 만료 시 401 → 자동 redirect.

모든 API 요청에 `Authorization: Bearer <token>` 헤더 자동 첨부 (fetch interceptor 패턴).

### 7. 1인 1팀 (users.team_id)

`teams` 테이블에 `members` 조인 테이블 없이 `users.team_id FK → teams`로 멤버십 표현. 단순하고 4테이블 제약에 부합. 팀 변경(탈퇴 후 재합류)은 `team_id UPDATE`로 처리.

**대안 고려:** `team_members(user_id, team_id, role)` 조인 테이블 — 5번째 테이블 필요, MVP 범위 외로 기각.

### 8. tasks.assignee_id nullable

`creator_id`(생성자) ≠ `assignee_id`(담당자). "내 태스크" = `WHERE assignee_id = current_user_id`. 미할당 태스크는 `assignee_id IS NULL`.

## Risks / Trade-offs

| 리스크 | 완화 방안 |
|--------|-----------|
| Tailwind CDN은 미사용 클래스 포함(파일 크기 큼) | MVP 범위에서 성능 비중이 낮아 허용 |
| localStorage JWT는 XSS에 취약 | 한국어 사용자만, 입력값 escape, MVP 범위 허용 |
| 5초 폴링은 서버 부하 | 동시 50명 이하 가정, Neon 무료 티어 허용 범위 |
| SQLite FK는 기본 비활성 | `PRAGMA foreign_keys = ON` 명시 설정 |
| Vercel Serverless cold start | 무료 티어에서 첫 요청 느릴 수 있음 (허용) |
| FastAPI async SQLite | aiosqlite 드라이버 필요, asyncpg와 다른 연결 설정 |
