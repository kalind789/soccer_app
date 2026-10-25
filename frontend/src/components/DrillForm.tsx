import { useState, type FormEvent, type ReactNode } from 'react'
import type { DrillFields } from '../api'
import { AGE_GROUPS, GOALS } from '../tags'
import TagPicker from './TagPicker'

const EMPTY: DrillFields = { name: '', objective: '', description: '', age_groups: [], goals: [] }

type Props = {
  initial?: DrillFields // Leave out for a new drill; pass the drill's values to edit it.
  submitLabel: string
  // The parent decides what saving means (create or update). If it throws, the form shows the error.
  onSubmit: (fields: DrillFields) => Promise<void>
  onCancel?: () => void
  children?: ReactNode // Extra fields to show below the drill's own, like minutes on the plan page.
}

function DrillForm({ initial = EMPTY, submitLabel, onSubmit, onCancel, children }: Props) {
  // One state object for all fields, instead of one useState per field.
  const [fields, setFields] = useState(initial)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  function update(name: 'name' | 'objective' | 'description', value: string) {
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
      <TagPicker
        label="Works on"
        options={GOALS}
        selected={fields.goals}
        onChange={(goals) => setFields({ ...fields, goals })}
      />
      <TagPicker
        label="Age groups"
        options={AGE_GROUPS}
        selected={fields.age_groups}
        onChange={(age_groups) => setFields({ ...fields, age_groups })}
      />
      {children}
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
