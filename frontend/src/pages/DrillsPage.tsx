import { useEffect, useState } from 'react'
import { archiveDrill, createDrill, listDrills, unarchiveDrill, updateDrill, type Drill, type DrillFields } from '../api'
import DrillForm from '../components/DrillForm'

function DrillsPage() {
  const [drills, setDrills] = useState<Drill[]>([])
  const [search, setSearch] = useState('')
  const [includeArchived, setIncludeArchived] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<number | null>(null) // Which drill shows its edit form.
  const [adding, setAdding] = useState(false)
  // Bumping this number makes the effect below run again, which reloads the list.
  const [reloadCount, setReloadCount] = useState(0)

  // Load the drills whenever the search, the checkbox, or reloadCount changes.
  useEffect(() => {
    // If the user types fast, an older request can finish after a newer one.
    // `ignore` makes sure only the latest answer is shown.
    let ignore = false
    listDrills(search, includeArchived)
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
  }, [search, includeArchived, reloadCount])

  function reload() {
    setReloadCount((count) => count + 1)
  }

  async function handleCreate(fields: DrillFields) {
    await createDrill(fields)
    setAdding(false)
    reload()
  }

  async function handleUpdate(id: number, fields: DrillFields) {
    await updateDrill(id, fields)
    setEditingId(null)
    reload()
  }

  async function toggleArchived(drill: Drill) {
    try {
      await (drill.archived ? unarchiveDrill(drill.id) : archiveDrill(drill.id))
      reload()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <section>
      <div className="page-header">
        <div>
          <h1>Drill library</h1>
          <p className="muted">Your reusable drills. Editing one updates it in every session plan that uses it.</p>
        </div>
        {!adding && <button onClick={() => setAdding(true)}>New drill</button>}
      </div>

      {adding && (
        <div className="card">
          <h2>New drill</h2>
          <DrillForm submitLabel="Add drill" onSubmit={handleCreate} onCancel={() => setAdding(false)} />
        </div>
      )}

      <div className="filters">
        <input
          type="search"
          placeholder="Search by name"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <label className="checkbox">
          <input
            type="checkbox"
            checked={includeArchived}
            onChange={(e) => setIncludeArchived(e.target.checked)}
          />
          Show archived
        </label>
      </div>

      {error && <p className="error">{error}</p>}

      {drills.length === 0 ? (
        <p className="empty">{search ? `No drills match "${search}".` : 'No drills yet. Add your first one.'}</p>
      ) : (
        <ul className="list">
          {drills.map((drill) => (
            <li key={drill.id} className={drill.archived ? 'card archived' : 'card'}>
              {editingId === drill.id ? (
                <DrillForm
                  initial={{ name: drill.name, objective: drill.objective, description: drill.description }}
                  submitLabel="Save changes"
                  onSubmit={(fields) => handleUpdate(drill.id, fields)}
                  onCancel={() => setEditingId(null)}
                />
              ) : (
                <div className="card-row">
                  <div>
                    <h3>
                      {drill.name}
                      {drill.archived && <span className="badge">Archived</span>}
                    </h3>
                    {drill.objective && (
                      <p>
                        <span className="label">Goal</span> {drill.objective}
                      </p>
                    )}
                    {drill.description && <p className="muted pre-line">{drill.description}</p>}
                  </div>
                  <div className="row">
                    <button className="secondary" onClick={() => setEditingId(drill.id)}>
                      Edit
                    </button>
                    <button className="secondary" onClick={() => toggleArchived(drill)}>
                      {drill.archived ? 'Unarchive' : 'Archive'}
                    </button>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export default DrillsPage
