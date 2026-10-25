// Every call to the backend goes through this file, so components never build URLs themselves.
// The types below mirror backend/app/schemas.py. If you change one, change the other.

import { supabase } from './supabase'

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

// --- Teams ---

// Matches TeamRef: enough to show which team something belongs to.
export type TeamRef = {
  id: number
  name: string
}

// Matches TeamRead.
export type Team = TeamRef & {
  plan_count: number
}

// Matches TeamCreate and TeamUpdate.
export type TeamFields = {
  name: string
}

// --- Session plans ---

// Matches SessionPlanCreate and SessionPlanUpdate.
export type PlanFields = {
  team_id: number
  title: string
  focus: string
  location: string
  notes: string
  date: string // "2026-11-03"
  start_time: string // "18:00" (the backend sends back "18:00:00")
  end_time: string
}

// Matches SessionPlanSummary: the short version, used in lists.
export type PlanSummary = Omit<PlanFields, 'notes' | 'team_id'> & {
  id: number
  team: TeamRef
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
  // The login token proves who we are. getSession() refreshes it first if it has expired.
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  })
  if (response.status === 401) {
    // The backend doesn't accept our login anymore: log out, which brings back the login page.
    await supabase.auth.signOut()
  }
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

// --- Team calls ---

export const listTeams = () => request<Team[]>('/teams')
export const createTeam = (fields: TeamFields) => send<Team>('POST', '/teams', fields)
export const updateTeam = (id: number, fields: TeamFields) => send<Team>('PATCH', `/teams/${id}`, fields)
export const deleteTeam = (id: number) => send<void>('DELETE', `/teams/${id}`)

// --- Session plan calls ---

export const listPlans = (teamId?: number) =>
  request<PlanSummary[]>(teamId === undefined ? '/session-plans' : `/session-plans?team_id=${teamId}`)
export const getPlan = (id: number) => request<Plan>(`/session-plans/${id}`)
export const createPlan = (fields: PlanFields) => send<Plan>('POST', '/session-plans', fields)
export const updatePlan = (id: number, fields: PlanFields) => send<Plan>('PATCH', `/session-plans/${id}`, fields)
export const deletePlan = (id: number) => send<void>('DELETE', `/session-plans/${id}`)
export const setPlanDrills = (id: number, drills: SlotEntry[]) =>
  send<Plan>('PUT', `/session-plans/${id}/drills`, { drills })
