import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { acceptInvite, previewInvite, type InvitePreview } from '../api'
import { ageWithFormat } from '../tags'
import { useTeams } from '../teamContext'

// Where an invite link (/join/<token>) lands, after logging in.
function JoinPage() {
  const { token = '' } = useParams()
  const [invite, setInvite] = useState<InvitePreview | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [joining, setJoining] = useState(false)
  const { reloadTeams } = useTeams()
  const navigate = useNavigate()

  useEffect(() => {
    previewInvite(token)
      .then(setInvite)
      .catch((err: Error) => setError(err.message))
  }, [token])

  async function handleJoin() {
    setJoining(true)
    try {
      const team = await acceptInvite(token)
      await reloadTeams()
      navigate(`/teams/${team.id}`)
    } catch (err) {
      setError((err as Error).message)
      setJoining(false)
    }
  }

  if (error && !invite) {
    return (
      <div className="empty-page">
        <span className="empty-icon">🔗</span>
        <h2>This invite doesn't work</h2>
        <p className="muted">{error}</p>
        <Link to="/teams" className="button">
          Go to your teams
        </Link>
      </div>
    )
  }
  if (!invite) return <div className="loading">Checking your invite…</div>

  return (
    <div className="welcome">
      <span className="empty-icon">🤝</span>
      <h1>Join {invite.team_name}</h1>
      <p className="muted">
        {invite.head_coach || 'The head coach'} invited you to coach
        {invite.age_group ? ` this ${ageWithFormat(invite.age_group)} team` : ' this team'}. You'll share its sessions
        and drills.
      </p>
      {invite.already_member ? (
        <Link to={`/teams/${invite.team_id}`} className="button">
          You're already on staff. Open the team
        </Link>
      ) : (
        <button onClick={handleJoin} disabled={joining}>
          {joining ? 'Joining…' : `Join as a coach`}
        </button>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  )
}

export default JoinPage
