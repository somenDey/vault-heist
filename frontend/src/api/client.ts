// A small typed client for the backend API.
//
// It creates an anonymous session on first use, remembers it in localStorage,
// sends it as X-Session-ID, and starts a new one if the server forgets it.

import type {
  ChatResponse,
  ErrorResponse,
  GuessResponse,
  LevelState,
  LevelSummary,
  SessionResponse,
} from './types'

export const API_URL: string = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const SESSION_KEY = 'vault-heist.session'

/** An error from the API, with its stable `code` (see docs/architecture.md). */
export class ApiError extends Error {
  readonly status: number
  readonly code: string

  constructor(status: number, code: string, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

/** The backend couldn't be reached at all. */
export const NETWORK_ERROR = 'network_error'

async function send(path: string, init: RequestInit = {}): Promise<Response> {
  try {
    return await fetch(`${API_URL}${path}`, init)
  } catch {
    throw new ApiError(
      0,
      NETWORK_ERROR,
      "Can't reach the bank's server. Is the backend running (just dev)?",
    )
  }
}

async function parse<T>(response: Response): Promise<T> {
  const body: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    const error = (body as ErrorResponse | null)?.error
    throw new ApiError(
      response.status,
      error?.code ?? 'unknown_error',
      error?.message ?? `Request failed (${response.status}).`,
    )
  }
  return body as T
}

async function sessionId(): Promise<string> {
  const saved = localStorage.getItem(SESSION_KEY)
  if (saved) return saved
  const created = await parse<SessionResponse>(await send('/api/sessions', { method: 'POST' }))
  localStorage.setItem(SESSION_KEY, created.session_id)
  return created.session_id
}

/** Call the API as the current player, renewing the session once if it's unknown. */
async function call<T>(path: string, body?: unknown): Promise<T> {
  for (let attempt = 1; ; attempt++) {
    const response = await send(path, {
      method: body === undefined ? 'GET' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-ID': await sessionId(),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
    if (response.status === 401 && attempt === 1) {
      localStorage.removeItem(SESSION_KEY) // The server forgot us (e.g. a new database).
      continue
    }
    return parse<T>(response)
  }
}

export const api = {
  listLevels: () => call<LevelSummary[]>('/api/levels'),
  getLevel: (levelId: number) => call<LevelState>(`/api/levels/${levelId}`),
  chat: (levelId: number, message: string) =>
    call<ChatResponse>(`/api/levels/${levelId}/chat`, { message }),
  guess: (levelId: number, guess: string) =>
    call<GuessResponse>(`/api/levels/${levelId}/guess`, { guess }),
  reset: (levelId: number) => call<LevelState>(`/api/levels/${levelId}/reset`, {}),
}

export type Api = typeof api
