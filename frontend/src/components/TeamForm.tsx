import { useState, type FormEvent } from 'react'
import type { TeamFields } from '../api'

type Props = {
  initial?: TeamFields
  submitLabel: string
  onSubmit: (fields: TeamFields) => Promise<void>
  onCancel?: () => void
}

function TeamForm({ initial = { name: '' }, submitLabel, onSubmit, onCancel }: Props) {
  const [fields, setFields] = useState(initial)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    try {
      await onSubmit(fields)
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
