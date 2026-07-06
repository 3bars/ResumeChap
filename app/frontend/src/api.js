// Thin API client for the ResumeChap backend.
const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (res.status === 204) return null
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    const detail = data && data.detail ? data.detail : res.statusText
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }
  return data
}

export const api = {
  // Resumes
  listResumes: (params = {}) => {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v)
    ).toString()
    return request(`/resumes${qs ? `?${qs}` : ''}`)
  },
  getResume: (id) => request(`/resumes/${id}`),
  createResume: (body) => request('/resumes', { method: 'POST', body: JSON.stringify(body) }),
  updateResume: (id, body) => request(`/resumes/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  deleteResume: (id) => request(`/resumes/${id}`, { method: 'DELETE' }),

  // Versions
  addVersion: (resumeId, body) =>
    request(`/resumes/${resumeId}/versions`, { method: 'POST', body: JSON.stringify(body) }),
  updateVersion: (id, body) => request(`/versions/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  deleteVersion: (id) => request(`/versions/${id}`, { method: 'DELETE' }),

  // Tags
  listTags: () => request('/tags'),

  // Import (resume-engine)
  importFile: async (file) => {
    const form = new FormData()
    form.append('file', file)
    const res = await fetch(`${BASE}/import`, { method: 'POST', body: form })
    const data = await res.json().catch(() => null)
    if (!res.ok) throw new Error((data && data.detail) || 'Import failed')
    return data
  },

  // AI engine
  getAISettings: () => request('/ai/settings'),
  updateAISettings: (body) => request('/ai/settings', { method: 'PUT', body: JSON.stringify(body) }),
  diff: (versionAId, versionBId) =>
    request('/ai/diff', {
      method: 'POST',
      body: JSON.stringify({ version_a_id: versionAId, version_b_id: versionBId }),
    }),
}
