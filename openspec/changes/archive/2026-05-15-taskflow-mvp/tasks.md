## 1. ?„ë¡œ?íŠ¸ ì´ˆê¸° ?¤ì •

- [x] 1.1 ?”ë ‰? ë¦¬ êµ¬ì¡° ?ì„± (`backend/`, `frontend/`, `frontend/js/`, `vercel.json`) + `.gitignore` ?‘ì„± (`.env`, `taskflow.db`, `__pycache__/`, `*.pyc`, `*.pyo`)
- [x] 1.2 ë°±ì—”???˜ì¡´???¤ì¹˜ + `requirements.txt` ?‘ì„± (`fastapi`, `uvicorn`, `sqlalchemy`, `aiosqlite`, `asyncpg`, `python-jose[cryptography]`, `bcrypt`, `python-dotenv`, `mangum`)
- [x] 1.3 ë¡œì»¬ `.env` ?Œì¼ ?‘ì„± ??`SECRET_KEY` ?ì„± (`openssl rand -hex 32`), `DATABASE_URL=sqlite+aiosqlite:///./taskflow.db`
- [x] 1.4 `backend/main.py` ?ì„± ??FastAPI ?? CORSMiddleware ?¤ì • (localhost:* + *.vercel.app)
- [x] 1.5 `backend/database.py` ??SQLAlchemy async ?”ì§„, DATABASE_URL ?˜ê²½ë³€?˜ë¡œ SQLite/Neon ?„í™˜, SQLite ?¬ìš© ??`PRAGMA foreign_keys = ON` ?´ë²¤??ë¦¬ìŠ¤???±ë¡
- [x] 1.6 `backend/models.py` ??ORM ëª¨ë¸ 4ê°??•ì˜ (users, teams, tasks, messages) + ?¸ë±??(`tasks.team_id+created_at`, `messages.team_id+created_at`, `teams.invite_code`, `users.team_id`)
- [x] 1.7 DB ?Œì´ë¸??ë™ ?ì„± (`create_all` on startup) ?•ì¸

## 2. ?¸ì¦ API (Auth 4ê°?

