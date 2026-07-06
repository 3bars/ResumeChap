import { useEffect, useState } from 'react'
import { api } from '../api'

const PROVIDER_INFO = {
  abacus: { label: 'Abacus.AI', needsKey: false, needsEndpoint: false, hint: 'Uses the built-in Abacus.AI environment — no API key needed.' },
  openai: { label: 'OpenAI', needsKey: true, needsEndpoint: false, hint: 'Requires an OpenAI API key (sk-…).' },
  anthropic: { label: 'Anthropic (Claude)', needsKey: true, needsEndpoint: false, hint: 'Requires an Anthropic API key.' },
  gemini: { label: 'Google Gemini', needsKey: true, needsEndpoint: false, hint: 'Requires a Google AI Studio API key.' },
  copilot: { label: 'Microsoft Copilot / Azure OpenAI', needsKey: true, needsEndpoint: true, hint: 'Requires an Azure OpenAI key + endpoint; model = deployment name.' },
}

export default function Settings() {
  const [settings, setSettings] = useState(null)
  const [enabled, setEnabled] = useState(false)
  const [provider, setProvider] = useState('abacus')
  const [model, setModel] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [endpoint, setEndpoint] = useState('')
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api.getAISettings().then((s) => {
      setSettings(s)
      setEnabled(s.enabled)
      setProvider(s.provider)
      setModel(s.model || '')
      setEndpoint(s.endpoint || '')
    }).catch((e) => setError(e.message))
  }, [])

  async function save() {
    setStatus('')
    setError('')
    try {
      const body = { enabled, provider, model: model || null, endpoint: endpoint || null }
      // Only send api_key if the user typed a new one (avoid wiping existing).
      if (apiKey) body.api_key = apiKey
      const updated = await api.updateAISettings(body)
      setSettings(updated)
      setApiKey('')
      setStatus('Settings saved.')
    } catch (e) {
      setError(e.message)
    }
  }

  if (!settings) return error ? <p className="error">{error}</p> : <p className="muted">Loading…</p>

  const info = PROVIDER_INFO[provider]

  return (
    <>
      <h1>Settings</h1>
      <div className="card" style={{ maxWidth: 640 }}>
        <h2 style={{ marginTop: 0 }}>AI Engine</h2>
        <p className="muted small">
          The AI engine is optional. When enabled, ResumeChap can generate written summaries of the
          differences between two resume versions. When disabled, you still get a plain text diff.
        </p>

        <div className="field">
          <label className="row" style={{ cursor: 'pointer', gap: '0.5rem', alignItems: 'center' }}>
            <input
              type="checkbox"
              checked={enabled}
              onChange={(e) => setEnabled(e.target.checked)}
              style={{ width: 'auto' }}
            />
            Enable AI features
          </label>
        </div>

        <div className="field">
          <label>Provider</label>
          <select value={provider} onChange={(e) => setProvider(e.target.value)} disabled={!enabled}>
            {settings.available_providers.map((p) => (
              <option key={p} value={p}>{PROVIDER_INFO[p]?.label || p}</option>
            ))}
          </select>
          <p className="small muted" style={{ marginTop: '0.35rem' }}>{info.hint}</p>
        </div>

        <div className="field">
          <label>Model {info.label === 'Microsoft Copilot / Azure OpenAI' ? '(deployment name)' : '(optional)'}</label>
          <input
            value={model}
            onChange={(e) => setModel(e.target.value)}
            placeholder="Leave blank for provider default"
            disabled={!enabled}
          />
        </div>

        {info.needsKey && (
          <div className="field">
            <label>API Key {settings.has_api_key ? '(saved — leave blank to keep)' : ''}</label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={settings.has_api_key ? '••••••••' : 'Enter API key'}
              disabled={!enabled}
            />
          </div>
        )}

        {info.needsEndpoint && (
          <div className="field">
            <label>Endpoint</label>
            <input
              value={endpoint}
              onChange={(e) => setEndpoint(e.target.value)}
              placeholder="https://your-resource.openai.azure.com"
              disabled={!enabled}
            />
          </div>
        )}

        {error && <p className="error">{error}</p>}
        {status && <p className="success-text">{status}</p>}

        <button className="primary" onClick={save}>Save Settings</button>
      </div>

      <p className="small muted" style={{ marginTop: '1rem' }}>
        🔒 Your API keys are stored only on your machine (in your local data directory) and are never
        committed to the repository or sent anywhere except your chosen AI provider.
      </p>
    </>
  )
}
