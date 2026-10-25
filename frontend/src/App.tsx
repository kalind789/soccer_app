import { BrowserRouter, Navigate, NavLink, Route, Routes } from 'react-router'
import { TeamProvider } from './components/TeamProvider'
import TeamSwitcher from './components/TeamSwitcher'
import { ToastProvider } from './components/Toast'
import DrillsPage from './pages/DrillsPage'
import PlanPage from './pages/PlanPage'
import PlansPage from './pages/PlansPage'
import TeamsPage from './pages/TeamsPage'

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <TeamProvider>
          <header className="site-header">
            <div className="site-header-inner">
              <div className="header-left">
                <NavLink to="/plans" className="brand">
                  <span className="brand-mark">⚽</span>
                  <span className="brand-name">Practice Planner</span>
                </NavLink>
                <TeamSwitcher />
              </div>
              <nav className="nav">
                {/* NavLink adds class="active" when its page is open, so the CSS can highlight it. */}
                <NavLink to="/plans">Sessions</NavLink>
                <NavLink to="/drills">Drills</NavLink>
                <NavLink to="/teams">Teams</NavLink>
              </nav>
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
      </ToastProvider>
    </BrowserRouter>
  )
}

export default App
