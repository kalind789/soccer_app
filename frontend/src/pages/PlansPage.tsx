import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { createPlan, listPlans, type PlanFields, type PlanSummary } from '../api'
import PlanForm from '../components/PlanForm'
import { formatDate, formatMinutes, formatTime } from '../format'

function PlansPage() {
  const [plans, setPlans] = useState<PlanSummary[] | null>(null) // null = still loading.
  const [error, setError] = useState<string | null>(null)
  const [adding, setAdding] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    listPlans()
      .then(setPlans)
      .catch((err: Error) => setError(err.message))
  }, [])

  async function handleCreate(fields: PlanFields) {
    const plan = await createPlan(fields)
    navigate(`/plans/${plan.id}`) // Go straight to the new plan to add drills.
  }

  return (
    <section>
      <div className="page-header">
        <div>
          <h1>Session plans</h1>
          <p className="muted">Each practice, with its drills in order.</p>
        </div>
        {!adding && <button onClick={() => setAdding(true)}>New session plan</button>}
      </div>

      {adding && (
        <div className="card">
          <h2>New session plan</h2>
          <PlanForm submitLabel="Create and add drills" onSubmit={handleCreate} onCancel={() => setAdding(false)} />
        </div>
      )}

      {error && <p className="error">{error}</p>}

      {plans?.length === 0 && <p className="empty">No session plans yet. Create your first one.</p>}

      <ul className="list">
        {plans?.map((plan) => (
          <li key={plan.id}>
            <Link to={`/plans/${plan.id}`} className="card card-link">
              <div className="card-row">
                <div>
                  <h3>{plan.title}</h3>
                  {plan.focus && (
                    <p>
                      <span className="label">Goal</span> {plan.focus}
                    </p>
                  )}
                  <p className="muted">
                    {formatDate(plan.date)} · {formatTime(plan.start_time)}–{formatTime(plan.end_time)}
                    {plan.location && ` · ${plan.location}`}
                  </p>
                </div>
                <span className="badge">{formatMinutes(plan.duration_minutes)}</span>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}

export default PlansPage
