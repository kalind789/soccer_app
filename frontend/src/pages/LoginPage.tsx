import { useState, type FormEvent } from 'react'
import { supabase } from '../supabase'

type Mode = 'log-in' | 'sign-up'

// Shown instead of the whole app until someone logs in.
function LoginPage() {
  const [mode, setMode] = useState<Mode>('log-in')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    setMessage(null)
    if (mode === 'log-in') {
      // On success, AuthProvider hears about the new login and the app replaces this page.
      const { error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) setError(error.message)
    } else {
      const { data, error } = await supabase.auth.signUp({ email, password })
      if (error) setError(error.message)
      // With email confirmation on (Supabase's default), there's no login until they click the link.
      else if (!data.session) setMessage(`Check ${email} for a link to confirm your account, then log in.`)
    }
    setBusy(false)
  }

  function switchMode() {
    setMode(mode === 'log-in' ? 'sign-up' : 'log-in')
    setError(null)
    setMessage(null)
  }

  return (
    <div className="welcome">
      <span className="empty-icon">⚽</span>
      <h1>{mode === 'log-in' ? 'Welcome back' : 'Create your account'}</h1>
      <p className="muted">Plan practices drill by drill, for every team you coach.</p>
      <div className="panel">
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
              autoComplete={mode === 'log-in' ? 'current-password' : 'new-password'}
              minLength={6}
              required
            />
          </label>
          {error && <p className="error">{error}</p>}
          {message && <p className="notice">{message}</p>}
          <button type="submit" disabled={busy}>
            {busy ? 'One moment…' : mode === 'log-in' ? 'Log in' : 'Sign up'}
          </button>
        </form>
      </div>
      <p className="muted">
        {mode === 'log-in' ? 'New here?' : 'Already have an account?'}{' '}
        <button type="button" className="link-button" onClick={switchMode}>
          {mode === 'log-in' ? 'Create an account' : 'Log in'}
        </button>
      </p>
    </div>
  )
}

export default LoginPage
