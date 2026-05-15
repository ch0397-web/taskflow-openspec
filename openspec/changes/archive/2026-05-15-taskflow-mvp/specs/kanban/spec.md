## ADDED Requirements

### Requirement: Task List with Filter
GET /teams/{id}/tasks는 칸반 보드의 태스크 목록을 반환한다. 필터와 정렬을 지원한다.

- 기본: 해당 팀의 모든 태스크, created_at DESC 정렬
- 필터: `?assignee=me` (assignee_id = current_user_id), `?assignee=unassigned` (assignee_id IS NULL)
- 응답: `[{ id, title, status, creator_id, assignee_id, assignee_email, created_at }]`

#### Scenario: Get all tasks
- **WHEN** GET /teams/{id}/tasks with valid team member JWT
- **THEN** system returns HTTP 200 with all tasks sorted by created_at DESC

#### Scenario: Filter my tasks
- **WHEN** GET /teams/{id}/tasks?assignee=me
- **THEN** system returns only tasks where assignee_id equals current_user_id

#### Scenario: Filter unassigned tasks
- **WHEN** GET /teams/{id}/tasks?assignee=unassigned
- **THEN** system returns only tasks where assignee_id IS NULL

---

### Requirement: Task Creation
POST /teams/{id}/tasks는 새 태스크를 생성한다. 초기 상태는 항상 TODO.

- title: 1-100자 필수
- assignee_id: nullable (미할당 가능)
- creator_id: 현재 사용자 자동 설정
- 응답: HTTP 201 + `{ id, title, status: "TODO", creator_id, assignee_id, created_at }`

#### Scenario: Create task with assignee
- **WHEN** POST /teams/{id}/tasks with title and valid assignee_id (team member)
- **THEN** system returns HTTP 201 with task in TODO status

#### Scenario: Create unassigned task
- **WHEN** POST /teams/{id}/tasks with title and no assignee_id
- **THEN** system returns HTTP 201 with task where assignee_id is null

#### Scenario: Title too long
- **WHEN** POST /teams/{id}/tasks with title exceeding 100 characters
- **THEN** system returns HTTP 400 with error code VALIDATION_ERROR

---

### Requirement: Task Status Change
PATCH /tasks/{id}/status는 태스크 상태만 변경한다. 팀 멤버 누구나 가능.

- status: "TODO" | "DOING" | "DONE" 만 허용
- 응답: HTTP 200 + 업데이트된 태스크 객체

#### Scenario: Move task to DOING
- **WHEN** PATCH /tasks/{id}/status with { "status": "DOING" } by any team member
- **THEN** system returns HTTP 200 with task status updated to DOING

#### Scenario: Invalid status value
- **WHEN** PATCH /tasks/{id}/status with invalid status value
- **THEN** system returns HTTP 400 with error code VALIDATION_ERROR

---

### Requirement: Task Update (Title and Assignee)
PUT /tasks/{id}는 태스크 제목과 담당자를 수정한다. 팀 멤버 누구나 가능.

- 수정 가능 필드: title, assignee_id
- 응답: HTTP 200 + 업데이트된 태스크 객체

#### Scenario: Update task title
- **WHEN** PUT /tasks/{id} with new title by any team member
- **THEN** system returns HTTP 200 with updated task

#### Scenario: Update assignee to unassigned
- **WHEN** PUT /tasks/{id} with assignee_id: null
- **THEN** system returns HTTP 200 with task assignee_id set to null

---

### Requirement: Task Detail
GET /tasks/{id}는 태스크 상세 정보를 반환한다.

#### Scenario: Get task detail
- **WHEN** GET /tasks/{id} by a team member
- **THEN** system returns HTTP 200 with full task object including creator and assignee info

---

### Requirement: Task Deletion with Permission Check
DELETE /tasks/{id}는 creator 또는 team owner만 삭제 가능하다. 비권한자는 403.

- creator_id = current_user OR team.owner_id = current_user → 삭제 가능
- 그 외 → HTTP 403 `FORBIDDEN`

#### Scenario: Creator deletes own task
- **WHEN** DELETE /tasks/{id} by the task's creator
- **THEN** system returns HTTP 204

#### Scenario: Team owner deletes any task
- **WHEN** DELETE /tasks/{id} by team owner (even if not creator)
- **THEN** system returns HTTP 204

#### Scenario: Non-creator non-owner attempts deletion
- **WHEN** DELETE /tasks/{id} by team member who is neither creator nor owner
- **THEN** system returns HTTP 403 with error code FORBIDDEN
