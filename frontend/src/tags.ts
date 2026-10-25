// Drill tags. The values must match AgeGroup and Goal in backend/app/schemas.py.

// U.S. Soccer's age groups, each with its game format.
export const AGE_GROUPS = [
  { value: 'u6-u8', label: 'U6–U8', format: '4v4' },
  { value: 'u9-u10', label: 'U9–U10', format: '7v7' },
  { value: 'u11-u12', label: 'U11–U12', format: '9v9' },
  { value: 'u13+', label: 'U13+', format: '11v11' },
] as const

// What a practice (or drill) works on.
export const GOALS = [
  { value: 'warm-up', label: 'Warm-up' },
  { value: 'possession', label: 'Possession' },
  { value: 'attacking', label: 'Attacking' },
  { value: 'finishing', label: 'Finishing' },
  { value: 'defending', label: 'Defending' },
  { value: 'transition', label: 'Transition' },
] as const

// The value types, worked out from the lists above: 'u6-u8' | 'u9-u10' | ...
export type AgeGroup = (typeof AGE_GROUPS)[number]['value']
export type Goal = (typeof GOALS)[number]['value']

export const ageLabel = (value: AgeGroup) => AGE_GROUPS.find((age) => age.value === value)?.label ?? value
export const goalLabel = (value: Goal) => GOALS.find((goal) => goal.value === value)?.label ?? value

// A drill tagged for every age group works at any level, so the app calls it a fundamental.
export const isForAllAges = (ageGroups: AgeGroup[]) => AGE_GROUPS.every((age) => ageGroups.includes(age.value))
