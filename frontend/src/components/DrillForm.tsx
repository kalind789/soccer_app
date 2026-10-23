import { useState, type FormEvent } from 'react'
import type { DrillFields } from '../api'

const EMPTY: DrillFields = { name: '', objective: '', description: '' }

type Props = {
  initial?: DrillFields // Leave out for a new drill; pass the drill's values to edit it.
  submitLabel: string
  // The parent decides what saving means (create or update). If it throws, the form shows the error.
  onSubmit: (fields: DrillFields) => Promise<void>
  onCancel?: () => void
}

function DrillForm({ initial = EMPTY, submitLabel, onSubmit, onCancel }: Props) {
  // One state object for all fields, instead of one useState per field.
  const [fields, setFields] = useState(initial)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  function update(name: keyof DrillFields, value: string) {
    setFields({ ...fields, [name]: value }) // Copy everything, then replace one field.
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault() // Stop the browser from reloading the page, its default for forms.
    setSaving(true)
    try {
      await onSubmit(fields)
      setError(null)
      if (initial === EMPTY) setFields(EMPTY) // Clear the form after creating, ready for the next drill.
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="stack" onSubmit={handleSubmit}>
      <label>
        Name
        <input value={fields.name} onChange={(e) => update('name', e.target.value)} maxLength={100} required />
      </label>
      <label>
        Goal
        <input
          value={fields.objective}
          onChange={(e) => update('objective', e.target.value)}
          placeholder="What should players get better at?"
        />
      </label>
      <label>
        Description
        <textarea
          value={fields.description}
          onChange={(e) => update('description', e.target.value)}
          rows={4}
          placeholder="Setup, rules, progressions, coaching points"
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

export default DrillForm
