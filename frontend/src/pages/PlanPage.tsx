import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { deletePlan, getPlan, updatePlan, type Plan, type PlanFields } from '../api'
import DateTile from '../components/DateTile'
import Modal from '../components/Modal'
import PlanForm from '../components/PlanForm'
import SlotEditor from '../components/SlotEditor'
import { useTeams } from '../teamContext'
import { useToast } from '../toast'
import { formatDate, formatMinutes, formatTime, toTimeInput } from '../format'

function PlanPage() {
  const { planId } = useParams() // The ":planId" part of the URL /plans/:planId.
  const [plan, setPlan] = useState<Plan | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const navigate = useNavigate()
  const showToast = useToast()
  const { reloadTeams } = useTeams()

  useEffect(() => {
    getPlan(Number(planId))
      .then(setPlan)
      .catch((err: Error) => setError(err.message))
  }, [planId])

  async function handleUpdate(fields: PlanFields) {
    setPlan(await updatePlan(Number(planId), fields))
    setEditing(false)
    void reloadTeams() // The plan may have moved to another team, so session counts change.
    showToast({ message: 'Session details saved' })
  }

  async function handleDelete() {
    if (!plan) return
    try {
      await deletePlan(plan.id)
      void reloadTeams()
      showToast({ message: `Deleted “${plan.title}”` })
      navigate('/plans')
    } catch (err) {
      setError((err as Error).message)
      setConfirmingDelete(false)
    }
  }

  if (error && !plan) {
    return (
      <div className="empty-page">
        <span className="empty-icon">🔍</span>
        <h2>We couldn't find that session</h2>
        <p className="muted">{error}</p>
        <Link to="/plans" className="button">
          Back to sessions
        </Link>
      </div>
    )
  }
  if (!plan) return <div className="loading">Loading session…</div>

  return (
    <>
      <Link to="/plans" className="back">
        ← All sessions
      </Link>

      <header className="hero">
        <DateTile date={plan.date} />
        <div className="hero-text">
          <p className="eyebrow">
            {plan.team.name} · {plan.team.season}
          </p>
          <h1>{plan.title}</h1>
          {plan.focus && <p className="goal-chip">🎯 {plan.focus}</p>}
          <div className="meta">
            <span>🗓 {formatDate(plan.date)}</span>
            <span>
              🕕 {formatTime(plan.start_time)}–{formatTime(plan.end_time)} · {formatMinutes(plan.duration_minutes)}
            </span>
            {plan.location && <span>📍 {plan.location}</span>}
          </div>
          {plan.notes && <p className="notes">{plan.notes}</p>}
        </div>
        <div className="hero-actions">
          <button className="secondary" onClick={() => setEditing(true)}>
            Edit details
          </button>
          <button className="ghost danger-text" onClick={() => setConfirmingDelete(true)}>
            Delete
          </button>
        </div>
      </header>

      {error && <p className="error">{error}</p>}

      <SlotEditor plan={plan} onSaved={setPlan} />

      {editing && (
        <Modal title="Edit session details" onClose={() => setEditing(false)}>
          <PlanForm
            initial={{
              team_id: plan.team.id,
              title: plan.title,
              focus: plan.focus,
              location: plan.location,
              notes: plan.notes,
              date: plan.date,
              start_time: toTimeInput(plan.start_time),
              end_time: toTimeInput(plan.end_time),
            }}
            submitLabel="Save changes"
            onSubmit={handleUpdate}
            onCancel={() => setEditing(false)}
          />
        </Modal>
      )}

      {confirmingDelete && (
        <Modal title="Delete this session?" onClose={() => setConfirmingDelete(false)}>
          <p>
            “{plan.title}” will be deleted. Its drills stay in your library, so nothing else is lost.
          </p>
          <div className="row end">
            <button className="secondary" onClick={() => setConfirmingDelete(false)}>
              Keep it
            </button>
            <button className="danger" onClick={handleDelete}>
              Delete session
            </button>
          </div>
        </Modal>
      )}
    </>
  )
}

export default PlanPage
