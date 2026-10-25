import { createContext, useContext } from 'react'
import type { Team } from './api'

export type TeamState = {
  teams: Team[] | null // null = still loading.
  selectedTeam: Team | null // The team whose sessions the Sessions page shows.
  selectTeam: (teamId: number) => void
  reloadTeams: () => Promise<Team[]>
  error: string | null
}

export const TeamContext = createContext<TeamState>({
  teams: null,
  selectedTeam: null,
  selectTeam: () => {},
  reloadTeams: async () => [],
  error: null,
})

// Any component can call `const { teams, selectedTeam } = useTeams()`.
export const useTeams = () => useContext(TeamContext)
