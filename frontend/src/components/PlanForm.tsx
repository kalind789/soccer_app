import { useState, type FormEvent } from 'react'
import type { PlanFields } from '../api'
import { useTeams } from '../teamContext'

function today(): string {
  const now = new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
}

const EMPTY: Omit<PlanFields, 'team_id'> = {
  title: '',
  focus: '',
  location: '',
  notes: '',
  date: today(),
  start_time: '18:00',
  end_time: '19:30',
}

type Props = {
  initial?: PlanFields // Leave out for a new plan (in the selected team); pass the plan's values to edit it.
  submitLabel: string
  onSubmit: (fields: PlanFields) => Promise<void>
  onCancel?: () => void
}

function PlanForm({ initial, submitLabel, onSubmit, onCancel }: Props) {
  const { teams, selectedTeam } = useTeams()
  const [fields, setFields] = useState<PlanFields>(initial ?? { ...EMPTY, team_id: selectedTeam?.id ?? 0 })
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  function update(name: Exclude<keyof PlanFields, 'team_id'>, value: string) {
    setFields({ ...fields, [name]: value })
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    try {
      await onSubmit(fields)
      setError(null)
    } catch (err) {
      // For example "end_time must be after start_time", straight from the backend's rule.
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="stack" onSubmit={handleSubmit}>
      <label>
        Team
        <select
          value={fields.team_id || ''}
          onChange={(e) => setFields({ ...fields, team_id: Number(e.target.value) })}
          required
        >
          <option value="" disabled>
            Pick a team
          </option>
          {teams?.map((team) => (
            <option key={team.id} value={team.id}>
              {team.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Title
        <input
          value={fields.title}
          onChange={(e) => update('title', e.target.value)}
          maxLength={100}
          required
          placeholder="e.g. U12 Tuesday training"
        />
      </label>
      <label>
        Goal
        <input
          value={fields.focus}
          onChange={(e) => update('focus', e.target.value)}
          maxLength={200}
          placeholder="What is this session about?"
        />
      </label>
      <div className="grid-3">
        <label>
          Date
          <input type="date" value={fields.date} onChange={(e) => update('date', e.target.value)} required />
        </label>
        <label>
          Start
          <input
            type="time"
            value={fields.start_time}
            onChange={(e) => update('start_time', e.target.value)}
            required
          />
        </label>
        <label>
          End
          <input type="time" value={fields.end_time} onChange={(e) => update('end_time', e.target.value)} required />
        </label>
      </div>
      <label>
        Location
        <input
          value={fields.location}
          onChange={(e) => update('location', e.target.value)}
          maxLength={200}
          placeholder="e.g. Field 3"
        />
      </label>
      <label>
        Notes
        <textarea value={fields.notes} onChange={(e) => update('notes', e.target.value)} rows={3} />
      </label>
      {error && <p className="error">{error}</p>}
      <div className="row">
        <button type="submit" disabled={saving}>
          {saving ? 'Saving…' : submitLabel}
        </button>
        {onCancel && (
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}

export default PlanForm
