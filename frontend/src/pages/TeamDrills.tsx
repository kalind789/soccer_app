import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import {
  archiveDrill,
  createTeamDrill,
  listTeamDrills,
  unarchiveDrill,
  updateDrill,
  type Drill,
  type DrillFields,
  type Team,
} from '../api'
import { drillColor } from '../colors'
import DrillForm from '../components/DrillForm'
import DrillTags from '../components/DrillTags'
import Modal from '../components/Modal'
import { useToast } from '../toast'

// The Drills tab of a team's page: the team's own drill library.
function TeamDrills({ team }: { team: Team }) {
  const [drills, setDrills] = useState<Drill[] | null>(null) // null = still loading.
  const [search, setSearch] = useState('')
  const [includeArchived, setIncludeArchived] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState<Drill | null>(null) // The drill open in the edit window.
  const [adding, setAdding] = useState(false)
  // Bumping this number makes the effect below run again, which reloads the list.
  const [reloadCount, setReloadCount] = useState(0)
  const showToast = useToast()

  // Load the drills whenever the search, the toggle, or reloadCount changes.
  useEffect(() => {
    // If the user types fast, an older request can finish after a newer one.
    // `ignore` makes sure only the latest answer is shown.
    let ignore = false
    listTeamDrills(team.id, search, includeArchived)
      .then((result) => {
        if (!ignore) {
          setDrills(result)
          setError(null)
        }
      })
      .catch((err: Error) => {
        if (!ignore) setError(err.message)
      })
    return () => {
      ignore = true
    }
  }, [team.id, search, includeArchived, reloadCount])

  function reload() {
    setReloadCount((count) => count + 1)
  }

  async function handleCreate(fields: DrillFields) {
    const drill = await createTeamDrill(team.id, fields)
    setAdding(false)
    reload()
    showToast({ message: `Added “${drill.name}” to ${team.name}'s drills` })
  }

  async function handleUpdate(fields: DrillFields) {
    if (!editing) return
    await updateDrill(editing.id, fields)
    setEditing(null)
    reload()
    showToast({ message: 'Drill saved. Every session using it is updated.' })
  }

  async function setArchived(drill: Drill, archived: boolean) {
    try {
      await (archived ? archiveDrill(drill.id) : unarchiveDrill(drill.id))
      reload()
      showToast({
        message: archived ? `Archived “${drill.name}”` : `Restored “${drill.name}”`,
        action: { label: 'Undo', run: () => void setArchived(drill, !archived) },
      })
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <>
      <div className="tab-header">
        <p className="muted">This team's own drills. Edits show up in every session that uses the drill.</p>
        <button onClick={() => setAdding(true)}>+ New drill</button>
      </div>

      <div className="toolbar">
        <input
          type="search"
          className="search"
          placeholder="Search drills"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="segmented" role="group" aria-label="Which drills to show">
          <button className={includeArchived ? '' : 'active'} onClick={() => setIncludeArchived(false)}>
            Active
          </button>
          <button className={includeArchived ? 'active' : ''} onClick={() => setIncludeArchived(true)}>
            Include archived
          </button>
        </div>
      </div>

      {error && <p className="error">{error}</p>}
      {!drills && !error && <div className="loading">Loading drills…</div>}

      {drills?.length === 0 &&
        (search ? (
          <div className="empty-page">
            <span className="empty-icon">🔍</span>
            <h2>No drills match “{search}”</h2>
            <button className="secondary" onClick={() => setSearch('')}>
              Clear search
            </button>
          </div>
        ) : (
          <div className="empty-page">
            <span className="empty-icon">🧩</span>
            <h2>No drills of your own yet</h2>
            <p className="muted">
              Add the drills you run most, or start from the <Link to="/ideas">drill ideas</Link>. You can use those
              in any session as they are.
            </p>
            <button onClick={() => setAdding(true)}>+ New drill</button>
          </div>
        ))}

      <ul className="drill-grid">
        {drills?.map((drill) => (
          <li key={drill.id} className={drill.archived ? 'drill-card archived' : 'drill-card'}>
            <button className="drill-card-main" onClick={() => setEditing(drill)} title="Edit drill">
              <span className="drill-card-stripe" style={{ background: drillColor(drill.id) }} />
              <h3>
                {drill.name}
                {drill.archived && <span className="pill">Archived</span>}
              </h3>
              {drill.objective && <p className="goal-line">🎯 {drill.objective}</p>}
              <DrillTags drill={drill} />
              <p className="drill-card-description">{drill.description || 'No description yet.'}</p>
            </button>
            <div className="drill-card-actions">
              <button className="ghost small" onClick={() => setEditing(drill)}>
                Edit
              </button>
              <button className="ghost small" onClick={() => setArchived(drill, !drill.archived)}>
                {drill.archived ? 'Restore' : 'Archive'}
              </button>
            </div>
          </li>
        ))}
      </ul>

      {adding && (
        <Modal title="New drill" onClose={() => setAdding(false)}>
          <DrillForm submitLabel="Add drill" onSubmit={handleCreate} onCancel={() => setAdding(false)} />
        </Modal>
      )}

      {editing && (
        <Modal title="Edit drill" onClose={() => setEditing(null)}>
          <DrillForm
            initial={{
              name: editing.name,
              objective: editing.objective,
              description: editing.description,
              age_groups: editing.age_groups,
              goals: editing.goals,
            }}
            submitLabel="Save changes"
            onSubmit={handleUpdate}
            onCancel={() => setEditing(null)}
          />
        </Modal>
      )}
    </>
  )
}

export default TeamDrills
