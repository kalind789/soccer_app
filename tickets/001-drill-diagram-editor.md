# 001: Drag-and-drop drill diagrams

**Status:** To do · **Size:** Large · **Depends on:** nothing

## Why

Coaches explain drills with a picture: where the players stand, where the cones go, and who passes to whom. Text alone is slow to read at the field.

## What

Each drill gets a diagram, built by dragging pieces onto a pitch.

## Acceptance criteria

1. A drill's edit form has a diagram editor: a pitch (full, half, or a grid area) you can drag pieces onto.
2. Pieces: players for two teams (two colors), cones, balls, goals, and coach/neutral players.
3. Arrows using common coaching symbols: **solid = pass, dashed = run without the ball, wavy = dribble.**
4. You can move, delete, and undo pieces.
5. The diagram is saved as **JSON data** (e.g. `{"type": "cone", "x": 30, "y": 50}`), not as an image, so it stays editable. It needs a migration for the new column.
6. The diagram shows as a small preview on drill cards and in session plans.
7. It works with touch on a phone or tablet, not just a mouse.
8. Backend tests check the diagram is saved and read back, and that bad shapes are rejected (422).

## Out of scope

- Uploading photos of diagrams (you chose drag-and-drop instead)
- Animating the diagram

## Notes

- I couldn't find a published official US Soccer symbol key. If you have one from a license course, match it.
- Check the `<svg>` drag libraries first (e.g. `react-konva`, or plain SVG with pointer events) before writing it from scratch.
