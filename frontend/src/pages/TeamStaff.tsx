import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import {
  createInviteLink,
  getInviteLink,
  removeMember,
  turnOffInviteLink,
  type InviteLink,
  type Member,
  type Team,
} from '../api'
import Modal from '../components/Modal'
import { formatDate } from '../format'
import { useSession } from '../authContext'
import { roleLabel } from '../tags'
import { useTeams } from '../teamContext'
import { useToast } from '../toast'

// The Staff tab of a team's page: who coaches the team, and (for the head coach) the invite link.
function TeamStaff({ team }: { team: Team }) {
  const session = useSession()
  const { reloadTeams } = useTeams()
  const navigate = useNavigate()
  const showToast = useToast()
  const [removing, setRemoving] = useState<Member | null>(null) // The coach in the "are you sure?" window.
  const [error, setError] = useState<string | null>(null)
  const myId = session?.user.id
  const isHeadCoach = team.my_role === 'head_coach'

  async function handleRemove(member: Member) {
    try {
      await removeMember(team.id, member.user_id)
      setRemoving(null)
      if (member.user_id === myId) {
        showToast({ message: `You left ${team.name}` })
        navigate('/teams')
      } else {
        showToast({ message: `Removed ${member.name} from ${team.name}` })
      }
      await reloadTeams()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <>
      <ul className="staff-list">
        {team.members.map((member) => (
          <li key={member.user_id} className="staff-row">
            <span className="avatar" aria-hidden="true">
              {(member.name || member.email || '?').charAt(0).toUpperCase()}
            </span>
            <span className="staff-text">
              <strong>
                {member.name || member.email}
                {member.user_id === myId && <span className="pill">You</span>}
              </strong>
              <small className="muted">
                {roleLabel(member.role)}
                {member.email && ` · ${member.email}`}
              </small>
            </span>
            {/* The head coach can remove coaches; a coach can only remove themselves (leave). */}
            {member.role === 'coach' && (isHeadCoach || member.user_id === myId) && (
              <button className="ghost small danger-text" onClick={() => setRemoving(member)}>
                {member.user_id === myId ? 'Leave team' : 'Remove'}
              </button>
            )}
          </li>
        ))}
      </ul>
      {error && <p className="error">{error}</p>}

      {isHeadCoach ? (
        <InvitePanel team={team} />
      ) : (
        <p className="hint">Only the head coach can invite coaches. Ask them for an invite link.</p>
      )}

      {removing && (
        <Modal
          title={removing.user_id === myId ? `Leave ${team.name}?` : `Remove ${removing.name}?`}
          onClose={() => setRemoving(null)}
        >
          <p>
            {removing.user_id === myId
              ? "You won't see this team's sessions or drills anymore, unless you're invited again."
              : `${removing.name} won't see this team's sessions or drills anymore. Everything they made stays with the team.`}
          </p>
          <div className="row end">
            <button className="secondary" onClick={() => setRemoving(null)}>
              Cancel
            </button>
            <button className="danger" onClick={() => handleRemove(removing)}>
              {removing.user_id === myId ? 'Leave team' : 'Remove'}
            </button>
          </div>
        </Modal>
      )}
    </>
  )
}

// The head coach's invite link: make one, copy it, replace it, or turn it off.
function InvitePanel({ team }: { team: Team }) {
  const [link, setLink] = useState<InviteLink | null | undefined>(undefined) // undefined = loading.
  const [error, setError] = useState<string | null>(null)
  const showToast = useToast()

  useEffect(() => {
    getInviteLink(team.id)
      .then(setLink)
      .catch((err: Error) => setError(err.message))
  }, [team.id])

  const url = link ? `${window.location.origin}/join/${link.token}` : ''

  async function run(action: () => Promise<void>) {
    try {
      await action()
      setError(null)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  const makeLink = () =>
    run(async () => {
      setLink(await createInviteLink(team.id))
      showToast({ message: link ? 'New link made. The old one no longer works.' : 'Invite link ready to share' })
    })

  const turnOff = () =>
    run(async () => {
      await turnOffInviteLink(team.id)
      setLink(null)
      showToast({ message: 'Invite link turned off' })
    })

  const copy = () =>
    run(async () => {
      await navigator.clipboard.writeText(url)
      showToast({ message: 'Link copied. Paste it in a text or email to your coaches.' })
    })

  return (
    <section className="panel invite-panel">
      <h2>Invite coaches</h2>
      <p className="muted">
        Anyone who opens the link and logs in joins {team.name} as a coach. They can plan sessions and edit drills.
      </p>
      {link === undefined && !error && <p className="muted">Loading…</p>}
      {link === null && <button onClick={makeLink}>Create invite link</button>}
      {link && (
        <>
          <div className="invite-link">
            <input value={url} readOnly aria-label="Invite link" onFocus={(e) => e.target.select()} />
            <button onClick={copy}>Copy</button>
          </div>
          <p className="small-text muted">Works until {formatDate(link.expires_at.slice(0, 10))}.</p>
          <div className="row">
            <button className="secondary small" onClick={makeLink}>
              New link
            </button>
            <button className="ghost small danger-text" onClick={turnOff}>
              Turn off
            </button>
          </div>
        </>
      )}
      {error && <p className="error">{error}</p>}
    </section>
  )
}

export default TeamStaff
