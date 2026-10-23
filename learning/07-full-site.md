# Step 9: Session plans pages and drill times

- **Where data belongs:** "how long does Rondo run?" depends on the session, so the minutes live on the *slot* (`SessionDrill`), not on the `Drill`. The drill stays reusable, with no fixed time.
- **Breaking API change:** `PUT .../drills` went from `{"drill_ids": [1, 2]}` to `{"drills": [{"drill_id": 1, "minutes": 15}]}`. Old callers break, so the frontend and backend change together.
- **`server_default`:** a value the *database* fills in. We used it once in the migration so existing slots got 10 minutes, then removed it so new slots must say their time.
- **Routing / React Router:** different URL, different page. `<Route path="/plans/:planId">` and `useParams()` read the `:planId` part.
- **`Link` / `NavLink`:** go to another page without reloading the whole site. `NavLink` also marks the current page as `active`.
- **`useNavigate`:** move to a page from code, e.g. after creating a plan.
- **Reusing a component:** `DrillForm` does both create and edit. The parent passes `initial` values and an `onSubmit` that decides what saving means.
- **Draft state:** `SlotEditor` edits a copy of the drill list and only sends it when you click Save. That's why there's "Discard changes".
- **Derived values:** `plannedMinutes` is calculated from `rows` every time the page redraws. It's never stored in state, just like `duration_minutes` on the backend.
- **Immutable updates:** `setRows(rows.map(...))` or `[...rows]` make a *new* list instead of changing the old one, so React notices the change.

My notes:
