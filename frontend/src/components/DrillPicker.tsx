import { useState } from 'react'
import type { Drill, DrillSuggestions } from '../api'
import { drillColor } from '../colors'
import { ageLabel, GOALS, type AgeGroup, type Goal } from '../tags'

type Props = {
  teamName: string
  teamAgeGroup: AgeGroup | null
  teamDrills: Drill[]
  ideas: Drill[]
  suggestions: DrillSuggestions | null
  usedCounts: Map<number, number> // drill id → how many times it's already in this plan.
  onAdd: (drill: Drill) => void
  onCreate: () => void
}

// The "Add drills" panel next to a session plan: suggestions first, then everything else.
function DrillPicker({ teamName, teamAgeGroup, teamDrills, ideas, suggestions, usedCounts, onAdd, onCreate }: Props) {
  const [search, setSearch] = useState('')
  const [goal, setGoal] = useState<Goal | ''>('') // '' = every goal.
  const query = search.trim().toLowerCase()
  const matches = (drill: Drill) => drill.name.toLowerCase().includes(query) && (!goal || drill.goals.includes(goal))

  // Each drill shows up once, in the first section it belongs to.
  const seen = new Set<number>()
  function section(drills: Drill[]): Drill[] {
    const result = drills.filter((drill) => !seen.has(drill.id) && matches(drill))
    result.forEach((drill) => seen.add(drill.id))
    return result
  }
  const timesUsed = new Map(suggestions?.used_before.map((drill) => [drill.id, drill.times_used]))
  const sections = [
    { title: 'Used before', drills: section(suggestions?.used_before ?? []) },
    {
      title: teamAgeGroup ? `Recommended for ${ageLabel(teamAgeGroup)}` : 'Recommended for any age',
      drills: section(suggestions?.recommended ?? []),
    },
    { title: `${teamName}'s drills`, drills: section(teamDrills) },
    { title: 'Drill ideas', drills: section(ideas) },
  ].filter((s) => s.drills.length > 0)

  return (
    <aside className="panel picker">
      <div className="panel-header">
        <h2>Add drills</h2>
        <button className="soft small" onClick={onCreate}>
          + New drill
        </button>
      </div>
      <div className="picker-filters">
        <input
          type="search"
          className="search"
          placeholder="Search drills"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select value={goal} onChange={(e) => setGoal(e.target.value as Goal | '')} aria-label="Works on">
          <option value="">All goals</option>
          {GOALS.map((g) => (
            <option key={g.value} value={g.value}>
              {g.label}
            </option>
          ))}
        </select>
      </div>
      <div className="picker-sections">
        {sections.map(({ title, drills }) => (
          <section key={title}>
            <h3 className="picker-section-title">{title}</h3>
            <ul className="picker-list">
              {drills.map((drill) => (
                <li key={drill.id}>
                  <PickerItem
                    drill={drill}
                    inPlan={usedCounts.get(drill.id) ?? 0}
                    timesUsed={timesUsed.get(drill.id)}
                    onAdd={() => onAdd(drill)}
                  />
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
      {sections.length === 0 && (
        <p className="hint">
          No drill matches.{' '}
          <button className="link" onClick={onCreate}>
            Create a new one
          </button>
        </p>
      )}
    </aside>
  )
}

type ItemProps = { drill: Drill; inPlan: number; timesUsed?: number; onAdd: () => void }

function PickerItem({ drill, inPlan, timesUsed, onAdd }: ItemProps) {
  const note = timesUsed ? `Used in ${timesUsed} ${timesUsed === 1 ? 'session' : 'sessions'}` : drill.objective
  return (
    <button className="picker-item" onClick={onAdd} title={`Add ${drill.name}`}>
      <span className="dot" style={{ background: drillColor(drill.id) }} />
      <span className="picker-text">
        <strong>{drill.name}</strong>
        {note && <small>{note}</small>}
      </span>
      {inPlan > 0 && <span className="pill">{inPlan === 1 ? 'In plan' : `${inPlan}× in plan`}</span>}
      <span className="picker-plus" aria-hidden="true">
        +
      </span>
    </button>
  )
}

export default DrillPicker
