# Steps 3 to 5: Drills, session plans, drills in sessions

- **Model (`app/models.py`):** a Python class that *is* a database table. One object = one row. Holds the rules (`archive()`, `check_times()`, `set_drills()`).
- **Schema (`app/schemas.py`):** a Pydantic class describing what the API *accepts* or *returns*. It validates incoming JSON before your code runs.
- **Why both?** The table and the API are different things that change for different reasons. For example, `archived` is returned but never accepted on create, and `duration_minutes` is returned but never stored.
- **Router:** a group of related endpoints (`/drills/...`), plugged into the app with `include_router`.
- **CRUD:** Create, Read, Update, Delete. These are the four basic operations, which map to POST, GET, PATCH, DELETE.
- **PATCH vs PUT:** PATCH changes only the fields you send. PUT replaces the whole thing (our drill list).
- **Status codes we use:** 200 OK, 201 Created, 204 No Content (deleted), 404 Not Found, 405 Method Not Allowed, 422 Unprocessable (bad data or a broken rule).
- **Primary key:** the column that uniquely identifies a row (`id`).
- **Foreign key:** a column that points at another table's primary key (`session_drills.drill_id` → `drills.id`).
- **Link table / many-to-many:** a plan has many drills and a drill is in many plans. `session_drills` sits in between, with an extra `position` column.
- **Relationship:** SQLAlchemy's way of letting you write `plan.slots` or `slot.drill` instead of writing the SQL join yourself.
- **Cascade:** "when the parent is deleted, delete these too". Deleting a plan deletes its slots, but not the drills.
- **Commit / rollback:** commit saves the changes in a database session for good. Rollback throws them away.
- **Custom exception:** `ArchivedDrillError`. The model raises it, and the router turns it into an HTTP 422. The model knows nothing about HTTP.

My notes:
