// Each drill gets its own color, picked from its id, so it looks the same on every page.
const DRILL_COLORS = ['#6366f1', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#8b5cf6', '#14b8a6']

export function drillColor(drillId: number): string {
  return DRILL_COLORS[drillId % DRILL_COLORS.length]
}
