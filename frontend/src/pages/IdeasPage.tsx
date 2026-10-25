import { useEffect, useState } from 'react'
import { listDrillIdeas, type Drill } from '../api'
import { drillColor } from '../colors'
import DrillTags from '../components/DrillTags'
import Modal from '../components/Modal'
import { AGE_GROUPS, GOALS, type AgeGroup, type Goal } from '../tags'

// The starter library that comes with the app. Ideas can't be edited, but any team can use them
// in a session: they show up in the "Add drills" panel.
function IdeasPage() {
  const [ideas, setIdeas] = useState<Drill[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [age, setAge] = useState<AgeGroup | null>(null) // null = every age group.
  const [goal, setGoal] = useState<Goal | null>(null) // null = every goal.
  const [open, setOpen] = useState<Drill | null>(null)

  useEffect(() => {
    listDrillIdeas()
      .then(setIdeas)
      .catch((err: Error) => setError(err.message))
  }, [])

  // Only a couple dozen ideas, so the filtering happens right here.
  const shown = (ideas ?? []).filter(
    (idea) => (!age || idea.age_groups.includes(age)) && (!goal || idea.goals.includes(goal)),
  )

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Drill ideas</h1>
          <p className="muted">
            Proven drills for every age, organized the way U.S. Soccer plans practice. Use any of them in a session.
          </p>
        </div>
      </div>

      <div className="filters">
        <FilterRow
          label="Age group"
          options={AGE_GROUPS.map((a) => ({ value: a.value, label: `${a.label} · ${a.format}` }))}
          value={age}
          onChange={setAge}
        />
        <FilterRow label="Works on" options={GOALS} value={goal} onChange={setGoal} />
      </div>

      {error && <p className="error">{error}</p>}
      {!ideas && !error && <div className="loading">Loading drill ideas…</div>}
      {ideas && shown.length === 0 && (
        <div className="empty-page">
          <span className="empty-icon">🔍</span>
          <h2>No drill ideas match both filters</h2>
          <button
            className="secondary"
            onClick={() => {
              setAge(null)
              setGoal(null)
            }}
          >
            Show all
          </button>
        </div>
      )}

      <ul className="drill-grid">
        {shown.map((idea) => (
          <li key={idea.id} className="drill-card">
            <button className="drill-card-main" onClick={() => setOpen(idea)} title="Read the full drill">
              <span className="drill-card-stripe" style={{ background: drillColor(idea.id) }} />
              <h3>{idea.name}</h3>
              {idea.objective && <p className="goal-line">🎯 {idea.objective}</p>}
              <DrillTags drill={idea} />
            </button>
          </li>
        ))}
      </ul>

      {open && (
        <Modal title={open.name} onClose={() => setOpen(null)}>
          {open.objective && <p className="goal-line">🎯 {open.objective}</p>}
          <DrillTags drill={open} />
          <p className="idea-description">{open.description}</p>
          <p className="hint">To use it, open a session and find it under “Drill ideas” in the Add drills panel.</p>
        </Modal>
      )}
    </>
  )
}

type FilterProps<T extends string> = {
  label: string
  options: readonly { value: T; label: string }[]
  value: T | null
  onChange: (value: T | null) => void
}

// "All" plus one chip per option; picking one shows only matching ideas.
function FilterRow<T extends string>({ label, options, value, onChange }: FilterProps<T>) {
  return (
    <div className="filter-row" role="group" aria-label={label}>
      <span className="filter-label">{label}</span>
      <div className="chips">
        <button className="chip" aria-pressed={value === null} onClick={() => onChange(null)}>
          All
        </button>
        {options.map((option) => (
          <button
            key={option.value}
            className="chip"
            aria-pressed={value === option.value}
            onClick={() => onChange(value === option.value ? null : option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  )
}

export default IdeasPage
