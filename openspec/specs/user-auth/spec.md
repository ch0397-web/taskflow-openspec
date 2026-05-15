## ADDED Requirements

### Requirement: User Registration
시스템은 이메일과 비밀번호로 회원가입을 지원해야 한다. 비밀번호는 bcrypt로 해싱되어 저장되며, 가입 즉시 JWT를 발급한다.

- 이메일: 유효한 형식, UNIQUE 제약
- 비밀번호: 8자 이상
- 응답: HTTP 201 + `{ token, user: { id, email, team_id } }`
- 에러: 중복 이메일 409 `EMAIL_TAKEN`, 형식 오류 400 `VALIDATION_ERROR`

#### Scenario: Successful signup
- **WHEN** POST /auth/signup with valid email and password (8+ chars)
- **THEN** system returns HTTP 201 with JWT token and user object (team_id: null)

#### Scenario: Duplicate email
- **WHEN** POST /auth/signup with already registered email
- **THEN** system returns HTTP 409 with error code EMAIL_TAKEN

#### Scenario: Invalid email format
- **WHEN** POST /auth/signup with malformed email (e.g., "user@invalid")
- **THEN** system returns HTTP 400 with error code VALIDATION_ERROR

#### Scenario: Password too short
- **WHEN** POST /auth/signup with password shorter than 8 characters
- **THEN** system returns HTTP 400 with error code VALIDATION_ERROR

---

### Requirement: User Login
시스템은 이메일+비밀번호 검증 후 JWT(24시간 유효)를 발급해야 한다. 이메일 존재 여부를 응답에서 노출하지 않는다.

- 성공: HTTP 200 + `{ token, user: { id, email, team_id } }`
- 실패: HTTP 401 `INVALID_CREDENTIALS` (이메일 존재 여부 불문 동일 메시지)
- 로그인 후 `users.team_id` 값으로 라우팅 분기 (NULL → 팀선택, 값 있음 → 칸반)

#### Scenario: Successful login
- **WHEN** POST /auth/login with correct email and password
- **THEN** system returns HTTP 200 with 24h JWT token and user.team_id value

#### Scenario: Wrong password
- **WHEN** POST /auth/login with correct email but wrong password
- **THEN** system returns HTTP 401 with error code INVALID_CREDENTIALS (not revealing email existence)

#### Scenario: Non-existent email
- **WHEN** POST /auth/login with email not in database
- **THEN** system returns HTTP 401 with error code INVALID_CREDENTIALS (same message as wrong password)

---

### Requirement: JWT Authentication Middleware
모든 `/teams/*`, `/tasks/*`, `/messages/*` 라우트는 `Authorization: Bearer <token>` 헤더를 검증해야 한다.

- 토큰 없음 또는 만료: HTTP 401 `TOKEN_EXPIRED`
- 유효한 토큰: `current_user` 컨텍스트 주입

#### Scenario: Valid token on protected route
- **WHEN** request includes valid non-expired JWT in Authorization header
- **THEN** system processes request with current_user context injected

#### Scenario: Expired token
- **WHEN** request includes JWT that has passed its 24h expiry
- **THEN** system returns HTTP 401 with error code TOKEN_EXPIRED

#### Scenario: Missing token
- **WHEN** request to protected route has no Authorization header
- **THEN** system returns HTTP 401 with error code TOKEN_EXPIRED

---

### Requirement: Stateless Logout
로그아웃은 서버에 블랙리스트를 유지하지 않는다. POST /auth/logout은 HTTP 200만 반환하며, 클라이언트가 localStorage에서 토큰을 삭제한다.

#### Scenario: Logout
- **WHEN** POST /auth/logout with valid JWT
- **THEN** system returns HTTP 200 with empty body

---

### Requirement: Current User Info
GET /auth/me는 현재 JWT에서 사용자 정보를 반환한다.

#### Scenario: Get current user
- **WHEN** GET /auth/me with valid JWT
- **THEN** system returns HTTP 200 with user id, email, team_id

---

### Requirement: Standardized Error Response
모든 4xx/5xx 응답은 `{ error: { code, message } }` 형태를 따른다. code는 SCREAMING_SNAKE, message는 한국어.

#### Scenario: Error response format
- **WHEN** any API call results in a 4xx or 5xx error
- **THEN** response body is { "error": { "code": "SCREAMING_SNAKE", "message": "한국어 메시지" } }
