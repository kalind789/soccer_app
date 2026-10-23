# Step 6: Drill search (your first ticket)

- **Ticket:** a small, written-down task with a "why", acceptance criteria, and what's out of scope. "Done" means every criterion is met and tested.
- **Query parameter:** the `?search=rondo&include_archived=true` part of a URL. In FastAPI, a function parameter that isn't in the path becomes one. A default (`= None`) makes it optional.
- **`str | None = None`:** "text, or nothing, and nothing if left out". Check it with `if search is not None:`.
- **Building a query:** `select(Drill)` only *writes* SQL. `.where(...)` and `.order_by(...)` add to it and return a new query, so it's `query = query.where(...)`. Nothing reaches the database until `db.scalars(query)`.
- **Stacking filters:** each `.where(...)` adds another condition. A row must pass all of them (SQL `AND`).
- **`ilike`:** case-insensitive pattern match. `%` means "any characters, or none", so `"%rondo%"` means "contains rondo". On SQLite, SQLAlchemy writes it as `lower(name) LIKE lower(...)`.
- **SQL placeholder (`:name_1`):** the search text is sent separately from the SQL, never pasted into it.
- **SQL injection:** an attack where user text gets pasted into SQL and runs as code. Placeholders prevent it.
- **Session factory (`sessionmaker`):** makes database sessions. `TestingSession` is the factory, and `TestingSession()` is one session. Like a cookie cutter and a cookie.
- **Red, then green:** write the test first and watch it fail, then make it pass. The failure proves the test really checks something.

My notes:
