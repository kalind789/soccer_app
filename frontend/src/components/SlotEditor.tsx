import { useEffect, useMemo, useRef, useState } from 'react'
import {
  closestCenter,
  DndContext,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import {
  createTeamDrill,
  getDrillSuggestions,
  listDrillIdeas,
  listTeamDrills,
  setPlanDrills,
  type Drill,
  type DrillFields,
  type DrillSuggestions,
  type Plan,
  type SlotEntry,
} from '../api'
import { drillColor } from '../colors'
import { formatMinutes } from '../format'
import DrillForm from './DrillForm'
import DrillPicker from './DrillPicker'
import Modal from './Modal'
import Timeline from './Timeline'

// One row in the editor. `key` tells React (and drag-and-drop) which row is which,
// even when the same drill appears twice. `minutes` is a string while the coach types.
type Row = { key: number; drill: Drill; minutes: string }

const START_MINUTES = '10' // Where a newly added drill starts. The coach changes it right away.
const SAVE_DELAY_MS = 600 // Wait until the coach stops typing for this long, then save.

let nextKey = 1
const toRows = (plan: Plan): Row[] =>
  plan.slots.map((slot) => ({ key: nextKey++, drill: slot.drill, minutes: String(slot.minutes) }))

const isValidMinutes = (minutes: string) => Number.isInteger(Number(minutes)) && Number(minutes) > 0
const toEntries = (rows: Row[]): SlotEntry[] => rows.map((r) => ({ drill_id: r.drill.id, minutes: Number(r.minutes) }))

type SaveStatus = 'saved' | 'saving' | 'invalid' | 'error'

type Props = {
  plan: Plan
  onSaved: (plan: Plan) => void
}

function SlotEditor({ plan, onSaved }: Props) {
  const [rows, setRows] = useState(() => toRows(plan))
  const [teamDrills, setTeamDrills] = useState<Drill[]>([])
  const [ideas, setIdeas] = useState<Drill[]>([])
  const [suggestions, setSuggestions] = useState<DrillSuggestions | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)
  const [createdMinutes, setCreatedMinutes] = useState('')
  const [focusKey, setFocusKey] = useState<number | null>(null) // The row whose minutes box gets focus.

  const teamId = plan.team.id
  useEffect(() => {
    // Three requests at once. Archived drills are left out: the backend won't let them be newly added.
    Promise.all([listTeamDrills(teamId), listDrillIdeas(), getDrillSuggestions(teamId)])
      .then(([own, allIdeas, suggested]) => {
        setTeamDrills(own)
        setIdeas(allIdeas)
        setSuggestions(suggested)
      })
      .catch((err: Error) => setError(err.message))
  }, [teamId])

  // --- Autosave ---
  // Everything about saving is worked out from two facts: what the rows say now,
  // and what the server last confirmed (savedSignature). Rows are compared as JSON text.
  const allValid = rows.every((row) => isValidMinutes(row.minutes))
  const signature = JSON.stringify(toEntries(rows))
  const [savedSignature, setSavedSignature] = useState(signature)
  const [saveError, setSaveError] = useState<string | null>(null)
  const status: SaveStatus = !allValid
    ? 'invalid'
    : signature === savedSignature
      ? 'saved'
      : saveError
        ? 'error'
        : 'saving'

  // Changes waiting for the timer. If the coach leaves the page first, they're saved on the way out.
  const pendingRef = useRef<SlotEntry[] | null>(null)
  const saveCount = useRef(0) // Only the newest save's answer counts, if two overlap.
  const onSavedRef = useRef(onSaved)
  useEffect(() => {
    onSavedRef.current = onSaved
  })

  useEffect(() => {
    if (!allValid || signature === savedSignature) {
      pendingRef.current = null
      return
    }
    const entries: SlotEntry[] = JSON.parse(signature)
    pendingRef.current = entries
    const timer = window.setTimeout(async () => {
      pendingRef.current = null
      const thisSave = ++saveCount.current
      try {
        const saved = await setPlanDrills(plan.id, entries)
        if (thisSave === saveCount.current) {
          setSavedSignature(JSON.stringify(entries))
          setSaveError(null)
          onSavedRef.current(saved)
        }
      } catch (err) {
        if (thisSave === saveCount.current) setSaveError((err as Error).message)
      }
    }, SAVE_DELAY_MS)
    return () => window.clearTimeout(timer) // A newer change restarts the wait.
  }, [signature, savedSignature, allValid, plan.id])

  useEffect(() => {
    // Leaving the page (unmount): don't lose changes that were still waiting for the timer.
    return () => {
      if (pendingRef.current) void setPlanDrills(plan.id, pendingRef.current)
    }
  }, [plan.id])

  // --- Editing ---
  function setMinutes(key: number, minutes: string) {
    setRows((current) => current.map((row) => (row.key === key ? { ...row, minutes } : row)))
  }

  function remove(key: number) {
    setRows((current) => current.filter((row) => row.key !== key))
  }

  function add(drill: Drill, minutes = START_MINUTES) {
    const key = nextKey++
    setRows((current) => [...current, { key, drill, minutes }])
    setFocusKey(key)
  }

  async function createAndAdd(fields: DrillFields) {
    // Saved to the team's drills right away. If it fails, DrillForm shows why.
    const drill = await createTeamDrill(teamId, fields)
    setTeamDrills((current) => [...current, drill].sort((a, b) => a.name.localeCompare(b.name)))
    add(drill, createdMinutes)
    setCreating(false)
    setCreatedMinutes('')
  }

  // --- Drag and drop ---
  const sensors = useSensors(
    // Only start dragging after the pointer moves 4px, so a plain click on the handle isn't a drag.
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
    // Keyboard: focus the handle, press Space, move with the arrow keys, press Space again.
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  function handleDragEnd({ active, over }: DragEndEvent) {
    if (!over || active.id === over.id) return
    setRows((current) => {
      const from = current.findIndex((row) => row.key === active.id)
      const to = current.findIndex((row) => row.key === over.id)
      return arrayMove(current, from, to)
    })
  }

  const plannedMinutes = rows.reduce((total, row) => total + (Number(row.minutes) || 0), 0)
  const leftOver = plan.duration_minutes - plannedMinutes
  const usedCounts = useMemo(() => {
    const counts = new Map<number, number>()
    for (const row of rows) counts.set(row.drill.id, (counts.get(row.drill.id) ?? 0) + 1)
    return counts
  }, [rows])

  return (
    <div className="editor">
      <section className="panel session">
        <div className="panel-header">
          <div>
            <h2>Session flow</h2>
            <p className={leftOver < 0 ? 'time-summary over' : 'time-summary'}>
              <strong>{formatMinutes(plannedMinutes)}</strong> of {formatMinutes(plan.duration_minutes)}
              {leftOver > 0 && ` · ${formatMinutes(leftOver)} free`}
              {leftOver < 0 && ` · ${formatMinutes(-leftOver)} over`}
            </p>
          </div>
          <SaveBadge status={status} />
        </div>

        <Timeline
          segments={rows.map((row) => ({
            key: row.key,
            drillId: row.drill.id,
            name: row.drill.name,
            minutes: Number(row.minutes) || 0,
          }))}
          sessionMinutes={plan.duration_minutes}
        />

        {rows.length === 0 ? (
          <div className="empty-flow">
            <span className="empty-icon">📋</span>
            <p>
              <strong>No drills yet</strong>
            </p>
            <p className="muted">Pick drills from the panel to build the session.</p>
          </div>
        ) : (
          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
            <SortableContext items={rows.map((row) => row.key)} strategy={verticalListSortingStrategy}>
              <ol className="slots">
                {rows.map((row, index) => (
                  <SlotRow
                    key={row.key}
                    row={row}
                    number={index + 1}
                    autoFocus={row.key === focusKey}
                    onMinutes={(minutes) => setMinutes(row.key, minutes)}
                    onRemove={() => remove(row.key)}
                  />
                ))}
              </ol>
            </SortableContext>
          </DndContext>
        )}
        {(error || saveError) && <p className="error">{error || saveError}</p>}
      </section>

      <DrillPicker
        teamName={plan.team.name}
        teamAgeGroup={plan.team.age_group}
        teamDrills={teamDrills}
        ideas={ideas}
        suggestions={suggestions}
        usedCounts={usedCounts}
        onAdd={(drill) => add(drill)}
        onCreate={() => setCreating(true)}
      />

      {creating && (
        <Modal title="New drill" onClose={() => setCreating(false)}>
          <p className="muted">It's saved to {plan.team.name}'s drills too, so you can reuse it in other sessions.</p>
          <DrillForm submitLabel="Create and add to session" onSubmit={createAndAdd} onCancel={() => setCreating(false)}>
            <label>
              Minutes in this session
              <input
                type="number"
                min={1}
                value={createdMinutes}
                onChange={(e) => setCreatedMinutes(e.target.value)}
                placeholder="15"
                required
              />
            </label>
          </DrillForm>
        </Modal>
      )}
    </div>
  )
}

function SaveBadge({ status }: { status: SaveStatus }) {
  const text = { saved: '✓ Saved', saving: 'Saving…', invalid: 'Fix minutes to save', error: 'Not saved' }[status]
  return <span className={`save-badge ${status}`}>{text}</span>
}

type SlotRowProps = {
  row: Row
  number: number
  autoFocus: boolean
  onMinutes: (minutes: string) => void
  onRemove: () => void
}

function SlotRow({ row, number, autoFocus, onMinutes, onRemove }: SlotRowProps) {
  const { attributes, listeners, setNodeRef, setActivatorNodeRef, transform, transition, isDragging } = useSortable({
    id: row.key,
  })
  const [open, setOpen] = useState(false) // Show the drill's description?
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (autoFocus) {
      inputRef.current?.focus()
      inputRef.current?.select() // So typing a number replaces the starting value.
      inputRef.current?.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
    }
  }, [autoFocus])

  // −/+ jump to the next multiple of 5 (12 → 15 → 20), and never below 1.
  const current = Number(row.minutes) || 0
  const down = Math.max(1, Math.ceil(current / 5) * 5 - 5)
  const up = Math.floor(current / 5) * 5 + 5
  const valid = isValidMinutes(row.minutes)

  return (
    <li
      ref={setNodeRef}
      className={isDragging ? 'slot dragging' : 'slot'}
      style={{ transform: CSS.Transform.toString(transform), transition, borderLeftColor: drillColor(row.drill.id) }}
    >
      <button
        ref={setActivatorNodeRef}
        className="drag-handle"
        aria-label={`Drag to reorder ${row.drill.name}`}
        {...attributes}
        {...listeners}
      >
        ⠿
      </button>
      <span className="slot-number">{number}</span>
      <div className="slot-drill">
        <button className="slot-name" onClick={() => setOpen(!open)} aria-expanded={open}>
          {row.drill.name}
          {row.drill.archived && <span className="pill">Archived</span>}
        </button>
        {row.drill.objective && <p className="muted small-text">{row.drill.objective}</p>}
        {open && (
          <p className="slot-description">{row.drill.description || "No description yet. Add one on the team's Drills tab."}</p>
        )}
      </div>
      <div className={valid ? 'stepper' : 'stepper invalid'}>
        <button onClick={() => onMinutes(String(down))} aria-label="Less time" disabled={current <= 1}>
          −
        </button>
        <input
          ref={inputRef}
          type="number"
          min={1}
          value={row.minutes}
          onChange={(e) => onMinutes(e.target.value)}
          aria-label={`Minutes for ${row.drill.name}`}
        />
        <span className="stepper-unit">min</span>
        <button onClick={() => onMinutes(String(up))} aria-label="More time">
          +
        </button>
      </div>
      <button className="ghost icon remove" onClick={onRemove} aria-label={`Remove ${row.drill.name}`}>
        ✕
      </button>
    </li>
  )
}

export default SlotEditor
