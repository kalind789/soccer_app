# Step 12: Teams and seasons

- **One team per season:** "U12 Eagles 2026" and "U12 Eagles 2027" are two rows in `teams`. Next season starts empty, and last season's plans stay where they were.
- **Self-referencing foreign key:** `previous_team_id` points at another row in the *same* table. That's how 2027 knows it continues 2026, like a linked list.
- **`ondelete="SET NULL"`:** if last season's team is deleted, the database clears `previous_team_id` instead of refusing or deleting next season too.
- **Owned through a parent:** a plan has no `owner_id` of its own. You own a plan if you own its team (`plan.team.owner_id`). One fact stored in one place can't get out of sync.
- **One access check:** `get_team_or_404` is the only function that decides who can touch a team. Ticket 003 (several coaches per team) only has to change that one function.
- **Data migration:** the migration made a "My team" for every coach who already had plans, moved the plans into it, and *then* made `team_id` required. Order matters: you can't require a column that's still empty.
- **409 Conflict:** "your request is fine, but the current state says no", e.g. deleting a team that still has plans.
- **React context:** `TeamProvider` loads teams once and shares them with every page through `useTeams()`, so the header switcher and the pages never disagree about which team is selected.
- **localStorage:** a little storage in the browser. It remembers your selected team between visits; if it's blocked, the app falls back to your newest team.

My notes:
