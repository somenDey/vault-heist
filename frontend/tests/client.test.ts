import { afterEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError, NETWORK_ERROR } from '../src/api/client'

function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function mockFetch(...responses: Response[]) {
  const fetchMock = vi.fn()
  for (const response of responses) fetchMock.mockResolvedValueOnce(response)
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('api client', () => {
  it('creates a session on first use and sends it with every request', async () => {
    const fetchMock = mockFetch(json(201, { session_id: 'abc' }), json(200, []), json(200, []))

    await api.listLevels()
    await api.listLevels()

    expect(fetchMock).toHaveBeenCalledTimes(3) // One session, then two calls using it.
    const [, init] = fetchMock.mock.calls[2] as [string, RequestInit]
    expect((init.headers as Record<string, string>)['X-Session-ID']).toBe('abc')
  })

  it('starts a new session if the server no longer knows the old one', async () => {
    localStorage.setItem('vault-heist.session', 'stale')
    mockFetch(
      json(401, { error: { code: 'invalid_session', message: 'Unknown session.' } }),
      json(201, { session_id: 'fresh' }),
      json(200, []),
    )

    await expect(api.listLevels()).resolves.toEqual([])
    expect(localStorage.getItem('vault-heist.session')).toBe('fresh')
  })

  it('turns error responses into ApiError with the stable code', async () => {
    localStorage.setItem('vault-heist.session', 'abc')
    mockFetch(json(404, { error: { code: 'unknown_level', message: 'There is no level 9.' } }))

    await expect(api.getLevel(9)).rejects.toMatchObject({
      status: 404,
      code: 'unknown_level',
      message: 'There is no level 9.',
    })
  })

  it('explains when the backend is not running', async () => {
    localStorage.setItem('vault-heist.session', 'abc')
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    const error = await api.listLevels().catch((err: unknown) => err)

    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).code).toBe(NETWORK_ERROR)
  })
})
