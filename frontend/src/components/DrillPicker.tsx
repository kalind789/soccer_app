import { useState } from 'react'
import type { Drill } from '../api'
import { drillColor } from '../colors'

type Props = {
  library: Drill[]
  usedCounts: Map<number, number> // drill id → how many times it's already in this plan.
  onAdd: (drill: Drill) => void
  onCreate: () => void
}

// The "Add drills" panel next to a session plan: search the library and click to add.
function DrillPicker({ library, usedCounts, onAdd, onCreate }: Props) {
  const [search, setSearch] = useState('')
  // The library is small, so filtering here is instant, with no request per key press.
  const matches = library.filter((drill) => drill.name.toLowerCase().includes(search.trim().toLowerCase()))

  return (
    <aside className="panel picker">
      <div className="panel-header">
        <h2>Add drills</h2>
        <button className="soft small" onClick={onCreate}>
          + New drill
        </button>
      </div>
      <input
        type="search"
        className="search"
        placeholder="Search your library"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <ul className="picker-list">
        {matches.map((drill) => {
          const used = usedCounts.get(drill.id) ?? 0
          return (
            <li key={drill.id}>
              <button className="picker-item" onClick={() => onAdd(drill)} title={`Add ${drill.name}`}>
                <span className="dot" style={{ background: drillColor(drill.id) }} />
                <span className="picker-text">
                  <strong>{drill.name}</strong>
                  {drill.objective && <small>{drill.objective}</small>}
                </span>
                {used > 0 && <span className="pill">{used === 1 ? 'In plan' : `${used}× in plan`}</span>}
                <span className="picker-plus" aria-hidden="true">
                  +
                </span>
              </button>
            </li>
          )
        })}
      </ul>
      {library.length === 0 ? (
        <p className="hint">Your library is empty. Create your first drill and it'll be saved for every session.</p>
      ) : (
        matches.length === 0 && (
          <p className="hint">
            No drill called “{search}”.{' '}
            <button className="link" onClick={onCreate}>
              Create it
            </button>
          </p>
        )
      )}
    </aside>
  )
}

export default DrillPicker
