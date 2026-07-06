import { useState } from 'react'
import { api } from '../api'

// Modal for creating a new resume. Supports free-form/markdown content and
// importing content from an uploaded PDF/DOCX/TXT file (resume-engine).
export default function ResumeFormModal({ onClose, onSaved }) {
  const [title, setTitle] = useState('')
  const [targetRole, setTargetRole] = useState('')
  const [description, setDescription] = useState('')
  const [tags, setTags] = useState('')
  const [content, setContent] = useState('')
  const [importing, setImporting] = useState(false)
  const [importedName, setImportedName] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  async function handleImport(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setImporting(true)
    setError('')
    try {
      const res = await api.importFile(file)
      setContent(res.content)
      setImportedName(res.filename)
      if (!title) setTitle(file.name.replace(/\.[^.]+$/, ''))
    } catch (err) {
      setError(err.message)
    } finally {
      setImporting(false)
    }
  }

  async function handleSave() {
    if (!title.trim()) {
      setError('Title is required.')
      return
    }
    setSaving(true)
    setError('')
    try {
      await api.createResume({
        title: title.trim(),
        target_role: targetRole.trim() || null,
        description: description.trim() || null,
        tags: tags.split(',').map((t) => t.trim()).filter(Boolean),
        content,
        content_format: 'markdown',
      })
      onSaved()
    } catch (err) {
      setError(err.message)
      setSaving(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>New Resume</h2>
        {error && <p className="error">{error}</p>}

        <div className="field">
          <label>Title *</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Cloud Engineer" />
        </div>
        <div className="field">
          <label>Target role / track</label>
          <input
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g. AWS / DevOps / Linux Admin"
          />
        </div>
        <div className="field">
          <label>Description</label>
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Short note about this resume"
          />
        </div>
        <div className="field">
          <label>Tags (comma separated)</label>
          <input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="cloud, aws, senior" />
        </div>

        <div className="field">
          <label>
            Resume content (markdown) — or import from a file
            <input
              type="file"
              accept=".pdf,.docx,.txt,.md,.markdown"
              onChange={handleImport}
              style={{ marginTop: '0.4rem' }}
            />
          </label>
          {importing && <p className="small muted">Parsing file…</p>}
          {importedName && <p className="small success-text">Imported from {importedName}</p>}
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="# Your Name&#10;Summary, experience, skills…"
            style={{ minHeight: 180 }}
          />
        </div>

        <div className="row between">
          <button onClick={onClose}>Cancel</button>
          <button className="primary" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Create Resume'}
          </button>
        </div>
      </div>
    </div>
  )
}
