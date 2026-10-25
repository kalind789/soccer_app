import { BrowserRouter, Navigate, NavLink, Route, Routes } from 'react-router'
import { useSession } from './authContext'
import { AuthProvider } from './components/AuthProvider'
import { TeamProvider } from './components/TeamProvider'
import { ToastProvider } from './components/Toast'
import IdeasPage from './pages/IdeasPage'
import JoinPage from './pages/JoinPage'
import LoginPage from './pages/LoginPage'
import PlanPage from './pages/PlanPage'
import TeamPage from './pages/TeamPage'
import TeamsPage from './pages/TeamsPage'
import { supabase } from './supabase'

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <LoggedInOnly />
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  )
}

// The whole app, but only for someone who is logged in. Everyone else gets the login page.
function LoggedInOnly() {
  const session = useSession()

  if (session === undefined) return <div className="loading">Loading…</div>
  if (session === null) {
    return (
      <main>
        <LoginPage />
      </main>
    )
  }

  return (
    // The key gives each user a fresh TeamProvider, so one coach never sees the last one's teams.
    <TeamProvider key={session.user.id}>
      <header className="site-header">
        <div className="site-header-inner">
          <NavLink to="/teams" className="brand">
            <span className="brand-mark">⚽</span>
            <span className="brand-name">Practice Planner</span>
          </NavLink>
          <div className="header-right">
            <nav className="nav">
              {/* NavLink adds class="active" when its page is open, so the CSS can highlight it. */}
              <NavLink to="/teams">Teams</NavLink>
              <NavLink to="/ideas">Drill ideas</NavLink>
            </nav>
            <button className="ghost small" onClick={() => supabase.auth.signOut()} title={session.user.email}>
              Log out
            </button>
          </div>
        </div>
      </header>
      <main>
        {/* Which page to show for which URL. */}
        <Routes>
          <Route path="/" element={<Navigate to="/teams" replace />} />
          <Route path="/teams" element={<TeamsPage />} />
          <Route path="/teams/:teamId" element={<TeamPage tab="sessions" />} />
          <Route path="/teams/:teamId/drills" element={<TeamPage tab="drills" />} />
          <Route path="/teams/:teamId/staff" element={<TeamPage tab="staff" />} />
          <Route path="/teams/:teamId/sessions/:planId" element={<PlanPage />} />
          <Route path="/ideas" element={<IdeasPage />} />
          <Route path="/join/:token" element={<JoinPage />} />
          <Route path="*" element={<div className="empty-page">Page not found.</div>} />
        </Routes>
      </main>
    </TeamProvider>
  )
}

export default App
