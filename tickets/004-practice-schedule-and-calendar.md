# 004: Practice schedules and a calendar

**Status:** To do · **Size:** Medium · **Depends on:** nothing. Works better after 002.

## Why

Teams practice on a regular schedule, like every Tuesday and Thursday from 6 to 7:30. Making each session plan by hand is repetitive, and coaches want to see their season at a glance.

## What

Repeating practice schedules, a calendar view, and export to your phone's calendar.

## Acceptance criteria

1. Create a **practice schedule**: days of the week, start and end time, location, and a date range (e.g. Sep 1 to Nov 30).
2. The schedule creates session plans for each practice, which you can then fill with drills. Plans that have drills are never overwritten.
3. You can cancel or move one practice without changing the whole schedule (e.g. a holiday or a rain-out).
4. A **calendar page** shows the month or week, with each practice on its day. Clicking one opens its session plan.
5. Each practice shows whether it's planned yet (it has drills) or still empty.
6. **Export to calendar:** an `.ics` link or file, so practices show up in Google Calendar or Apple Calendar.
7. Tests cover: creating practices from a schedule, skipping a cancelled date, and not overwriting plans that have drills.

## Out of scope

- Two-way sync with Google Calendar (changes made in Google flowing back)
- Games and tournaments (practices only, for now)

## Notes

- Dates and time zones are tricky. Save the time zone with the schedule and test around daylight saving time (early November).
- Look into the `icalendar` Python package for the export.
