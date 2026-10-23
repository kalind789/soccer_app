# 003: Teams and email invites

**Status:** To do · **Size:** Medium · **Depends on:** 002 (users and auth)

## Why

A club usually has several coaches for one team. They need to share one drill library and plan sessions together.

## What

Teams that own drills and plans, and email invites to join a team.

## Acceptance criteria

1. A user can create a team. Drills and session plans belong to a team, not just to one user.
2. Roles: **owner** (can invite, remove members, and delete the team) and **coach** (can edit drills and plans).
3. An owner invites someone by email. They get a link that expires after 7 days and can only be used once.
4. Opening the link: if you're logged in, you join the team; if not, you sign up or log in first, then join.
5. An owner can see pending invites, cancel one, and remove members.
6. Authorization: only team members can see a team's drills and plans, and only owners can invite.
7. Tests cover: a valid invite, an expired invite, a used invite, a non-owner trying to invite (403), and a non-member trying to read the team's data (404).

## Out of scope

- Player or parent accounts (coaches only for now)
- Belonging to several teams with separate libraries, unless it turns out easy

## Notes

- Store a **random token** in the invite link, never the user id or email.
- Sending email: check whether Supabase can do it, or use a service like Resend. Test with a fake email sender.
