import { BrowserRouter, Navigate, NavLink, Route, Routes } from 'react-router'
import DrillsPage from './pages/DrillsPage'
import PlanPage from './pages/PlanPage'
import PlansPage from './pages/PlansPage'

function App() {
  return (
    <BrowserRouter>
      <header className="site-header">
        <div className="site-header-inner">
          <span className="brand">⚽ Practice Planner</span>
          <nav>
            {/* NavLink adds class="active" when its page is open, so the CSS can highlight it. */}
            <NavLink to="/plans">Session plans</NavLink>
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
          <Route path="*" element={<p className="empty">Page not found.</p>} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}

export default App
