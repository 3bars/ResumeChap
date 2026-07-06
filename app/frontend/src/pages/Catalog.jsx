import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import ResumeFormModal from '../components/ResumeFormModal.jsx'

export default function Catalog() {
  const [resumes, setResumes] = useState([])
  const [tags, setTags] = useState([])
  const [search, setSearch] = useState('')
  const [tagFilter, setTagFilter] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    try {
      const [rs, ts] = await Promise.all([
        api.listResumes({ search, tag: tagFilter }),
        api.listTags(),
      ])
      setResumes(rs)
      setTags(ts)
      setError('')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, tagFilter])

  async function handleDelete(id, title) {
    if (!confirm(`Delete resume "${title}" and all its versions? This cannot be undone.`)) return
    try {
      await api.deleteResume(id)
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <>
      <div className="row between" style={{ marginBottom: '1.25rem' }}>
        <h1 style={{ margin: 0 }}>Your Resumes</h1>
        <button className="primary" onClick={() => setShowCreate(true)}>
          + New Resume
        </button>
      </div>

      <div className="toolbar">
        <input
          placeholder="Search title, role, description…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select value={tagFilter} onChange={(e) => setTagFilter(e.target.value)}>
          <option value="">All tags</option>
          {tags.map((t) => (
            <option key={t.id} value={t.name}>
              {t.name}
            </option>
          ))}
        </select>
        {(search || tagFilter) && (
          <button onClick={() => { setSearch(''); setTagFilter('') }}>Clear</button>
        )}
      </div>

      {error && <p className="error">{error}</p>}

      {loading ? (
        <p className="muted">Loading…</p>
      ) : resumes.length === 0 ? (
        <div className="empty">
          <p>No resumes yet.</p>
          <button className="primary" onClick={() => setShowCreate(true)}>
            Create your first resume
          </button>
        </div>
      ) : (
        <div className="grid">
          {resumes.map((r) => (
            <div className="card" key={r.id}>
              <div className="row between">
                <h3>
                  <Link to={`/resumes/${r.id}`}>{r.title}</Link>
                </h3>
                <button className="danger small" onClick={() => handleDelete(r.id, r.title)}>
                  Delete
                </button>
              </div>
              {r.target_role && <div className="meta">🎯 {r.target_role}</div>}
              {r.description && <p className="small muted">{r.description}</p>}
              <div className="meta small">
                {r.version_count} version{r.version_count !== 1 ? 's' : ''} · updated{' '}
                {new Date(r.updated_at).toLocaleDateString()}
              </div>
              {r.tags.length > 0 && (
                <div className="tags">
                  {r.tags.map((t) => (
                    <span className="tag" key={t.id}>
                      {t.name}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <ResumeFormModal
          onClose={() => setShowCreate(false)}
          onSaved={() => {
            setShowCreate(false)
            load()
          }}
        />
      )}
    </>
  )
}
