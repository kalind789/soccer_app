import { useEffect, useState, type FormEvent } from 'react'
import { createDrill, listDrills, setPlanDrills, type Drill, type DrillFields, type Plan } from '../api'
import { formatMinutes } from '../format'
import DrillForm from './DrillForm'

// One row in the editor. `key` tells React which row is which, even when the same drill appears twice.
// `minutes` is a string while the coach types, so the box can be empty for a moment.
type Row = { key: number; drill: Drill; minutes: string }

let nextKey = 1
const toRows = (plan: Plan): Row[] =>
  plan.slots.map((slot) => ({ key: nextKey++, drill: slot.drill, minutes: String(slot.minutes) }))

const isValidMinutes = (minutes: string) => Number.isInteger(Number(minutes)) && Number(minutes) > 0

type Props = {
  plan: Plan
  onSaved: (plan: Plan) => void
}

function SlotEditor({ plan, onSaved }: Props) {
  // A draft copy of the drill list. Nothing is saved until the coach clicks Save.
  const [rows, setRows] = useState(() => toRows(plan))
  const [library, setLibrary] = useState<Drill[]>([])
  const [newDrillId, setNewDrillId] = useState('')
  const [newMinutes, setNewMinutes] = useState('')
  const [creating, setCreating] = useState(false) // Is the "new drill" form open?
  const [createdMinutes, setCreatedMinutes] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    // Archived drills are left out: the backend won't let them be newly added.
    listDrills()
      .then(setLibrary)
      .catch((err: Error) => setError(err.message))
  }, [])

  const plannedMinutes = rows.reduce((total, row) => total + (Number(row.minutes) || 0), 0)
  const leftOver = plan.duration_minutes - plannedMinutes
  const changed =
    JSON.stringify(rows.map((r) => [r.drill.id, Number(r.minutes)])) !==
    JSON.stringify(plan.slots.map((s) => [s.drill.id, s.minutes]))
  const allValid = rows.every((row) => isValidMinutes(row.minutes))

  function setMinutes(key: number, minutes: string) {
    setRows(rows.map((row) => (row.key === key ? { ...row, minutes } : row)))
  }

  function move(index: number, by: -1 | 1) {
    const copy = [...rows]
    ;[copy[index], copy[index + by]] = [copy[index + by], copy[index]] // Swap the two rows.
    setRows(copy)
  }

  function remove(key: number) {
    setRows(rows.filter((row) => row.key !== key))
  }

  function add(event: FormEvent) {
    event.preventDefault()
    const drill = library.find((d) => d.id === Number(newDrillId))
    if (!drill) return
    setRows([...rows, { key: nextKey++, drill, minutes: newMinutes }])
    setNewDrillId('')
    setNewMinutes('')
  }

  // Save the drill to the library right away, then add it to this plan's draft list.
  async function createAndAdd(fields: DrillFields) {
    const drill = await createDrill(fields) // If this fails, DrillForm shows the error.
    setLibrary([...library, drill].sort((a, b) => a.name.localeCompare(b.name)))
    setRows([...rows, { key: nextKey++, drill, minutes: createdMinutes }])
    setCreating(false)
    setCreatedMinutes('')
  }

  async function save() {
    setSaving(true)
    try {
      const entries = rows.map((row) => ({ drill_id: row.drill.id, minutes: Number(row.minutes) }))
      const saved = await setPlanDrills(plan.id, entries)
      setRows(toRows(saved))
      setError(null)
      onSaved(saved)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="card stack">
      <div className="card-row">
        <h2>Drills</h2>
        <p className={leftOver < 0 ? 'time-summary over' : 'time-summary'}>
          {formatMinutes(plannedMinutes)} planned of {formatMinutes(plan.duration_minutes)}
          {leftOver > 0 && ` · ${formatMinutes(leftOver)} free`}
          {leftOver < 0 && ` · ${formatMinutes(-leftOver)} over`}
        </p>
      </div>

      {rows.length === 0 ? (
        <p className="empty">No drills yet. Add one below.</p>
      ) : (
        <ol className="slots">
          {rows.map((row, index) => (
            <li key={row.key} className="slot">
              <span className="slot-number">{index + 1}</span>
              <div className="slot-drill">
                <strong>{row.drill.name}</strong>
                {row.drill.archived && <span className="badge">Archived</span>}
                {row.drill.objective && <p className="muted">{row.drill.objective}</p>}
              </div>
              <label className="minutes">
                <input
                  type="number"
                  min={1}
                  value={row.minutes}
                  onChange={(e) => setMinutes(row.key, e.target.value)}
                  aria-label={`Minutes for ${row.drill.name}`}
                  className={isValidMinutes(row.minutes) ? '' : 'invalid'}
                />
                min
              </label>
              <div className="row">
                <button className="icon" onClick={() => move(index, -1)} disabled={index === 0} title="Move up">
                  ↑
                </button>
                <button
                  className="icon"
                  onClick={() => move(index, 1)}
                  disabled={index === rows.length - 1}
                  title="Move down"
                >
                  ↓
                </button>
                <button className="icon" onClick={() => remove(row.key)} title="Remove from plan">
                  ✕
                </button>
              </div>
            </li>
          ))}
        </ol>
      )}

      <form className="add-slot" onSubmit={add}>
        <select value={newDrillId} onChange={(e) => setNewDrillId(e.target.value)} required>
          <option value="">Add a drill…</option>
          {library.map((drill) => (
            <option key={drill.id} value={drill.id}>
              {drill.name}
            </option>
          ))}
        </select>
        <label className="minutes">
          <input
            type="number"
            min={1}
            value={newMinutes}
            onChange={(e) => setNewMinutes(e.target.value)}
            placeholder="15"
            aria-label="Minutes for the new drill"
            required
          />
          min
        </label>
        <button type="submit" className="secondary">
          Add
        </button>
        {!creating && (
          <button type="button" className="secondary" onClick={() => setCreating(true)}>
            + New drill
          </button>
        )}
      </form>
      {library.length === 0 && !creating && (
        <p className="muted">Your drill library is empty. Use “New drill” to make one.</p>
      )}

      {creating && (
        <div className="card nested">
          <h3>New drill</h3>
          <p className="muted">It's saved to your drill library, so you can reuse it in other sessions.</p>
          <DrillForm submitLabel="Create and add to session" onSubmit={createAndAdd} onCancel={() => setCreating(false)}>
            <label className="minutes">
              <input
                type="number"
                min={1}
                value={createdMinutes}
                onChange={(e) => setCreatedMinutes(e.target.value)}
                placeholder="15"
                aria-label="Minutes in this session"
                required
              />
              min in this session
            </label>
          </DrillForm>
        </div>
      )}

      {error && <p className="error">{error}</p>}
      {changed && (
        <div className="row save-bar">
          <button onClick={save} disabled={saving || !allValid}>
            {saving ? 'Saving…' : 'Save drills'}
          </button>
          <button className="secondary" onClick={() => setRows(toRows(plan))}>
            Discard changes
          </button>
          {!allValid && <span className="error">Every drill needs at least 1 minute.</span>}
        </div>
      )}
    </div>
  )
}

export default SlotEditor
