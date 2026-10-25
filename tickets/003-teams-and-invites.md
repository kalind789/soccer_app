# 003: Shared teams and invites

**Status:** Done (2026-10-25), with a shareable link instead of email · **Size:** Medium · **Depends on:** 002 (users and auth)

## Why

A club usually has several coaches for one team. They need to plan that team's sessions together.

## Already done

Teams exist (just a name). Each team has a single owner, the coach who made it, and session plans belong to a team. Each team has its own drills, and every team can use the built-in drill ideas. This ticket adds more coaches to a team.

## What

Team members with roles, and email invites to join a team.

## Acceptance criteria

1. ✅ A team has members, not just an owner. Access is a membership check in one place: `get_team_or_404`.
2. ✅ Roles: **head coach** (edits and deletes the team, manages the invite link, removes coaches) and **coach** (plans sessions, edits drills, can leave).
3. ✅ Changed: instead of one email per person, the head coach shares **one invite link** (in a text, email, or group chat). It works for 7 days, for anyone who opens it. A new link or "Turn off" makes the old one stop working. The user chose "a link or something"; no email service needed.
4. ✅ Opening the link: logged in, you see "Join <team>"; not logged in, you log in or sign up first and come back to the same link.
5. ✅ The head coach sees the current link, replaces or turns it off, and removes coaches.
6. ✅ Authorization: only staff can see a team's plans and drills (404 otherwise); only the head coach can manage (403 for coaches).
7. ✅ Tests (`tests/test_staff.py`): valid, wrong, expired, replaced and turned-off links; coach tries to manage (403); outsider (404); leave; remove; head coach can't leave (409).

## Out of scope

- Player or parent accounts (coaches only for now)

## Notes

- Store a **random token** in the invite link, never the user id or email.
- Later, maybe: one-person, single-use email invites (Supabase can send email, or Resend), and handing the head coach role to someone else.
