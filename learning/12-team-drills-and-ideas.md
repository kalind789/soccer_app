# Step 14: Team drills, tags and drill ideas

- **Nullable foreign key as a flag:** `drills.team_id` points at a team, or is empty (`NULL`). Empty means "drill idea": one table holds both kinds, so a plan's slots can point at either.
- **Seed data in a migration:** the 24 drill ideas are written inside a migration with `op.bulk_insert`. Every database (yours, Supabase, a teammate's) gets the same ideas just by running `alembic upgrade head`.
- **JSON column:** `age_groups` and `goals` are short lists stored as JSON text, e.g. `["u9-u10", "u11-u12"]`. Simpler than a tags table; the trade-off is that filtering by tag in SQL is awkward, so the browser does it.
- **`Literal` types:** `Literal["warm-up", "possession", ...]` makes Pydantic reject any other value with a 422, so bad tags never reach the database.
- **403 vs 404, again:** someone else's drill is a 404 (don't reveal it exists). A drill idea is visible to everyone, so refusing to edit it is an honest 403.
- **`GROUP BY` and `COUNT`:** the suggestions query joins drills → slots → plans, groups by drill, and counts slots: "how many times did this team use each drill?" Then it sorts by that count.
- **Nested routes:** `/teams/3`, `/teams/3/drills` and `/teams/3/sessions/7` put everything about a team under its URL. `NavLink end` makes "Sessions" active only on exactly `/teams/3`.
- **Generic component (`<T extends string>`):** `TagPicker` and `FilterRow` work for both age groups and goals, and TypeScript still knows which values are allowed.
- **Play–Practice–Play:** U.S. Soccer's grassroots session shape: start with a game, practice a topic, finish with a game. "Scrimmage in Your Game Format" is the idea for the two Play parts.

My notes:
