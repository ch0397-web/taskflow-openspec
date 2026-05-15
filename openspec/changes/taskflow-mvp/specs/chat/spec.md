## ADDED Requirements

### Requirement: Message List with Polling
GET /teams/{id}/messages는 채팅 메시지를 반환한다. 폴링 방식으로 새 메시지를 증분 수신한다.

- 초기 조회: since 없음 → 최근 50개 반환
- 증분 조회: `?since=<ISO_8601_timestamp>` → 해당 시각 이후 메시지만 반환
- 응답: `[{ id, user_id, user_email, content, created_at }]`, created_at ASC 정렬

#### Scenario: Initial message load
- **WHEN** GET /teams/{id}/messages without since parameter
- **THEN** system returns HTTP 200 with up to 50 most recent messages

#### Scenario: Incremental poll
- **WHEN** GET /teams/{id}/messages?since=2026-05-13T14:27:00Z
- **THEN** system returns HTTP 200 with only messages created after that timestamp

#### Scenario: No new messages
- **WHEN** GET /teams/{id}/messages?since=<most recent timestamp>
- **THEN** system returns HTTP 200 with empty array

---

### Requirement: Send Message
POST /teams/{id}/messages는 팀 채팅에 메시지를 전송한다.

- content: 1-1000자 필수 (클라이언트 + 서버 양쪽 검증)
- user_id: 현재 사용자 자동 설정
- 응답: HTTP 201 + `{ id, user_id, user_email, content, created_at }`
- 1000자 초과: HTTP 400 `TOO_LONG`

#### Scenario: Send valid message
- **WHEN** POST /teams/{id}/messages with content 1-1000 chars
- **THEN** system returns HTTP 201 with message object

#### Scenario: Message too long
- **WHEN** POST /teams/{id}/messages with content exceeding 1000 characters
- **THEN** system returns HTTP 400 with error code TOO_LONG and limit/actual fields

#### Scenario: Empty message
- **WHEN** POST /teams/{id}/messages with empty content
- **THEN** system returns HTTP 400 with error code VALIDATION_ERROR

---

### Requirement: Delete Own Message
DELETE /messages/{id}는 본인 메시지만 삭제 가능하다. team owner도 타인 메시지 삭제 불가.

- message.user_id = current_user → 삭제 가능
- 그 외 → HTTP 403 `NOT_OWNER`

#### Scenario: Delete own message
- **WHEN** DELETE /messages/{id} by the message author
- **THEN** system returns HTTP 204

#### Scenario: Delete other's message
- **WHEN** DELETE /messages/{id} by any user other than the message author (including team owner)
- **THEN** system returns HTTP 403 with error code NOT_OWNER

---

### Requirement: Message Delivery Guarantee
POST가 201로 성공한 메시지는 이후 GET에서 반드시 노출된다. DELETE된 메시지는 누락이 아닌 삭제로 간주한다.

#### Scenario: Posted message appears in poll
- **WHEN** POST /teams/{id}/messages returns HTTP 201
- **THEN** subsequent GET /teams/{id}/messages includes that message
