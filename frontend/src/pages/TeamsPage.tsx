import { useState } from 'react'
import { useNavigate } from 'react-router'
import { createTeam, deleteTeam, updateTeam, type Team, type TeamFields } from '../api'
import Modal from '../components/Modal'
import TeamForm from '../components/TeamForm'
import { teamColor } from '../colors'
import { teamInitial } from '../format'
import { useTeams } from '../teamContext'
import { useToast } from '../toast'

// Which pop-up is open, and for which team.
type Dialog =
  | { kind: 'create' }
  | { kind: 'edit'; team: Team }
  | { kind: 'delete'; team: Team }

function TeamsPage() {
  const { teams, reloadTeams, error } = useTeams()
  const [dialog, setDialog] = useState<Dialog | null>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const navigate = useNavigate()
  const showToast = useToast()

  async function handleCreate(fields: TeamFields) {
    const team = await createTeam(fields)
    await reloadTeams()
    setDialog(null)
    showToast({ message: `Created ${team.name}` })
    navigate(`/teams/${team.id}`)
  }

  async function handleEdit(team: Team, fields: TeamFields) {
    await updateTeam(team.id, fields)
    await reloadTeams()
    setDialog(null)
    showToast({ message: 'Team saved' })
  }

  async function handleDelete(team: Team) {
    try {
      await deleteTeam(team.id)
      await reloadTeams()
      setDialog(null)
      showToast({ message: `Deleted ${team.name}` })
    } catch (err) {
      setDeleteError((err as Error).message)
    }
  }

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Teams</h1>
          <p className="muted">Each team has its own sessions. For a new year, just make a new team.</p>
        </div>
        <button onClick={() => setDialog({ kind: 'create' })}>+ New team</button>
      </div>

      {error && <p className="error">{error}</p>}
      {!teams && !error && <div className="loading">Loading teams…</div>}

      {teams?.length === 0 && (
        <div className="empty-page">
          <span className="empty-icon">🛡️</span>
          <h2>Create your first team</h2>
          <p className="muted">Session plans belong to a team, like “U12 Eagles 2027”.</p>
          <button onClick={() => setDialog({ kind: 'create' })}>+ New team</button>
        </div>
      )}

      {teams && teams.length > 0 && (
        <ul className="team-grid">
          {teams.map((team) => (
            <li key={team.id} className="team-card">
              <button className="team-card-main" onClick={() => navigate(`/teams/${team.id}`)}>
                <span className="team-badge" style={{ background: teamColor(team.id) }} aria-hidden="true">
                  {teamInitial(team.name)}
                </span>
                <span className="team-card-text">
                  <strong>{team.name}</strong>
                  <small>
                    {team.plan_count} {team.plan_count === 1 ? 'session' : 'sessions'}
                  </small>
                </span>
              </button>
              <div className="drill-card-actions">
                <button className="ghost small" onClick={() => setDialog({ kind: 'edit', team })}>
                  Edit
                </button>
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
          ))}
        </ul>
      )}

      {dialog?.kind === 'create' && (
        <Modal title="New team" onClose={() => setDialog(null)}>
          <TeamForm submitLabel="Create team" onSubmit={handleCreate} onCancel={() => setDialog(null)} />
        </Modal>
      )}

      {dialog?.kind === 'edit' && (
        <Modal title="Edit team" onClose={() => setDialog(null)}>
          <TeamForm
            initial={{ name: dialog.team.name }}
            submitLabel="Save changes"
            onSubmit={(fields) => handleEdit(dialog.team, fields)}
            onCancel={() => setDialog(null)}
          />
        </Modal>
      )}

      {dialog?.kind === 'delete' && (
        <Modal title="Delete this team?" onClose={() => setDialog(null)}>
          {dialog.team.plan_count > 0 ? (
            <p>
              {dialog.team.name} still has {dialog.team.plan_count} session
              {dialog.team.plan_count === 1 ? '' : 's'}. Delete them or move them to another team first.
            </p>
          ) : (
            <p>
              {dialog.team.name} has no sessions. Its own drills are deleted with it; drill ideas aren't affected.
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
