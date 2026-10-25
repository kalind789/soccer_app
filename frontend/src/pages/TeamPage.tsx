import { Link, NavLink, useParams } from 'react-router'
import { teamColor } from '../colors'
import { teamInitial } from '../format'
import { useTeams } from '../teamContext'
import TeamDrills from './TeamDrills'
import TeamSessions from './TeamSessions'

// One team: its sessions and its own drills, as two tabs. The tab comes from the URL:
// /teams/3 shows sessions, /teams/3/drills shows drills.
function TeamPage({ tab }: { tab: 'sessions' | 'drills' }) {
  const { teamId } = useParams()
  const { teams, error } = useTeams()
  const team = teams?.find((t) => t.id === Number(teamId))

  if (error) return <p className="error">{error}</p>
  if (!teams) return <div className="loading">Loading team…</div>
  if (!team) {
    return (
      <div className="empty-page">
        <span className="empty-icon">🔍</span>
        <h2>We couldn't find that team</h2>
        <Link to="/teams" className="button">
          Back to teams
        </Link>
      </div>
    )
  }

  return (
    <>
      <Link to="/teams" className="back">
        ← All teams
      </Link>
      <div className="team-header">
        <span className="team-badge" style={{ background: teamColor(team.id) }} aria-hidden="true">
          {teamInitial(team.name)}
        </span>
        <h1>{team.name}</h1>
      </div>
      <nav className="tabs" aria-label={`${team.name} sections`}>
        {/* `end`: only "active" on exactly /teams/3, not on /teams/3/drills. */}
        <NavLink to={`/teams/${team.id}`} end>
          Sessions
        </NavLink>
        <NavLink to={`/teams/${team.id}/drills`}>Drills</NavLink>
      </nav>
      {/* key: a different team gets a fresh tab, with nothing left over from the last one. */}
      {tab === 'sessions' ? <TeamSessions key={team.id} team={team} /> : <TeamDrills key={team.id} team={team} />}
    </>
  )
}

export default TeamPage
