import { BrowserRouter, Navigate, NavLink, Route, Routes } from 'react-router'
import { useSession } from './authContext'
import { AuthProvider } from './components/AuthProvider'
import { TeamProvider } from './components/TeamProvider'
import TeamSwitcher from './components/TeamSwitcher'
import { ToastProvider } from './components/Toast'
import DrillsPage from './pages/DrillsPage'
import LoginPage from './pages/LoginPage'
import PlanPage from './pages/PlanPage'
import PlansPage from './pages/PlansPage'
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
          <div className="header-left">
            <NavLink to="/plans" className="brand">
              <span className="brand-mark">⚽</span>
              <span className="brand-name">Practice Planner</span>
            </NavLink>
            <TeamSwitcher />
          </div>
          <div className="header-right">
            <nav className="nav">
              {/* NavLink adds class="active" when its page is open, so the CSS can highlight it. */}
              <NavLink to="/plans">Sessions</NavLink>
              <NavLink to="/drills">Drills</NavLink>
              <NavLink to="/teams">Teams</NavLink>
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
          <Route path="/" element={<Navigate to="/plans" replace />} />
          <Route path="/plans" element={<PlansPage />} />
          <Route path="/plans/:planId" element={<PlanPage />} />
          <Route path="/drills" element={<DrillsPage />} />
          <Route path="/teams" element={<TeamsPage />} />
          <Route path="*" element={<div className="empty-page">Page not found.</div>} />
        </Routes>
      </main>
    </TeamProvider>
  )
}

export default App
