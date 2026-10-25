import { useCallback, useEffect, useState, type ReactNode } from 'react'
import { listTeams, type Team } from '../api'
import { TeamContext } from '../teamContext'

// Loads the coach's teams once and shares them with every page.
export function TeamProvider({ children }: { children: ReactNode }) {
  const [teams, setTeams] = useState<Team[] | null>(null)
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

  return <TeamContext.Provider value={{ teams, reloadTeams, error }}>{children}</TeamContext.Provider>
}
