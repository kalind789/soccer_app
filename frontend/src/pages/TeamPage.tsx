import { Link, NavLink, useParams } from 'react-router'
import { teamColor } from '../colors'
import { teamInitial } from '../format'
import { ageWithFormat } from '../tags'
import { useTeams } from '../teamContext'
import TeamDrills from './TeamDrills'
import TeamSessions from './TeamSessions'
import TeamStaff from './TeamStaff'

// One team: its sessions, its own drills and its staff, as tabs. The tab comes from the URL:
// /teams/3 shows sessions, /teams/3/drills drills, /teams/3/staff the staff.
function TeamPage({ tab }: { tab: 'sessions' | 'drills' | 'staff' }) {
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
        <div>
          <h1>{team.name}</h1>
          <p className="muted">
            {team.age_group ? ageWithFormat(team.age_group) : 'No age group yet'} ·{' '}
            {team.members.map((m) => m.name || m.email).join(', ')}
          </p>
        </div>
      </div>
      <nav className="tabs" aria-label={`${team.name} sections`}>
        {/* `end`: only "active" on exactly /teams/3, not on /teams/3/drills. */}
        <NavLink to={`/teams/${team.id}`} end>
          Sessions
        </NavLink>
        <NavLink to={`/teams/${team.id}/drills`}>Drills</NavLink>
        <NavLink to={`/teams/${team.id}/staff`}>Staff ({team.members.length})</NavLink>
      </nav>
      {/* key: a different team gets a fresh tab, with nothing left over from the last one. */}
      {tab === 'sessions' && <TeamSessions key={team.id} team={team} />}
      {tab === 'drills' && <TeamDrills key={team.id} team={team} />}
      {tab === 'staff' && <TeamStaff key={team.id} team={team} />}
    </>
  )
}

export default TeamPage
