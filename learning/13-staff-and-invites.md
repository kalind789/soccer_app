# Step 15: Coaching staff and invite links

- **Many-to-many:** a coach can be on several teams, and a team has several coaches. A link table (`team_members`, one row per coach per team) holds that, like `session_drills` links plans and drills.
- **Composite primary key:** `team_members` has no `id`; the pair `(team_id, user_id)` is the key, so the same coach can't be on the same team twice.
- **Roles:** `head_coach` manages the team, `coach` plans with them. Checked in two helpers: `get_team_or_404` (are you on staff?) and `get_managed_team` (are you the head coach?).
- **Invite token:** `secrets.token_urlsafe(16)` makes 16 random bytes (128 bits), far too many to guess. The link is the password, so it expires after 7 days and can be replaced or turned off.
- **`secrets.compare_digest`:** compares two secrets in the same time no matter where they differ, so an attacker can't learn the token one character at a time from response times.
- **Idempotent:** doing it twice has the same effect as once. Accepting an invite you already accepted changes nothing.
- **Denormalized copy:** a member's name and email are *copied* from their login onto the membership row, because the backend can't read Supabase's users table in tests. It's refreshed each time they list their teams.
- **Data migration, again:** every team's old `owner_id` became a `head_coach` row in `team_members` before the column was dropped.
- **Redirect after login:** `redirectTo: window.location.href` sends someone back to the invite link they opened, after Google or the confirmation email.

My notes:
