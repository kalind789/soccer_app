import { useState } from 'react'
import { useNavigate } from 'react-router'
import { createTeam, deleteTeam, updateTeam, type Team, type TeamFields } from '../api'
import Modal from '../components/Modal'
import TeamForm from '../components/TeamForm'
import { teamColor } from '../colors'
import { nextSeason, teamInitial } from '../format'
import { useTeams } from '../teamContext'
import { useToast } from '../toast'

// Which pop-up is open, and for which team.
type Dialog =
  | { kind: 'create' }
  | { kind: 'edit'; team: Team }
  | { kind: 'next-season'; team: Team }
  | { kind: 'delete'; team: Team }

function TeamsPage() {
  const { teams, selectedTeam, selectTeam, reloadTeams, error } = useTeams()
  const [dialog, setDialog] = useState<Dialog | null>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const navigate = useNavigate()
  const showToast = useToast()

  async function handleCreate(fields: TeamFields) {
    const team = await createTeam(fields)
    await reloadTeams()
    selectTeam(team.id)
    setDialog(null)
    showToast({ message: `Created ${team.name} (${team.season})` })
  }

  async function handleEdit(team: Team, fields: TeamFields) {
    await updateTeam(team.id, fields)
    await reloadTeams()
    setDialog(null)
    showToast({ message: 'Team saved' })
  }

  async function handleNextSeason(previous: Team, fields: TeamFields) {
    const team = await createTeam({ ...fields, previous_team_id: previous.id })
    await reloadTeams()
    selectTeam(team.id)
    setDialog(null)
    showToast({ message: `Started ${team.name} ${team.season}. Last season's plans stay with ${previous.season}.` })
  }

  async function handleDelete(team: Team) {
    try {
      await deleteTeam(team.id)
      await reloadTeams()
      setDialog(null)
      showToast({ message: `Deleted ${team.name} (${team.season})` })
    } catch (err) {
      setDeleteError((err as Error).message)
    }
  }

  function openSessions(team: Team) {
    selectTeam(team.id)
    navigate('/plans')
  }

  // Group by season, newest first (the API already sorts them that way).
  const seasons: [string, Team[]][] = []
  for (const team of teams ?? []) {
    const group = seasons.find(([season]) => season === team.season)
    if (group) group[1].push(team)
    else seasons.push([team.season, [team]])
  }
  const byId = new Map((teams ?? []).map((team) => [team.id, team]))
  // A team that already has a next season doesn't need the "Start next season" button.
  const continued = new Set((teams ?? []).map((team) => team.previous_team_id))

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Teams</h1>
          <p className="muted">One team per season. Start next season to get a fresh team that keeps its history.</p>
        </div>
        <button onClick={() => setDialog({ kind: 'create' })}>+ New team</button>
      </div>

      {error && <p className="error">{error}</p>}
      {!teams && !error && <div className="loading">Loading teams…</div>}

      {teams?.length === 0 && (
        <div className="empty-page">
          <span className="empty-icon">🛡️</span>
          <h2>Create your first team</h2>
          <p className="muted">Session plans belong to a team, like “U12 Eagles” in the 2026 season.</p>
          <button onClick={() => setDialog({ kind: 'create' })}>+ New team</button>
        </div>
      )}

      {seasons.map(([season, seasonTeams]) => (
        <section className="group" key={season}>
          <h2 className="group-title">
            {season} <span className="count">{seasonTeams.length}</span>
          </h2>
          <ul className="team-grid">
            {seasonTeams.map((team) => {
              const previous = team.previous_team_id ? byId.get(team.previous_team_id) : undefined
              return (
                <li key={team.id} className={team.id === selectedTeam?.id ? 'team-card selected' : 'team-card'}>
                  <button className="team-card-main" onClick={() => openSessions(team)}>
                    <span className="team-badge" style={{ background: teamColor(team.id) }} aria-hidden="true">
                      {teamInitial(team.name)}
                    </span>
                    <span className="team-card-text">
                      <strong>{team.name}</strong>
                      <small>
                        {team.plan_count} {team.plan_count === 1 ? 'session' : 'sessions'}
                        {previous && ` · continues ${previous.season}`}
                      </small>
                    </span>
                  </button>
                  <div className="drill-card-actions">
                    <button className="ghost small" onClick={() => setDialog({ kind: 'edit', team })}>
                      Edit
                    </button>
                    {!continued.has(team.id) && (
                      <button className="ghost small" onClick={() => setDialog({ kind: 'next-season', team })}>
                        Start next season
                      </button>
                    )}
                    <button
                      className="ghost small danger-text"
                      onClick={() => {
                        setDeleteError(null)
                        setDialog({ kind: 'delete', team })
                      }}
                    >
                      Delete
                    </button>
                  </div>
                </li>
              )
            })}
          </ul>
        </section>
      ))}

      {dialog?.kind === 'create' && (
        <Modal title="New team" onClose={() => setDialog(null)}>
          <TeamForm submitLabel="Create team" onSubmit={handleCreate} onCancel={() => setDialog(null)} />
        </Modal>
      )}

      {dialog?.kind === 'edit' && (
        <Modal title="Edit team" onClose={() => setDialog(null)}>
          <TeamForm
            initial={{ name: dialog.team.name, season: dialog.team.season }}
            submitLabel="Save changes"
            onSubmit={(fields) => handleEdit(dialog.team, fields)}
            onCancel={() => setDialog(null)}
          />
        </Modal>
      )}

      {dialog?.kind === 'next-season' && (
        <Modal title={`Next season for ${dialog.team.name}`} onClose={() => setDialog(null)}>
          <p className="muted">
            A new, empty team for the new season. {dialog.team.season}'s sessions stay where they are, and the two
            seasons stay linked.
          </p>
          <TeamForm
            initial={{ name: dialog.team.name, season: nextSeason(dialog.team.season) }}
            submitLabel="Start season"
            onSubmit={(fields) => handleNextSeason(dialog.team, fields)}
            onCancel={() => setDialog(null)}
          />
        </Modal>
      )}

      {dialog?.kind === 'delete' && (
        <Modal title="Delete this team?" onClose={() => setDialog(null)}>
          {dialog.team.plan_count > 0 ? (
            <p>
              {dialog.team.name} ({dialog.team.season}) still has {dialog.team.plan_count} session
              {dialog.team.plan_count === 1 ? '' : 's'}. Delete them or move them to another team first.
            </p>
          ) : (
            <p>
              {dialog.team.name} ({dialog.team.season}) has no sessions, so nothing else is lost.
            </p>
          )}
          {deleteError && <p className="error">{deleteError}</p>}
          <div className="row end">
            <button className="secondary" onClick={() => setDialog(null)}>
              Keep it
            </button>
            <button className="danger" onClick={() => handleDelete(dialog.team)} disabled={dialog.team.plan_count > 0}>
              Delete team
            </button>
          </div>
        </Modal>
      )}
    </>
  )
}

export default TeamsPage
