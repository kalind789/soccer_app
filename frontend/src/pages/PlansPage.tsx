import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { createPlan, createTeam, listPlans, type PlanFields, type PlanSummary, type TeamFields } from '../api'
import DateTile from '../components/DateTile'
import Modal from '../components/Modal'
import PlanForm from '../components/PlanForm'
import TeamForm from '../components/TeamForm'
import { formatMinutes, formatTime } from '../format'
import { useTeams } from '../teamContext'

function todayString(): string {
  const now = new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
}

function PlansPage() {
  const { teams, selectedTeam, selectTeam, reloadTeams } = useTeams()
  const [plans, setPlans] = useState<PlanSummary[] | null>(null) // null = still loading.
  const [error, setError] = useState<string | null>(null)
  const [adding, setAdding] = useState(false)
  const navigate = useNavigate()
  const teamId = selectedTeam?.id

  // Load the selected team's plans, again whenever the coach switches team.
  useEffect(() => {
    if (teamId === undefined) return
    let ignore = false // Switching teams quickly: only show the latest team's plans.
    listPlans(teamId)
      .then((result) => {
        if (!ignore) {
          setPlans(result)
          setError(null)
        }
      })
      .catch((err: Error) => {
        if (!ignore) setError(err.message)
      })
    return () => {
      ignore = true
    }
  }, [teamId])

  async function handleCreate(fields: PlanFields) {
    const plan = await createPlan(fields)
    void reloadTeams() // Session counts changed.
    navigate(`/plans/${plan.id}`) // Go straight to the new plan to add drills.
  }

  async function handleCreateTeam(fields: TeamFields) {
    const team = await createTeam(fields)
    await reloadTeams()
    selectTeam(team.id)
  }

  if (teams?.length === 0) {
    return (
      <div className="welcome">
        <span className="empty-icon">🛡️</span>
        <h1>Start with a team</h1>
        <p className="muted">
          Session plans belong to a team, like “U12 Eagles 2027”. You can add more teams anytime.
        </p>
        <div className="panel">
          <TeamForm submitLabel="Create team" onSubmit={handleCreateTeam} />
        </div>
      </div>
    )
  }
  if (!selectedTeam) return <div className="loading">Loading…</div>

  // Dates are "YYYY-MM-DD" text, which sorts and compares correctly as plain strings.
  const today = todayString()
  const upcoming = plans?.filter((plan) => plan.date >= today) ?? []
  const past = (plans?.filter((plan) => plan.date < today) ?? []).reverse() // Most recent first.

  return (
    <>
      <div className="page-header">
        <div>
          <p className="eyebrow">{selectedTeam.name}</p>
          <h1>Sessions</h1>
          <p className="muted">Plan each practice, drill by drill.</p>
        </div>
        <button onClick={() => setAdding(true)}>+ New session</button>
      </div>

      {error && <p className="error">{error}</p>}
      {!plans && !error && <div className="loading">Loading sessions…</div>}

      {plans?.length === 0 && (
        <div className="empty-page">
          <span className="empty-icon">⚽</span>
          <h2>Plan {selectedTeam.name}'s first practice</h2>
          <p className="muted">Pick a date and time, then drop in drills from your library.</p>
          <button onClick={() => setAdding(true)}>+ New session</button>
        </div>
      )}

      {upcoming.length > 0 && <PlanGroup title="Upcoming" plans={upcoming} />}
      {past.length > 0 && <PlanGroup title="Past" plans={past} muted />}

      {adding && (
        <Modal title="New session" onClose={() => setAdding(false)}>
          <PlanForm submitLabel="Create and add drills" onSubmit={handleCreate} onCancel={() => setAdding(false)} />
        </Modal>
      )}
    </>
  )
}

function PlanGroup({ title, plans, muted = false }: { title: string; plans: PlanSummary[]; muted?: boolean }) {
  return (
    <section className="group">
      <h2 className="group-title">
        {title} <span className="count">{plans.length}</span>
      </h2>
      <ul className="plan-list">
        {plans.map((plan) => (
          <li key={plan.id}>
            <PlanCard plan={plan} muted={muted} />
          </li>
        ))}
      </ul>
    </section>
  )
}

function PlanCard({ plan, muted }: { plan: PlanSummary; muted: boolean }) {
  const percent = Math.min(plan.planned_minutes / plan.duration_minutes, 1) * 100
  const over = plan.planned_minutes > plan.duration_minutes

  return (
    <Link to={`/plans/${plan.id}`} className={muted ? 'plan-card past' : 'plan-card'}>
      <DateTile date={plan.date} muted={muted} />
      <div className="plan-card-body">
        <h3>{plan.title}</h3>
        {plan.focus && <p className="goal-line">🎯 {plan.focus}</p>}
        <p className="muted small-text">
          {formatTime(plan.start_time)}–{formatTime(plan.end_time)}
          {plan.location && ` · ${plan.location}`}
        </p>
        <div className="progress" aria-label={`${plan.planned_minutes} of ${plan.duration_minutes} minutes planned`}>
          <div className={over ? 'progress-fill over' : 'progress-fill'} style={{ width: `${percent}%` }} />
        </div>
        <p className="small-text muted">
          {plan.drill_count === 0
            ? 'No drills yet'
            : `${plan.drill_count} ${plan.drill_count === 1 ? 'drill' : 'drills'} · ${formatMinutes(plan.planned_minutes)} of ${formatMinutes(plan.duration_minutes)}`}
        </p>
      </div>
      <span className="chevron" aria-hidden="true">
        ›
      </span>
    </Link>
  )
}

export default PlansPage
