## ADDED Requirements

### Requirement: Team Creation
팀 리더는 팀을 생성하고 초대코드를 발급받는다. 생성자는 자동으로 owner가 되며, users.team_id가 해당 팀으로 업데이트된다.

- 팀 이름: 1-30자
- 초대코드: 서버 자동 생성, 형식 `^[A-Z]{4}-[0-9]{4}$` (예: FRNT-2026)
- 응답: HTTP 201 + `{ id, name, invite_code, owner_id, created_at }`

#### Scenario: Successful team creation
- **WHEN** POST /teams with valid team name (1-30 chars) and valid JWT
- **THEN** system returns HTTP 201 with team object including auto-generated invite_code
- **THEN** users.team_id is updated to the new team's id

#### Scenario: Team name too long
- **WHEN** POST /teams with team name exceeding 30 characters
- **THEN** system returns HTTP 400 with error code VALIDATION_ERROR

---

### Requirement: Join Team via Invite Code
팀원은 초대코드를 입력해 기존 팀에 합류한다. 합류 시 users.team_id가 업데이트된다.

- 초대코드 형식 검증: 클라이언트 + 서버 양쪽
- 존재하지 않는 코드: 404 `NOT_FOUND`
- 이미 다른 팀 소속: 409 (기존 팀 탈퇴 필요, Day 2 범위 외)
- 응답: HTTP 200 + `{ team: { id, name, member_count }, redirect: "/teams/{id}" }`

#### Scenario: Successful join
- **WHEN** POST /teams/join with valid invite_code matching existing team
- **THEN** system returns HTTP 200 with team info and users.team_id updated

#### Scenario: Invalid invite code format
- **WHEN** POST /teams/join with malformed code (e.g., "abcd1234" without hyphen)
- **THEN** system returns HTTP 400 with error code VALIDATION_ERROR

#### Scenario: Invite code not found
- **WHEN** POST /teams/join with correctly formatted but non-existent code
- **THEN** system returns HTTP 404 with error code NOT_FOUND

#### Scenario: Already in a team
- **WHEN** POST /teams/join when user already has a non-null team_id
- **THEN** system returns HTTP 409

---

### Requirement: Team Access Guard
team_id가 NULL인 사용자는 칸반/채팅에 접근할 수 없다. 비멤버가 다른 팀의 리소스에 접근하면 403을 반환한다.

- `users.team_id IS NULL` → 팀 선택 화면으로 강제 redirect
- `users.team_id ≠ requested team_id` → HTTP 403 `FORBIDDEN`

#### Scenario: Unauthenticated team member accesses team resources
- **WHEN** user with team_id=NULL attempts GET /teams/{id}/tasks
- **THEN** system returns HTTP 403 with error code FORBIDDEN

#### Scenario: Member of different team accesses resources
- **WHEN** user with team_id=1 attempts GET /teams/2/tasks
- **THEN** system returns HTTP 403 with error code FORBIDDEN

---

### Requirement: Get Team Info
GET /teams/{id}는 팀 기본 정보를 반환한다. 해당 팀 멤버만 접근 가능.

#### Scenario: Get team info as member
- **WHEN** GET /teams/{id} with JWT of a user whose team_id matches {id}
- **THEN** system returns HTTP 200 with team id, name, invite_code, owner_id

---

### Requirement: Member List
GET /teams/{id}/members는 팀 멤버 목록을 반환한다. owner 여부를 표시한다.

- 응답: `[{ id, email, is_owner, joined_at }]`

#### Scenario: Get member list
- **WHEN** GET /teams/{id}/members with valid team member JWT
- **THEN** system returns HTTP 200 with list of members, each indicating is_owner status

---

### Requirement: Leave Team
DELETE /teams/{id}/leave는 자기 자신을 팀에서 탈퇴시킨다. users.team_id를 NULL로 업데이트한다.

- owner는 팀을 탈퇴할 수 없다 (팀 삭제 기능 없음, MVP 범위 외)

#### Scenario: Member leaves team
- **WHEN** DELETE /teams/{id}/leave by a non-owner member
- **THEN** system returns HTTP 200 and sets users.team_id to NULL

#### Scenario: Owner attempts to leave
- **WHEN** DELETE /teams/{id}/leave by team owner
- **THEN** system returns HTTP 403 with error code FORBIDDEN
