import { useCallback, useEffect, useState, type ReactNode } from 'react'
import { listTeams, type Team } from '../api'
import { TeamContext } from '../teamContext'

const STORAGE_KEY = 'selectedTeamId'

// Remembering the selected team is a convenience, so if the browser blocks storage, just carry on.
function readSavedTeamId(): number | null {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved ? Number(saved) : null
  } catch {
    return null
  }
}

function saveTeamId(teamId: number) {
  try {
    localStorage.setItem(STORAGE_KEY, String(teamId))
  } catch {
    // Not saved; it still works for this visit.
  }
}

// Loads the coach's teams once and shares them, with the selected team, with every page.
export function TeamProvider({ children }: { children: ReactNode }) {
  const [teams, setTeams] = useState<Team[] | null>(null)
  const [selectedId, setSelectedId] = useState<number | null>(readSavedTeamId)
  const [error, setError] = useState<string | null>(null)

  const reloadTeams = useCallback(async () => {
    try {
      const result = await listTeams()
      setTeams(result)
      setError(null)
      return result
    } catch (err) {
      setError((err as Error).message)
      return []
    }
  }, [])

  useEffect(() => {
    listTeams()
      .then(setTeams)
      .catch((err: Error) => setError(err.message))
  }, [])

  const selectTeam = useCallback((teamId: number) => {
    setSelectedId(teamId)
    saveTeamId(teamId)
  }, [])

  // If the saved team is gone (deleted, or another coach's browser), fall back to the newest team.
  const selectedTeam = teams?.find((team) => team.id === selectedId) ?? teams?.[0] ?? null

  return (
    <TeamContext.Provider value={{ teams, selectedTeam, selectTeam, reloadTeams, error }}>
      {children}
    </TeamContext.Provider>
  )
}
