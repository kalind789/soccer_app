import { useNavigate } from 'react-router'
import { teamColor } from '../colors'
import { teamInitial } from '../format'
import { useTeams } from '../teamContext'

const MANAGE = 'manage'

// The "U12 Eagles · 2026 ▾" picker in the header. A plain <select>, so it works with keyboards,
// screen readers, and the native picker on phones.
function TeamSwitcher() {
  const { teams, selectedTeam, selectTeam } = useTeams()
  const navigate = useNavigate()

  if (!teams || teams.length === 0 || !selectedTeam) return null

  return (
    <label className="team-switcher">
      <span className="visually-hidden">Team</span>
      <span className="team-switcher-badge" style={{ background: teamColor(selectedTeam.id) }} aria-hidden="true">
        {teamInitial(selectedTeam.name)}
      </span>
      <select
        value={selectedTeam.id}
        onChange={(e) => {
          if (e.target.value === MANAGE) return navigate('/teams')
          selectTeam(Number(e.target.value))
          navigate('/plans')
        }}
      >
        {teams.map((team) => (
          <option key={team.id} value={team.id}>
            {team.name} · {team.season}
          </option>
        ))}
        <option value={MANAGE}>Manage teams…</option>
      </select>
    </label>
  )
}

export default TeamSwitcher
