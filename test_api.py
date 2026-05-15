import urllib.request, urllib.error, json, sys

BASE = 'http://localhost:8002'
results = []
token1 = token2 = token3 = team_id = task_id = msg_id = invite = None


def req(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body else None
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    try:
        r = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(r) as res:
            body = res.read()
            return res.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}


def test(name, method, path, body=None, token=None, expect=None):
    code, resp = req(method, path, body, token)
    ok = (expect is None and code < 400) or (code == expect)
    status = "PASS" if ok else "FAIL"
    results.append((status, name, code, None if ok else resp))
    print(f"[{status}] {code} | {name}")
    return resp


print("=== AUTH (9) ===")
r = test("signup 정상", "POST", "/auth/signup", {"email": "u1@t.com", "password": "pass1234"}, expect=201)
token1 = r.get("token")
test("signup 중복이메일", "POST", "/auth/signup", {"email": "u1@t.com", "password": "pass1234"}, expect=409)
test("signup 짧은PW", "POST", "/auth/signup", {"email": "x@x.com", "password": "123"}, expect=400)
test("signup 잘못된이메일", "POST", "/auth/signup", {"email": "notanemail", "password": "pass1234"}, expect=400)
r = test("login 정상", "POST", "/auth/login", {"email": "u1@t.com", "password": "pass1234"}, expect=200)
token1 = r.get("token")
test("login 잘못된PW", "POST", "/auth/login", {"email": "u1@t.com", "password": "wrong"}, expect=401)
test("login 없는이메일", "POST", "/auth/login", {"email": "nobody@t.com", "password": "pass"}, expect=401)
test("GET /auth/me 정상", "GET", "/auth/me", token=token1, expect=200)
test("GET /auth/me 토큰없음", "GET", "/auth/me", expect=401)
test("POST /auth/logout", "POST", "/auth/logout", token=token1, expect=200)

print("\n=== TEAMS (11) ===")
r = test("팀 생성", "POST", "/teams", {"name": "TestTeam"}, token=token1, expect=201)
team_id = r.get("id")
invite = r.get("invite_code", "")
test("팀 생성 이름초과", "POST", "/teams", {"name": "a" * 31}, token=token1, expect=400)

_, r2 = req("POST", "/auth/signup", {"email": "u2@t.com", "password": "pass1234"})
token2 = r2.get("token")
_, r3 = req("POST", "/auth/signup", {"email": "u3@t.com", "password": "pass1234"})
token3 = r3.get("token")

test("초대코드 합류 정상", "POST", "/teams/join", {"invite_code": invite}, token=token2, expect=200)
test("초대코드 합류 이미소속", "POST", "/teams/join", {"invite_code": invite}, token=token2, expect=409)
test("초대코드 없는코드", "POST", "/teams/join", {"invite_code": "ZZZZ-9999"}, token=token3, expect=404)
test("초대코드 형식오류", "POST", "/teams/join", {"invite_code": "invalid"}, token=token3, expect=400)
test(f"GET /teams/{team_id}", "GET", f"/teams/{team_id}", token=token1, expect=200)
test(f"GET /teams/{team_id}/members", "GET", f"/teams/{team_id}/members", token=token1, expect=200)
test("비멤버 팀 접근 403", "GET", f"/teams/{team_id}", token=token3, expect=403)
test("owner 탈퇴 불가 403", "DELETE", f"/teams/{team_id}/leave", token=token1, expect=403)
test("member 탈퇴 정상", "DELETE", f"/teams/{team_id}/leave", token=token2, expect=200)

print("\n=== TASKS (11) ===")
r = test("태스크 생성", "POST", f"/teams/{team_id}/tasks", {"title": "Task 1"}, token=token1, expect=201)
task_id = r.get("id")
test("태스크 생성 빈제목", "POST", f"/teams/{team_id}/tasks", {"title": ""}, token=token1, expect=400)
test("태스크 생성 제목초과", "POST", f"/teams/{team_id}/tasks", {"title": "a" * 101}, token=token1, expect=400)
test("태스크 목록", "GET", f"/teams/{team_id}/tasks", token=token1, expect=200)
test("태스크 @me 필터", "GET", f"/teams/{team_id}/tasks?assignee=me", token=token1, expect=200)
test("태스크 미할당 필터", "GET", f"/teams/{team_id}/tasks?assignee=unassigned", token=token1, expect=200)
test(f"GET /tasks/{task_id}", "GET", f"/tasks/{task_id}", token=token1, expect=200)
test("PATCH status DOING", "PATCH", f"/tasks/{task_id}/status", {"status": "DOING"}, token=token1, expect=200)
test("PATCH status 잘못된값", "PATCH", f"/tasks/{task_id}/status", {"status": "INVALID"}, token=token1, expect=400)
test("PUT 제목수정", "PUT", f"/tasks/{task_id}", {"title": "Updated Task"}, token=token1, expect=200)

req("POST", "/teams/join", {"invite_code": invite}, token3)
test("DELETE 권한없는멤버 403", "DELETE", f"/tasks/{task_id}", token=token3, expect=403)
test("DELETE creator 정상", "DELETE", f"/tasks/{task_id}", token=token1, expect=204)
test("DELETE 삭제된태스크 404", "GET", f"/tasks/{task_id}", token=token1, expect=404)

print("\n=== MESSAGES (7) ===")
test("메시지 목록 초기", "GET", f"/teams/{team_id}/messages", token=token1, expect=200)
r = test("메시지 전송", "POST", f"/teams/{team_id}/messages", {"content": "Hello"}, token=token1, expect=201)
msg_id = r.get("id")
test("메시지 1001자 초과", "POST", f"/teams/{team_id}/messages", {"content": "x" * 1001}, token=token1, expect=400)
test("메시지 빈내용", "POST", f"/teams/{team_id}/messages", {"content": ""}, token=token1, expect=400)
test("since= 폴링", "GET", f"/teams/{team_id}/messages?since=2020-01-01T00:00:00Z", token=token1, expect=200)
test("타인메시지 삭제 403", "DELETE", f"/messages/{msg_id}", token=token3, expect=403)
test("본인메시지 삭제", "DELETE", f"/messages/{msg_id}", token=token1, expect=204)

print("\n=== SECURITY (2) ===")
test("탈퇴후 비멤버 칸반 403", "GET", f"/teams/{team_id}/tasks", token=token2, expect=403)
test("탈퇴후 비멤버 채팅 403", "GET", f"/teams/{team_id}/messages", token=token2, expect=403)

passed = sum(1 for r in results if r[0] == "PASS")
failed = sum(1 for r in results if r[0] == "FAIL")
total = len(results)
print(f"\n{'='*50}")
print(f"총 {total}건 | PASS {passed} | FAIL {failed}")
print('='*50)
if failed:
    print("\nFAIL 상세:")
    for r in results:
        if r[0] == "FAIL":
            err = str(r[3])[:120] if r[3] else ""
            print(f"  [{r[2]}] {r[1]}")
            if err:
                print(f"         -> {err}")
