import { BrowserRouter, Navigate, NavLink, Route, Routes } from 'react-router'
import { ToastProvider } from './components/Toast'
import DrillsPage from './pages/DrillsPage'
import PlanPage from './pages/PlanPage'
import PlansPage from './pages/PlansPage'

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <header className="site-header">
          <div className="site-header-inner">
            <NavLink to="/plans" className="brand">
              <span className="brand-mark">⚽</span> Practice Planner
            </NavLink>
            <nav className="nav">
              {/* NavLink adds class="active" when its page is open, so the CSS can highlight it. */}
              <NavLink to="/plans">Sessions</NavLink>
              <NavLink to="/drills">Drill library</NavLink>
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
            <Route path="*" element={<div className="empty-page">Page not found.</div>} />
          </Routes>
        </main>
      </ToastProvider>
    </BrowserRouter>
  )
}

export default App
