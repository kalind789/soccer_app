import { useEffect, useState } from 'react'
import { archiveDrill, listDrills, unarchiveDrill, type Drill } from './api'
import NewDrillForm from './NewDrillForm'

function DrillLibrary() {
  const [drills, setDrills] = useState<Drill[]>([])
  const [search, setSearch] = useState('')
  const [includeArchived, setIncludeArchived] = useState(false)
  const [error, setError] = useState<string | null>(null)
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
      <h2>Drill library</h2>

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
        <p className="muted">{search ? `No drills match "${search}".` : 'No drills yet. Add one below.'}</p>
      ) : (
        <ul className="drill-list">
          {drills.map((drill) => (
            <li key={drill.id} className={drill.archived ? 'card archived' : 'card'}>
              <div>
                <h3>
                  {drill.name}
                  {drill.archived && <span className="badge">Archived</span>}
                </h3>
                {drill.objective && <p className="muted">{drill.objective}</p>}
                {drill.description && <p>{drill.description}</p>}
              </div>
              <button className="secondary" onClick={() => toggleArchived(drill)}>
                {drill.archived ? 'Unarchive' : 'Archive'}
              </button>
            </li>
          ))}
        </ul>
      )}

      <NewDrillForm onCreated={reload} />
    </section>
  )
}

export default DrillLibrary
