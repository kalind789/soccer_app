# 003: Shared teams and email invites

**Status:** To do · **Size:** Medium · **Depends on:** 002 (users and auth)

## Why

A club usually has several coaches for one team. They need to plan that team's sessions together.

## Already done

Teams exist (just a name). Each team has a single owner, the coach who made it, and session plans belong to a team. Each team has its own drills, and every team can use the built-in drill ideas. This ticket adds more coaches to a team.

## What

Team members with roles, and email invites to join a team.

## Acceptance criteria

1. A team has members, not just an owner. Replace `Team.owner_id` checks with a membership check (one place: `get_team_or_404`).
2. Roles: **owner** (can invite, remove members, and delete the team) and **coach** (can edit drills and plans).
3. An owner invites someone by email. They get a link that expires after 7 days and can only be used once.
4. Opening the link: if you're logged in, you join the team; if not, you sign up or log in first, then join.
5. An owner can see pending invites, cancel one, and remove members.
6. Authorization: only team members can see a team's plans and drills, and only owners can invite.
7. Tests cover: a valid invite, an expired invite, a used invite, a non-owner trying to invite (403), and a non-member trying to read the team's data (404).

## Out of scope

- Player or parent accounts (coaches only for now)

## Notes

- Store a **random token** in the invite link, never the user id or email.
- Sending email: check whether Supabase can do it, or use a service like Resend. Test with a fake email sender.
