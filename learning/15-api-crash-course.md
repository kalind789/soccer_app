# 15. API crash course

This is a tour of *our* API that teaches the general ideas as they come up. Every example is real code from `backend/app/`. Read it top to bottom, and do the "Try it" boxes as you go.

## 1. What an API is

An **API** (Application Programming Interface) is a promise between two programs: "send me *this*, and I'll answer with *that*." Ours is a **web API**: the programs talk over **HTTP**, the same protocol your browser uses to load pages.

```
 Browser (React, on Vercel)                 Backend (FastAPI, on Render)            Database (Supabase)
 ┌──────────────────────┐   HTTP request    ┌─────────────────────────┐   SQL    ┌────────────┐
 │ src/api.ts  fetch()  │ ────────────────▶ │ routers/ → models.py    │ ───────▶ │  Postgres  │
 │                      │ ◀──────────────── │                         │ ◀─────── │            │
 └──────────────────────┘   HTTP response   └─────────────────────────┘          └────────────┘
         client                                     server
```

- The **client** asks. The **server** answers. A server never calls the client first.
- The frontend never touches the database. Everything goes through the API, so the API is the one place that enforces the rules ("only staff can see a team"). If the rules lived in React, anyone could skip them by calling the database directly.
- `src/api.ts` is the only frontend file that talks to the backend. Read its `request()` function: everything below happens inside that one `fetch()` call.

## 2. A request, piece by piece

Here's what the browser sends when you reorder the drills in a plan:

```http
PUT /session-plans/5/drills?x=1 HTTP/1.1
Host: your-backend.onrender.com
Authorization: Bearer eyJhbGciOiJFUzI1NiIs...
Content-Type: application/json

{"drills": [{"drill_id": 12, "minutes": 15}, {"drill_id": 3, "minutes": 20}]}
```

| Part | Here | What it's for |
|---|---|---|
| **Method** (verb) | `PUT` | *What* to do: read, create, change, delete |
| **Path** | `/session-plans/5/drills` | *Which* thing. `5` is a **path parameter**: it picks one plan |
| **Query string** | `?x=1` | Optional extras after the `?`, like `?include_archived=true` or `?search=rondo`. (`x=1` is only here to show the shape) |
| **Headers** | `Authorization`, `Content-Type` | Information *about* the request: who you are, what format the body is in |
| **Body** | the JSON | The data itself. `GET` and `DELETE` usually have none |

**JSON** (JavaScript Object Notation) is the shared language: text that both TypeScript and Python can read. Python dicts and lists become JSON objects and arrays, and back again.

## 3. A response, piece by piece

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"id": 5, "title": "Pressing triggers", "slots": [...], "planned_minutes": 35, ...}
```

The **status code** is the first thing to read: it says how things went before you read the body.

| Code | Name | Where we send it |
|---|---|---|
| 200 | OK | Most successful reads and edits |
| 201 | Created | `POST /teams`, `POST /session-plans`: something new exists (`status_code=status.HTTP_201_CREATED`) |
| 204 | No Content | `DELETE` endpoints: it worked, and there's nothing to say. `request()` in `api.ts` checks for it, because there's no JSON to read |
| 401 | Unauthorized | No login token, or a forged or expired one (`auth.py`). Really means "unauthenticated: I don't know who you are" |
| 403 | Forbidden | "I know who you are, and you're not allowed": editing a drill idea, or a coach trying to delete the team |
| 404 | Not Found | It doesn't exist, **or it's not yours** (see section 7) |
| 409 | Conflict | The request is fine, but the current state blocks it: deleting a team that still has plans |
| 422 | Unprocessable Content | The data is wrong: a missing field, `minutes: 0`, an end time before the start time |
| 500 | Internal Server Error | A bug on our side. We never send it on purpose |

The rule of thumb: **2xx** = worked, **4xx** = the client's fault (fix the request), **5xx** = the server's fault.

> **Try it:** open the live site, press F12 (DevTools), go to the **Network** tab, then open a team. Click a request like `drills` and look at its Headers (method, status code, `Authorization`) and its Response (the JSON). That's everything in sections 2 and 3, live.

## 4. Resources and REST

Most web APIs follow a style called **REST**: URLs name *things* (nouns, called **resources**), and the method says what to do with them. You don't write `/getDrill?id=3` or `/deleteTeam`; you write `GET /drills/3` and `DELETE /teams/7`.

| Method | Meaning | Ours |
|---|---|---|
| `GET` | Read. Never changes anything | `GET /teams`, `GET /session-plans/5`, `GET /drill-ideas` |
| `POST` | Create something new (or "do an action") | `POST /teams`, `POST /teams/3/drills` |
| `PATCH` | Change *some* fields | `PATCH /drills/12` with only `{"name": "Rondo 4v1"}` |
| `PUT` | *Replace* the whole thing | `PUT /session-plans/5/drills`: the list you send becomes the list |
| `DELETE` | Remove | `DELETE /session-plans/5`, `DELETE /teams/3/members/<user_id>` |

Three things worth noticing in our URLs:

- **Collections and items:** `/session-plans` is all of them (`GET` lists, `POST` adds one); `/session-plans/5` is one of them.
- **Nesting shows ownership:** a team's drills live at `/teams/3/drills`, because a drill belongs to a team. Once a drill exists it also has its own address, `/drills/12`, so you don't need to know its team to edit it.
- **Actions that aren't plain CRUD** become a small sub-resource with `POST`: `POST /drills/12/archive`, `POST /invites/<token>/accept`. Archiving isn't "delete" (the drill stays), so it gets its own verb-like path. Purists argue about this; it's common and clear.

**PATCH vs PUT** is easiest to see in the schemas. `DrillUpdate` (used by `PATCH`) makes every field optional, and the router only changes what was sent:

```python
for field, value in data.model_dump(exclude_none=True).items():
    setattr(drill, field, value)
```

`SessionDrillsUpdate` (used by `PUT`) needs the full list, because it replaces the old one.

**Safe and idempotent:** `GET` is **safe**: calling it never changes data, so the browser may retry it or cache it freely. `PUT` and `DELETE` are **idempotent**: doing them twice ends in the same state as doing them once (send the same drill list twice, and the plan is the same). `POST` usually isn't: `POST /teams` twice makes two teams. That's why the autosave in `SlotEditor` can safely resend the drill list with `PUT`.

## 5. The contract: schemas

The two sides only agree if they agree on the *shape* of the JSON. That shape is the **contract**, and it lives in `schemas.py` (Pydantic) with a hand-made copy in `api.ts` (TypeScript types).

We keep separate shapes for each direction:

| Schema | Direction | Why separate |
|---|---|---|
| `SessionPlanCreate` | client → server | No `id` (the database picks it), but `team_id` is required |
| `SessionPlanUpdate` | client → server | Everything optional, for `PATCH` |
| `SessionPlanSummary` | server → client | Short version for lists, with calculated `duration_minutes` and `planned_minutes` |
| `SessionPlanRead` | server → client | Full version, with `notes` and the `slots` |

Keeping them apart from the SQLAlchemy models means we choose exactly what goes out. Nothing leaks by accident, like a team's `invite_token` in a list of teams.

**Validation** is the contract's guard. FastAPI checks every request body against its schema *before* your function runs. `minutes: int = Field(gt=0)` means `{"minutes": 0}` never reaches `set_plan_drills`: the client gets a 422 that lists what's wrong, and `errorMessage()` in `api.ts` turns that list into the toast you see.

## 6. One request through FastAPI

Here's the endpoint for "show one plan", from `routers/session_plans.py`:

```python
router = APIRouter(prefix="/session-plans", tags=["session plans"])

@router.get("/{plan_id}")
def get_plan(plan_id: int, db: DbSession, user: CurrentUser) -> SessionPlanRead:
    return SessionPlanRead.model_validate(get_plan_or_404(db, plan_id, user))
