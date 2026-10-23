// Every call to the backend goes through this file, so components never build URLs themselves.
// The types below mirror backend/app/schemas.py. If you change one, change the other.

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

// --- Drills ---

// Matches DrillRead.
export type Drill = {
  id: number
  name: string
  description: string
  objective: string
  archived: boolean
}

// Matches DrillCreate and DrillUpdate: what a coach can type in.
export type DrillFields = {
  name: string
  description: string
  objective: string
}

// --- Session plans ---

// Matches SessionPlanCreate and SessionPlanUpdate.
export type PlanFields = {
  title: string
  focus: string
  location: string
  notes: string
  date: string // "2026-11-03"
  start_time: string // "18:00" (the backend sends back "18:00:00")
  end_time: string
}

// Matches SessionPlanSummary: the short version, used in lists.
export type PlanSummary = Omit<PlanFields, 'notes'> & {
  id: number
  duration_minutes: number
  planned_minutes: number // Total of the drills' minutes.
  drill_count: number
}

// Matches SessionDrillRead: one drill in a plan, and how long it runs there.
export type Slot = {
  drill: Drill
  minutes: number
}

// Matches SessionPlanRead: the full version.
export type Plan = PlanSummary & {
  notes: string
  slots: Slot[]
}

// Matches SessionDrillEntry: what we send to replace a plan's drill list.
export type SlotEntry = {
  drill_id: number
  minutes: number
}

// --- The one function that talks to the server ---

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  })
  if (!response.ok) {
    throw new Error(await errorMessage(response))
  }
  if (response.status === 204) {
    return undefined as T // 204 No Content: nothing to read.
  }
  return response.json()
}

// FastAPI puts the reason in "detail": a sentence for our own errors (404, end time before start),
// or a list of problems when Pydantic rejects the data.
async function errorMessage(response: Response): Promise<string> {
  const body = await response.json().catch(() => ({}))
  if (typeof body.detail === 'string') return body.detail
  if (Array.isArray(body.detail)) return body.detail.map((problem: { msg: string }) => problem.msg).join('. ')
  return `Request failed (${response.status})`
}

function send<T>(method: string, path: string, body?: unknown): Promise<T> {
  return request(path, { method, body: body === undefined ? undefined : JSON.stringify(body) })
}

// --- Drill calls ---

export function listDrills(search = '', includeArchived = false): Promise<Drill[]> {
  const params = new URLSearchParams()
  if (search) params.set('search', search)
  if (includeArchived) params.set('include_archived', 'true')
  return request(`/drills?${params}`)
}

export const createDrill = (fields: DrillFields) => send<Drill>('POST', '/drills', fields)
export const updateDrill = (id: number, fields: DrillFields) => send<Drill>('PATCH', `/drills/${id}`, fields)
export const archiveDrill = (id: number) => send<Drill>('POST', `/drills/${id}/archive`)
export const unarchiveDrill = (id: number) => send<Drill>('POST', `/drills/${id}/unarchive`)

// --- Session plan calls ---

export const listPlans = () => request<PlanSummary[]>('/session-plans')
export const getPlan = (id: number) => request<Plan>(`/session-plans/${id}`)
export const createPlan = (fields: PlanFields) => send<Plan>('POST', '/session-plans', fields)
export const updatePlan = (id: number, fields: PlanFields) => send<Plan>('PATCH', `/session-plans/${id}`, fields)
export const deletePlan = (id: number) => send<void>('DELETE', `/session-plans/${id}`)
export const setPlanDrills = (id: number, drills: SlotEntry[]) =>
  send<Plan>('PUT', `/session-plans/${id}/drills`, { drills })