- [x] 2.1 `POST /auth/signup` ???´ë©”???•ì‹ ê²€ì¦? bcrypt ?´ì‹±, users INSERT, JWT ë°œê¸‰ (201)
- [x] 2.2 `POST /auth/login` ???´ë©”??ë¹„ë?ë²ˆí˜¸ ê²€ì¦? JWT ë°œê¸‰ (200), ?¤íŒ¨ ??401 INVALID_CREDENTIALS
- [x] 2.3 JWT ë¯¸ë“¤?¨ì–´ (`get_current_user` ?˜ì¡´?? ??Bearer ? í° ê²€ì¦? ë§Œë£Œ ??401 TOKEN_EXPIRED
- [x] 2.4 `GET /auth/me` ???„ì¬ ?¬ìš©???•ë³´ ë°˜í™˜
- [x] 2.5 `POST /auth/logout` ??200ë§?ë°˜í™˜ (stateless)
- [x] 2.6 ?ëŸ¬ ?‘ë‹µ ?œì?????ëª¨ë“  4xx/5xx??`{ error: { code, message } }` ?•íƒœ ?ìš©

## 3. ?€ API (Team 5ê°?

- [x] 3.1 `POST /teams` ???€ ?ì„±, invite_code ?ë™ ?ì„± (`AAAA-9999` ?•ì‹), owner_id=current_user, users.team_id UPDATE (201)
- [x] 3.2 `POST /teams/join` ??ì´ˆë?ì½”ë“œ ?•ì‹ ê²€ì¦? ?€ ì¡°íšŒ, users.team_id UPDATE; 404/409 ì²˜ë¦¬
- [x] 3.3 `GET /teams/{id}` ???€ ?•ë³´ ë°˜í™˜, ë¹„ë©¤ë²?403 FORBIDDEN
- [x] 3.4 `GET /teams/{id}/members` ??ë©¤ë²„ ëª©ë¡ ë°˜í™˜ (is_owner ?„ë“œ ?¬í•¨)
- [x] 3.5 `DELETE /teams/{id}/leave` ??ë³¸ì¸ ?ˆí‡´, users.team_id=NULL; owner??403

## 4. ì¹¸ë°˜ API (Task 6ê°?

- [x] 4.1 `GET /teams/{id}/tasks` ???œìŠ¤??ëª©ë¡, `?assignee=me|unassigned` ?„í„°, created_at DESC ?•ë ¬
- [x] 4.2 `POST /teams/{id}/tasks` ???œìŠ¤???ì„±, title(1-100??, assignee_id nullable, status=TODO (201)
- [x] 4.3 `GET /tasks/{id}` ???œìŠ¤???ì„¸ (creator_email, assignee_email ?¬í•¨)
- [x] 4.4 `PATCH /tasks/{id}/status` ???íƒœë§?ë³€ê²?(TODO|DOING|DONE), ?€ ë©¤ë²„ ?„êµ¬??ê°€??- [x] 4.5 `PUT /tasks/{id}` ??title + assignee_id ?˜ì •, ?€ ë©¤ë²„ ?„êµ¬??ê°€??- [x] 4.6 `DELETE /tasks/{id}` ??creator ?ëŠ” team ownerë§? ê·???403 FORBIDDEN

## 5. ì±„íŒ… API (Chat 3ê°?

- [x] 5.1 `GET /teams/{id}/messages` ??ë©”ì‹œì§€ ëª©ë¡, `?since=ISO_timestamp` ì¦ë¶„ ì¡°íšŒ, ê¸°ë³¸ ìµœê·¼ 50ê°?- [x] 5.2 `POST /teams/{id}/messages` ??ë©”ì‹œì§€ ?„ì†¡, content 1-1000??(?´ë¼+?œë²„ ê²€ì¦?; ì´ˆê³¼ ??400 TOO_LONG
- [x] 5.3 `DELETE /messages/{id}` ??ë³¸ì¸ ë©”ì‹œì§€ë§??? œ; ?€??403 NOT_OWNER

## 6. ?„ë¡ ?¸ì—”????ê³µí†µ ? í‹¸ë¦¬í‹°

- [x] 6.1 `frontend/js/api.js` ?ì„± ??`API_BASE_URL` ?¤ì • (ë¡œì»¬: `http://localhost:8000`, ?´ì˜: `/api`), `apiFetch()` ?˜í¼ (Authorization ?¤ë” ?ë™ ì²¨ë?, 401 ?‘ë‹µ ??localStorage ?•ë¦¬ ??login.html redirect)
- [x] 6.2 `frontend/js/auth.js` ?ì„± ??`getToken()`, `getTeamId()`, `setSession(token, teamId)`, `clearSession()` (localStorage ?? `tf_token`, `tf_team_id`)

## 7. ?„ë¡ ?¸ì—”????ë¡œê·¸???Œì›ê°€??(login.html)

- [x] 7.1 `frontend/login.html` ?ì„± ??Tailwind CDN, ë¡œê·¸???Œì›ê°€????UI
- [x] 7.2 ?Œì›ê°€???????´ë©”???•ì‹ + ë¹„ë?ë²ˆí˜¸ 8???´ë¼?´ì–¸??ê²€ì¦?- [x] 7.3 `POST /auth/signup` ?¸ì¶œ ??`setSession(token, team_id)` ??team_id NULL?´ë©´ team.html, ?ˆìœ¼ë©?kanban.html redirect
- [x] 7.4 `POST /auth/login` ?¸ì¶œ ??`setSession(token, team_id)` ??team_id ë¶„ê¸° redirect
- [x] 7.5 ?ëŸ¬ ë©”ì‹œì§€ ?¸ë¼???œì‹œ (EMAIL_TAKEN, INVALID_CREDENTIALS)
- [x] 7.6 ?´ë? ë¡œê·¸???íƒœ(`getToken()` ì¡´ì¬)ë©?kanban.htmlë¡??ë™ redirect

## 8. ?„ë¡ ?¸ì—”?????€ ? íƒ (team.html)

- [x] 8.1 `frontend/team.html` ?ì„± ??? í° ?†ìœ¼ë©?login.html redirect
- [x] 8.2 ?€ ë§Œë“¤ê¸??????€ ?´ë¦„ ?…ë ¥, `POST /teams` ?¸ì¶œ, ?±ê³µ ??`tf_team_id` ?€????ì´ˆë?ì½”ë“œ ?œì‹œ + ë³µì‚¬ ë²„íŠ¼
- [x] 8.3 ì´ˆë?ì½”ë“œ ?©ë¥˜ ?????•ì‹ ê²€ì¦??´ë¼ `^[A-Z]{4}-[0-9]{4}$`), `POST /teams/join` ?¸ì¶œ, ?±ê³µ ??`tf_team_id` ?€??- [x] 8.4 ?©ë¥˜/?ì„± ?±ê³µ ??kanban.html redirect, ?ëŸ¬ ì¼€?´ìŠ¤ ?¸ë¼???œì‹œ

## 9. ?„ë¡ ?¸ì—”????ì¹¸ë°˜ (kanban.html)

- [x] 9.1 `frontend/kanban.html` ?ì„± ??? í° + team_id ?†ìœ¼ë©?redirect
- [x] 9.2 3ì»¬ëŸ¼ ?ˆì´?„ì›ƒ (TODO/DOING/DONE), `GET /teams/{id}/tasks` ë¡œë“œ (`tf_team_id` ?¬ìš©)
- [x] 9.3 ?„í„° ??(?„ì²´/@me/ë¯¸í• ?? ???´ë¼?´ì–¸???„í„°ë§?- [x] 9.4 ê°?ì»¬ëŸ¼ `+` ë²„íŠ¼ ???¸ë¼???…ë ¥ ????`POST /teams/{id}/tasks`
- [x] 9.5 HTML5 Drag & Drop ??dragstart/dragover/drop ?´ë²¤?? drop ??`PATCH /tasks/{id}/status`
- [x] 9.6 ì¹´ë“œ ?´ë¦­ ???˜ì • ëª¨ë‹¬ ???œëª©/?íƒœ/assignee ?˜ì •, `PUT /tasks/{id}` ?¸ì¶œ
- [x] 9.7 ?? œ ë²„íŠ¼ ???•ì¸ ?¤ì´?¼ë¡œê·? `DELETE /tasks/{id}`, ê¶Œí•œ ?†ìœ¼ë©?ë²„íŠ¼ ?¨ê?
- [x] 9.8 ?¤ë” ?¤ë¹„ê²Œì´??(ì¹¸ë°˜/ì±„íŒ… ?????˜ì´ì§€ ?´ë™) + ë©¤ë²„ ë²„íŠ¼ ???°ì¸¡ ?¬ì´???¨ë„ ? ê? (`GET /teams/{id}/members` ë¡œë“œ)
- [x] 9.9 ë¡œê·¸?„ì›ƒ ë²„íŠ¼ ??`clearSession()` ??login.html redirect
- [x] 9.10 ëª¨ë°”??ë°˜ì‘????breakpoint <768px?ì„œ 1ì»¬ëŸ¼ ?¤ì??´í”„ (Tailwind sm: ?´ë˜??

## 10. ?„ë¡ ?¸ì—”????ì±„íŒ… (chat.html)

- [x] 10.1 `frontend/chat.html` ?ì„± ??? í° + team_id ?†ìœ¼ë©?redirect
- [x] 10.2 ë©”ì‹œì§€ ëª©ë¡ ?Œë”ë§???ë³¸ì¸/?€??ë§í’??êµ¬ë¶„, ë°œì‹ ???œê° ?œì‹œ
- [x] 10.3 ì´ˆê¸° ë¡œë“œ `GET /teams/{id}/messages` (ìµœê·¼ 50ê°?, ?´í›„ 5ì´?`setInterval` ?´ë§
- [x] 10.4 since= ?Œë¼ë¯¸í„° ì¦ë¶„ ?´ë§ ??ë§ˆì?ë§?ë©”ì‹œì§€ created_at ì¶”ì 
- [x] 10.5 ë©”ì‹œì§€ ?…ë ¥ì°???1000??ì¹´ìš´?? ì´ˆê³¼ ???„ì†¡ ë²„íŠ¼ ë¹„í™œ?±í™”
- [x] 10.6 `POST /teams/{id}/messages` ?„ì†¡, ?„ì†¡ ??ì¦‰ì‹œ ëª©ë¡ ê°±ì‹ 
- [x] 10.7 ë³¸ì¸ ë©”ì‹œì§€ hover ???? œ ?„ì´ì½? `DELETE /messages/{id}` ?¸ì¶œ
- [x] 10.8 ?¤íŠ¸?Œí¬ ?Šê? ?œì‹œ ???´ë§ ?¤íŒ¨ ??"?°ê²° ?Šê?" ë°°ë„ˆ, exponential backoff ?¬ì‹œ??(5s??0s??0s??0s??0s)

## 11. ë°°í¬ ?¤ì •

- [x] 11.1 `api/index.py` ?ì„± ??`mangum` ?¼ë¡œ FastAPI ?±ì„ ASGI?’WSGI ?¸ë“¤?¬ë¡œ ?˜í•‘ (`handler = Mangum(app)`)
- [x] 11.2 `vercel.json` ?‘ì„± ??`@vercel/python` ë¹Œë“œ ?¤ì •, `/api/(.*)` ??`api/index.py` ?¼ìš°??- [x] 11.3 `requirements.txt` Vercel ë£¨íŠ¸???„ì¹˜ ?•ì¸ (Python ?°í????˜ì¡´???¸ì‹??
- [x] 11.4 Vercel ?„ë¡œ?íŠ¸ ?°ê²° (`vercel link`), ?˜ê²½ë³€???¤ì • (`DATABASE_URL` Neon URL, `SECRET_KEY`)
- [x] 11.5 Neon ?°ì´?°ë² ?´ìŠ¤ ?ì„±, `DATABASE_URL` pooled connection string ë³µì‚¬ ??Vercel??ì£¼ì…
- [x] 11.6 `git push origin main` ??Vercel ?ë™ ë°°í¬ ?•ì¸
- [x] 11.7 ë°°í¬??URL?ì„œ ?Œì›ê°€?????€ ?ì„± ??ì¹¸ë°˜ ??ì±„íŒ… ?„ì²´ ?ë¦„ ?˜ë™ ê²€ì¦?