```

FastAPI reads almost everything from the function's signature:

1. **Routing:** `@router.get("/{plan_id}")` plus the prefix means "`GET /session-plans/<something>` comes here". `main.py` plugs every router into the app with `app.include_router(...)`.
2. **Path parameter:** `plan_id: int` matches `{plan_id}`. The type matters: `GET /session-plans/abc` is a 422, and you never see a string.
3. **Query parameters:** any other simple argument, like `team_id: int | None = None` in `list_plans` or `include_archived: bool = False` in `list_team_drills`, comes from `?team_id=3`. The default makes it optional.
4. **Body:** an argument whose type is a Pydantic model, like `data: SessionDrillsUpdate`, is read from the JSON body and validated.
5. **Dependencies:** `DbSession` and `CurrentUser` are `Annotated[..., Depends(...)]`. FastAPI calls `get_db()` and `get_current_user()` *before* your function and passes in the results. This is **dependency injection**: the endpoint says what it needs, and FastAPI provides it. That's also how the tests swap in an in-memory database and a fake user (`conftest.py` overrides the dependencies).
6. **Response:** the return type `-> SessionPlanRead` tells FastAPI how to turn the result into JSON, and drops any field that isn't in the schema.

Where does the real work go? The routers stay thin: they find the thing, check access, call a method on the model (like `plan.set_drills(...)`), and **translate model exceptions into HTTP errors**:

```python
try:
    plan.set_drills(drills)
except ArchivedDrillError as error:
    raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error))
```

`models.py` knows the soccer rules and nothing about HTTP. The router knows HTTP and nothing about soccer. That split keeps both easy to test.

> **Try it:** run the backend locally (`uv run fastapi dev app/main.py` from `backend/`) and open http://127.0.0.1:8000/docs. FastAPI built that page from the same signatures and schemas. Expand `GET /session-plans/{plan_id}` and compare it with the code above. Calls there will get 401 without a token; `/health` and `/version` work.

## 7. Who's asking? Auth, the API way

HTTP is **stateless**: the server remembers nothing between requests. So every request has to say who it's from. Ours carries a **bearer token**, a JWT that Supabase signed when you logged in:

```
Authorization: Bearer eyJhbGciOiJFUzI1NiIs...
```

"Bearer" means "whoever holds this token is treated as its owner", which is why it must stay secret (and why we use HTTPS). `get_current_user` in `auth.py` checks the signature with Supabase's public key, the expiry, the audience and the issuer. Any failure is a 401, and `request()` in `api.ts` logs you out when it sees one.

Two separate questions, two separate places:

- **Authentication** (who are you?) → `auth.py`, → 401.
- **Authorization** (what may you touch?) → the routers, e.g. `get_team_or_404` and `get_managed_team`, → 404 or 403.

**Why 404 instead of 403 for someone else's team?** A 403 would confirm "team 7 exists, it just isn't yours." Anyone could then count teams by trying ids. A 404 reveals nothing. We only use 403 when you can already *see* the thing (a drill idea, or your own team when you're not the head coach), so it hides nothing.

## 8. CORS: the browser's extra rule

Your browser won't let JavaScript on one **origin** (scheme + host + port, like `https://your-app.vercel.app`) read responses from another origin (like `https://your-backend.onrender.com`) unless the server says it's fine. That rule is the **same-origin policy**, and **CORS** (Cross-Origin Resource Sharing) is how a server says "this origin is fine":

```python
app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_ORIGIN], ...)
```

Before a `PUT` with JSON, the browser even sends a test request first (an `OPTIONS` **preflight**) to ask. Notes:

- CORS only exists in browsers. `curl` and the `/docs` page ignore it. It protects *users* from other websites, not the server from callers. The real protection is still the token.
- That's why `localhost:5173` works but `127.0.0.1:5173` doesn't (a different origin), and why Vercel branch previews don't work (they have their own addresses).

## 9. Try it from the terminal

`curl` is a client too. It sends exactly what you tell it to:

```bash
curl -i https://<your-render-url>/health        # -i shows the status line and headers
curl -i https://<your-render-url>/teams         # 401, with a WWW-Authenticate: Bearer header
```

The second one shows section 7 in action: no token, no data.

## Terms

- **Endpoint:** one method + path pair, like `GET /teams/{team_id}`. One Python function each.
- **Status code:** the three-digit result at the top of a response.
- **Resource:** a thing the API names with a URL (a team, a plan, a drill).
- **Path vs query parameter:** `/teams/3` picks *which* item; `?search=rondo` adjusts *how* to read it.
- **Idempotent:** doing it twice = doing it once.
- **Schema / contract:** the agreed shape of the JSON on both sides.
- **Dependency injection:** the function lists what it needs (`db`, `user`); the framework provides it.
- **Stateless:** each request stands alone; the token says who you are every time.
- **CORS / origin:** the browser's rule about which websites may call which servers.
