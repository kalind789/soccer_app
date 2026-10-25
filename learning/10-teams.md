# Step 12: Teams and a shared drill library

- **A team is just a name:** "U12 Eagles 2026" and "U12 Eagles 2027" are two unrelated rows in `teams`. A new year is a new team that starts empty.
- **Owned through a parent:** a plan has no `owner_id` of its own. You own a plan if you own its team (`plan.team.owner_id`). One fact stored in one place can't get out of sync.
- **One access check:** `get_team_or_404` is the only function that decides who can touch a team. Ticket 003 (several coaches per team) only has to change that one function.
- **Shared library:** drills have no owner at all, so every coach sees the same drills. Fewer columns, fewer checks.
- **Dropping columns in a migration:** the "shared drill library and simpler teams" migration removed `drills.owner_id`, `teams.season` and `teams.previous_team_id`. Dropped data can't come back, so the downgrade fills in placeholders.
- **Data migration:** the earlier teams migration made a "My team" for every coach who already had plans, moved the plans into it, and *then* made `team_id` required. Order matters: you can't require a column that's still empty.
- **409 Conflict:** "your request is fine, but the current state says no", e.g. deleting a team that still has plans.
- **React context:** `TeamProvider` loads teams once and shares them with every page through `useTeams()`, so the header switcher and the pages never disagree about which team is selected.
- **localStorage:** a little storage in the browser. It remembers your selected team between visits; if it's blocked, the app falls back to the first team.

My notes:
