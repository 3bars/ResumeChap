import { useState } from 'react'
import { api } from '../api'

// Modal for adding a new version (revision) or editing an existing one.
// `existing` (optional) is a version object -> edit mode; otherwise create mode.
export default function VersionEditorModal({ resumeId, existing, onClose, onSaved }) {
  const isEdit = Boolean(existing)
  const [label, setLabel] = useState(existing?.label || '')
  const [notes, setNotes] = useState(existing?.notes || '')
  const [content, setContent] = useState(existing?.content || '')
  const [importing, setImporting] = useState(false)
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
    } catch (err) {
      setError(err.message)
    } finally {
      setImporting(false)
    }
  }

  async function handleSave() {
    setSaving(true)
    setError('')
    try {
      if (isEdit) {
        await api.updateVersion(existing.id, { label, notes, content })
      } else {
        await api.addVersion(resumeId, { label, notes, content, content_format: 'markdown' })
      }
      onSaved()
    } catch (err) {
      setError(err.message)
      setSaving(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>{isEdit ? `Edit v${existing.version_number}` : 'New Version (revision)'}</h2>
        {error && <p className="error">{error}</p>}

        <div className="field">
          <label>Label</label>
          <input
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            placeholder="e.g. Tightened summary for senior roles"
          />
        </div>
        <div className="field">
          <label>Notes</label>
          <input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Optional notes" />
        </div>
        <div className="field">
          <label>
            Content (markdown){' '}
            <input
              type="file"
              accept=".pdf,.docx,.txt,.md,.markdown"
              onChange={handleImport}
              style={{ display: 'inline-block', width: 'auto', marginLeft: '0.5rem' }}
            />
          </label>
          {importing && <p className="small muted">Parsing file…</p>}
          <textarea value={content} onChange={(e) => setContent(e.target.value)} style={{ minHeight: 240 }} />
        </div>

        <div className="row between">
          <button onClick={onClose}>Cancel</button>
          <button className="primary" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : isEdit ? 'Save Changes' : 'Add Version'}
          </button>
        </div>
      </div>
    </div>
  )
}
