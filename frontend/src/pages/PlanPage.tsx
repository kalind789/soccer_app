import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { deletePlan, getPlan, updatePlan, type Plan, type PlanFields } from '../api'
import PlanForm from '../components/PlanForm'
import SlotEditor from '../components/SlotEditor'
import { formatDate, formatMinutes, formatTime, toTimeInput } from '../format'

function PlanPage() {
  const { planId } = useParams() // The ":planId" part of the URL /plans/:planId.
  const [plan, setPlan] = useState<Plan | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    getPlan(Number(planId))
      .then(setPlan)
      .catch((err: Error) => setError(err.message))
  }, [planId])

  async function handleUpdate(fields: PlanFields) {
    setPlan(await updatePlan(Number(planId), fields))
    setEditing(false)
  }

  async function handleDelete() {
    if (!plan || !confirm(`Delete "${plan.title}"? Its drills stay in your library.`)) return
    try {
      await deletePlan(plan.id)
      navigate('/plans')
    } catch (err) {
      setError((err as Error).message)
    }
  }

  if (error && !plan) {
    return (
      <section>
        <p className="error">{error}</p>
        <Link to="/plans">← Back to session plans</Link>
      </section>
    )
  }
  if (!plan) return <p className="muted">Loading…</p>

  return (
    <section>
      <Link to="/plans" className="back">
        ← Session plans
      </Link>

      {editing ? (
        <div className="card">
          <h2>Edit session details</h2>
          <PlanForm
            initial={{
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
        </div>
      ) : (
        <div className="page-header">
          <div>
            <h1>{plan.title}</h1>
            {plan.focus && (
              <p className="goal">
                <span className="label">Goal</span> {plan.focus}
              </p>
            )}
            <p className="muted">
              {formatDate(plan.date)} · {formatTime(plan.start_time)}–{formatTime(plan.end_time)} (
              {formatMinutes(plan.duration_minutes)}){plan.location && ` · ${plan.location}`}
            </p>
            {plan.notes && <p className="pre-line">{plan.notes}</p>}
          </div>
          <div className="row">
            <button className="secondary" onClick={() => setEditing(true)}>
              Edit details
            </button>
            <button className="danger" onClick={handleDelete}>
              Delete
            </button>
          </div>
        </div>
      )}

      {error && <p className="error">{error}</p>}

      <SlotEditor plan={plan} onSaved={setPlan} />
    </section>
  )
}

export default PlanPage
