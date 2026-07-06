import { Link, Outlet, useLocation } from 'react-router-dom'

export default function App() {
  const { pathname } = useLocation()
  return (
    <>
      <header className="app-header">
        <Link to="/" className="brand">
          <span>📄</span> ResumeChap
        </Link>
        <nav>
          <Link to="/" style={{ color: pathname === '/' ? 'var(--accent)' : 'var(--muted)' }}>
            Catalog
          </Link>
          <Link
            to="/settings"
            style={{ color: pathname === '/settings' ? 'var(--accent)' : 'var(--muted)' }}
          >
            Settings
          </Link>
        </nav>
      </header>
      <main className="container">
        <Outlet />
      </main>
    </>
  )
}
