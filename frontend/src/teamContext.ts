import { createContext, useContext } from 'react'
import type { Team } from './api'

export type TeamState = {
  teams: Team[] | null // null = still loading.
  reloadTeams: () => Promise<Team[]>
  error: string | null
}

export const TeamContext = createContext<TeamState>({
  teams: null,
  reloadTeams: async () => [],
  error: null,
})

// Any component can call `const { teams } = useTeams()`.
export const useTeams = () => useContext(TeamContext)
