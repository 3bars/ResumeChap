import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { api } from '../api'
import VersionEditorModal from '../components/VersionEditorModal.jsx'
import DiffView from '../components/DiffView.jsx'

export default function ResumeDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [resume, setResume] = useState(null)
  const [error, setError] = useState('')
  const [editingMeta, setEditingMeta] = useState(false)
  const [meta, setMeta] = useState({ title: '', target_role: '', description: '', tags: '' })

  const [versionModal, setVersionModal] = useState(null) // {mode:'new'} | {mode:'edit', version}
  const [preview, setPreview] = useState(null) // version being previewed

  // Compare state
  const [compareA, setCompareA] = useState('')
  const [compareB, setCompareB] = useState('')
  const [diff, setDiff] = useState(null)
  const [diffLoading, setDiffLoading] = useState(false)

  async function load() {
    try {
      const r = await api.getResume(id)
      setResume(r)
      setMeta({
        title: r.title,
        target_role: r.target_role || '',
        description: r.description || '',
        tags: r.tags.map((t) => t.name).join(', '),
      })
      setError('')
    } catch (e) {
      setError(e.message)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  async function saveMeta() {
    try {
      await api.updateResume(id, {
        title: meta.title,
        target_role: meta.target_role,
        description: meta.description,
        tags: meta.tags.split(',').map((t) => t.trim()).filter(Boolean),
      })
      setEditingMeta(false)
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  async function deleteVersion(v) {
    if (resume.versions.length <= 1) {
      alert('A resume must keep at least one version. Delete the resume instead.')
      return
    }
    if (!confirm(`Delete v${v.version_number}?`)) return
    await api.deleteVersion(v.id)
    load()
  }

  async function runCompare() {
    if (!compareA || !compareB || compareA === compareB) {
      setError('Pick two different versions to compare.')
      return
    }
    setDiffLoading(true)
    setError('')
    try {
      const res = await api.diff(Number(compareA), Number(compareB))
      setDiff(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setDiffLoading(false)
    }
  }

  if (!resume) {
    return error ? <p className="error">{error}</p> : <p className="muted">Loading…</p>
  }

  return (
    <>
      <p className="small">
        <Link to="/">← Back to catalog</Link>
      </p>

      {/* Resume metadata */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        {editingMeta ? (
          <>
            <div className="field">
              <label>Title</label>
              <input value={meta.title} onChange={(e) => setMeta({ ...meta, title: e.target.value })} />
            </div>
            <div className="field">
              <label>Target role / track</label>
              <input
                value={meta.target_role}
                onChange={(e) => setMeta({ ...meta, target_role: e.target.value })}
              />
            </div>
            <div className="field">
              <label>Description</label>
              <input
                value={meta.description}
                onChange={(e) => setMeta({ ...meta, description: e.target.value })}
              />
            </div>
            <div className="field">
              <label>Tags (comma separated)</label>
              <input value={meta.tags} onChange={(e) => setMeta({ ...meta, tags: e.target.value })} />
            </div>
            <div className="row between">
              <button onClick={() => setEditingMeta(false)}>Cancel</button>
              <button className="primary" onClick={saveMeta}>Save</button>
            </div>
          </>
        ) : (
          <>
            <div className="row between">
              <h1 style={{ margin: 0 }}>{resume.title}</h1>
              <div className="row">
                <button onClick={() => setEditingMeta(true)}>Edit details</button>
                <button
                  className="danger"
                  onClick={async () => {
                    if (confirm('Delete this entire resume?')) {
                      await api.deleteResume(id)
                      navigate('/')
                    }
                  }}
                >
                  Delete resume
                </button>
              </div>
            </div>
            {resume.target_role && <div className="meta">🎯 {resume.target_role}</div>}
            {resume.description && <p className="muted">{resume.description}</p>}
            {resume.tags.length > 0 && (
              <div className="tags">
                {resume.tags.map((t) => (
                  <span className="tag" key={t.id}>{t.name}</span>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {error && <p className="error">{error}</p>}

      {/* Compare */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ marginTop: 0 }}>Compare versions</h2>
        <div className="toolbar">
          <select value={compareA} onChange={(e) => setCompareA(e.target.value)}>
            <option value="">Version A…</option>
            {resume.versions.map((v) => (
              <option key={v.id} value={v.id}>
                v{v.version_number} {v.label ? `· ${v.label}` : ''}
              </option>
            ))}
          </select>
          <select value={compareB} onChange={(e) => setCompareB(e.target.value)}>
            <option value="">Version B…</option>
            {resume.versions.map((v) => (
              <option key={v.id} value={v.id}>
                v{v.version_number} {v.label ? `· ${v.label}` : ''}
              </option>
            ))}
          </select>
          <button className="primary" onClick={runCompare} disabled={diffLoading}>
            {diffLoading ? 'Comparing…' : 'Compare'}
          </button>
        </div>

        {diff && (
          <>
            <div className="row" style={{ marginBottom: '0.5rem' }}>
              <strong>AI Summary</strong>
              <span className={`badge ${diff.ai_enabled ? 'on' : ''}`}>
                {diff.ai_enabled ? 'AI enabled' : 'AI disabled'}
              </span>
            </div>
            <div className="ai-summary">
              <ReactMarkdown>{diff.summary}</ReactMarkdown>
            </div>
            <details>
              <summary className="muted small" style={{ cursor: 'pointer', marginBottom: '0.5rem' }}>
                Show raw text diff
              </summary>
              <DiffView text={diff.text_diff} />
            </details>
          </>
        )}
      </div>

      {/* Versions */}
      <div className="row between" style={{ marginBottom: '0.75rem' }}>
        <h2 style={{ margin: 0 }}>Versions ({resume.versions.length})</h2>
        <button className="primary" onClick={() => setVersionModal({ mode: 'new' })}>
          + New Version
        </button>
      </div>

      {resume.versions
        .slice()
        .sort((a, b) => b.version_number - a.version_number)
        .map((v) => (
          <div className={`version-item ${preview?.id === v.id ? 'selected' : ''}`} key={v.id}>
            <div className="row between">
              <div>
                <strong>v{v.version_number}</strong> {v.label && <span>· {v.label}</span>}
                <div className="meta small">
                  {new Date(v.created_at).toLocaleString()}
                  {v.source_filename ? ` · imported from ${v.source_filename}` : ''}
                </div>
                {v.notes && <div className="small muted">📝 {v.notes}</div>}
              </div>
              <div className="row">
                <button onClick={() => setPreview(preview?.id === v.id ? null : v)}>
                  {preview?.id === v.id ? 'Hide' : 'Preview'}
                </button>
                <button onClick={() => setVersionModal({ mode: 'edit', version: v })}>Edit</button>
                <button className="danger" onClick={() => deleteVersion(v)}>Delete</button>
              </div>
            </div>
            {preview?.id === v.id && (
              <div style={{ marginTop: '0.75rem', borderTop: '1px solid var(--border)', paddingTop: '0.75rem' }}>
                <ReactMarkdown>{v.content || '(empty)'}</ReactMarkdown>
              </div>
            )}
          </div>
        ))}

      {versionModal && (
        <VersionEditorModal
          resumeId={id}
          existing={versionModal.mode === 'edit' ? versionModal.version : null}
          onClose={() => setVersionModal(null)}
          onSaved={() => {
            setVersionModal(null)
            load()
          }}
        />
      )}
    </>
  )
}
