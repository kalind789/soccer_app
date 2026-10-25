import { useState, type FormEvent } from 'react'
import type { TeamFields } from '../api'
import { AGE_GROUPS, type AgeGroup } from '../tags'

// While typing, the age group can still be unpicked (''). The select is required, so it's set by submit.
type Draft = { name: string; age_group: AgeGroup | '' }

type Props = {
  initial?: Draft
  submitLabel: string
  onSubmit: (fields: TeamFields) => Promise<void>
  onCancel?: () => void
}

function TeamForm({ initial = { name: '', age_group: '' }, submitLabel, onSubmit, onCancel }: Props) {
  const [fields, setFields] = useState<Draft>(initial)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    try {
      await onSubmit(fields as TeamFields)
      setError(null)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="stack" onSubmit={handleSubmit}>
      <label>
        Team name
        <input
          value={fields.name}
          onChange={(e) => setFields({ ...fields, name: e.target.value })}
          maxLength={100}
          required
          placeholder="e.g. U12 Eagles 2027"
        />
      </label>
      <label>
        Age group
        <select
          value={fields.age_group}
          onChange={(e) => setFields({ ...fields, age_group: e.target.value as AgeGroup })}
          required
        >
          <option value="" disabled>
            Pick an age group
          </option>
          {AGE_GROUPS.map((age) => (
            <option key={age.value} value={age.value}>
              {age.label} ({age.format})
            </option>
          ))}
        </select>
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

export default TeamForm
