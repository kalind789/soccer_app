// Every call to the backend goes through this file, so components never build URLs themselves.

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

// Matches DrillRead in backend/app/schemas.py.
export type Drill = {
  id: number
  name: string
  description: string
  objective: string
  archived: boolean
}

// Matches DrillCreate: only name is required.
export type NewDrill = {
  name: string
  description?: string
  objective?: string
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  })
  if (!response.ok) {
    // FastAPI puts the reason in "detail". For a 422 it's a list of problems; for a 404 it's a sentence.
    const body = await response.json().catch(() => ({}))
    const detail = typeof body.detail === 'string' ? body.detail : `Request failed (${response.status})`
    throw new Error(detail)
  }
  return response.json()
}

export function listDrills(search: string, includeArchived: boolean): Promise<Drill[]> {
  const params = new URLSearchParams()
  if (search) params.set('search', search)
  if (includeArchived) params.set('include_archived', 'true')
  return request(`/drills?${params}`)
}

export function createDrill(drill: NewDrill): Promise<Drill> {
  return request('/drills', { method: 'POST', body: JSON.stringify(drill) })
}

export function archiveDrill(id: number): Promise<Drill> {
  return request(`/drills/${id}/archive`, { method: 'POST' })
}

export function unarchiveDrill(id: number): Promise<Drill> {
  return request(`/drills/${id}/unarchive`, { method: 'POST' })
}
