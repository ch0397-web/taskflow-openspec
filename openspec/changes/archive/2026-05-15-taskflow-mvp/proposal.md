## Why

소규모 팀이 태스크 현황과 커뮤니케이션을 별도 도구 없이 한 화면에서 추적할 수 있는 MVP가 필요하다. 칸반 보드와 실시간 채팅을 단일 서비스로 통합해 팀원이 컨텍스트 전환 없이 업무 진행 상황을 파악하고 합의할 수 있게 한다.

## What Changes

- FastAPI 백엔드 신규 구축 (Python, async, JWT 인증, bcrypt 해싱)
- Vanilla JS + Tailwind CSS 프론트엔드 신규 구축 (MPA 구조, 4개 HTML 페이지)
- SQLite(로컬) / Neon PostgreSQL(운영) 이중 환경 DB 구성
- Vercel 배포 (프론트: 정적 파일, 백엔드: Serverless Functions)
- API 18개 구현 (Auth 4 + Team 5 + Task 6 + Chat 3)
- DB 4테이블: `users`, `teams`, `tasks`, `messages`

**범위 외 (이번 MVP에 포함하지 않음):**
- 이메일/SMS/푸시 알림
- 파일 첨부 (이미지, 문서)
- 전문 검색 (Full-text search)
- 권한 세분화 (페이지별 권한, 팀 추방)
- 다국어 지원 (한국어 UI만)
- WebSocket 실시간 통신 (5초 폴링으로 대체)
- 자동화 테스트 (pytest/jest)

## Capabilities

### New Capabilities

- `user-auth`: 회원가입, 로그인, JWT 발급(24h), bcrypt 비밀번호 해싱, 로그아웃(stateless)
- `team-management`: 팀 생성, 초대코드 발급(XXXX-9999 형식), 초대코드 합류, 멤버 목록 조회, 팀 탈퇴
- `kanban`: TODO/DOING/DONE 3컬럼 태스크 보드, 카드 생성/수정/삭제/상태 이동, assignee 지정, 필터(@me/미할당)
- `chat`: 팀 단위 채팅 송수신, 5초 폴링(since= 증분), 메시지 1000자 제한, 본인 메시지 삭제
- `deployment`: 로컬 SQLite + 운영 Neon PostgreSQL 환경 분리, Vercel 자동 배포

### Modified Capabilities

## Impact

- 신규 프로젝트 (기존 코드 없음)
- **백엔드**: `backend/` — FastAPI, SQLAlchemy, python-jose, bcrypt, uvicorn
- **프론트엔드**: `frontend/` — HTML 4개, Vanilla JS, Tailwind CDN
- **DB**: `users(id, email, password_hash, team_id, created_at)`, `teams(id, name, invite_code, owner_id, created_at)`, `tasks(id, team_id, title, status, creator_id, assignee_id, created_at)`, `messages(id, team_id, user_id, content, created_at)`
- **배포**: DATABASE_URL 환경변수 하나로 로컬/운영 전환
- **CORS**: Vercel 도메인 명시 필요
