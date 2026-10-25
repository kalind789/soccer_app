import { useState, type FormEvent } from 'react'
import { supabase } from '../supabase'

type Mode = 'log-in' | 'sign-up'

// Shown instead of the whole app until someone logs in.
function LoginPage() {
  const [mode, setMode] = useState<Mode>('log-in')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const signingUp = mode === 'sign-up'

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setMessage(null)
    if (signingUp && password !== confirm) {
      setError("The passwords don't match.")
      return
    }
    setBusy(true)
    if (signingUp) {
      const { data, error } = await supabase.auth.signUp({ email, password })
      if (error) setError(error.message)
      // With email confirmation on (Supabase's default), there's no login until they click the link.
      else if (!data.session) setMessage(`Check ${email} for a link to confirm your account.`)
    } else {
      // On success, AuthProvider hears about the new login and the app replaces this page.
      const { error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) setError(error.message)
    }
    setBusy(false)
  }

  async function handleGoogle() {
    setError(null)
    // Leaves our site for Google's sign-in page. Google sends the coach back here, logged in.
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin },
    })
    if (error) setError(error.message)
  }

  function switchTo(next: Mode) {
    setMode(next)
    setConfirm('')
    setError(null)
    setMessage(null)
  }

  return (
    <div className="welcome">
      <span className="empty-icon">⚽</span>
      <h1>{signingUp ? 'Create your account' : 'Welcome back'}</h1>
      <p className="muted">Plan practices drill by drill, for every team you coach.</p>
      <div className="panel">
        <div className="auth-tabs" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={!signingUp}
            className={signingUp ? '' : 'active'}
            onClick={() => switchTo('log-in')}
          >
            Log in
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={signingUp}
            className={signingUp ? 'active' : ''}
            onClick={() => switchTo('sign-up')}
          >
            Sign up
          </button>
        </div>

        <button type="button" className="secondary google-button" onClick={handleGoogle}>
          <GoogleLogo />
          {signingUp ? 'Sign up with Google' : 'Log in with Google'}
        </button>
        <p className="divider">
          <span>or with email</span>
        </p>

        <form className="stack" onSubmit={handleSubmit}>
          <label>
            Email
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" required />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={signingUp ? 'new-password' : 'current-password'}
              minLength={6}
              required
            />
            {signingUp && <small className="hint">At least 6 characters.</small>}
          </label>
          {signingUp && (
            <label>
              Confirm password
              <input
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                autoComplete="new-password"
                required
              />
              {confirm && confirm !== password && <small className="hint error-text">Doesn't match yet.</small>}
            </label>
          )}
          {error && <p className="error">{error}</p>}
          {message && <p className="notice">{message}</p>}
          <button type="submit" disabled={busy}>
            {busy ? 'One moment…' : signingUp ? 'Create account' : 'Log in'}
          </button>
        </form>
      </div>
    </div>
  )
}

// Google's "G", which their sign-in button guidelines ask for.
function GoogleLogo() {
  return (
    <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.6l6.8-6.8C35.8 2.4 30.3 0 24 0 14.6 0 6.6 5.4 2.7 13.3l7.9 6.1C12.5 13.7 17.8 9.5 24 9.5z" />
      <path fill="#4285F4" d="M46.1 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.4c-.5 2.9-2.2 5.3-4.6 6.9l7.4 5.8c4.3-4 6.9-9.9 6.9-17.2z" />
      <path fill="#FBBC05" d="M10.6 28.6c-.5-1.4-.8-3-.8-4.6s.3-3.2.8-4.6l-7.9-6.1C1 16.6 0 20.2 0 24s1 7.4 2.7 10.7l7.9-6.1z" />
      <path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.4-5.8c-2.1 1.4-4.8 2.3-8.5 2.3-6.2 0-11.5-4.2-13.4-9.9l-7.9 6.1C6.6 42.6 14.6 48 24 48z" />
    </svg>
  )
}

export default LoginPage
