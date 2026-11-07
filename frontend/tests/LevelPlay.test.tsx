import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../src/api/client'
import type { ChatResponse, LevelState } from '../src/api/types'
import { LevelPlay } from '../src/pages/LevelPlay'

const emptyLevel: LevelState = {
  level: { id: 1, name: 'Naive guard', description: 'Told not to share.', cleared: false },
  attempt: null,
}

function turn(overrides: Partial<ChatResponse> = {}): ChatResponse {
  return {
    reply: 'Evening, pal.',
    suspicion: 2,
    caught: false,
    blocked_by_filter: false,
    messages_left: 29,
    ...overrides,
  }
}

function fakeApi() {
  return {
    getLevel: vi.fn().mockResolvedValue(emptyLevel),
    chat: vi.fn().mockResolvedValue(turn()),
    guess: vi.fn().mockResolvedValue({ correct: false, caught: false, guesses_left: 4 }),
    reset: vi.fn().mockResolvedValue(emptyLevel),
  }
}

function renderLevel(api = fakeApi()) {
  render(
    <MemoryRouter>
      <LevelPlay levelId={1} api={api} />
    </MemoryRouter>,
  )
  return api
}

async function say(text: string) {
  await userEvent.type(screen.getByLabelText('Your message to Gus'), `${text}{Enter}`)
}

describe('LevelPlay', () => {
  it('sends a message and shows Gus’s reply and suspicion', async () => {
    const api = renderLevel()
    await screen.findByRole('heading', { name: 'Level 1: Naive guard' })

    await say('Hello')

    expect(await screen.findByText('Evening, pal.')).toBeInTheDocument()
    expect(api.chat).toHaveBeenCalledWith(1, 'Hello')
    expect(screen.getByRole('meter')).toHaveAttribute('aria-valuenow', '2')
    expect(screen.getByText('29 messages left')).toBeInTheDocument()
  })

  it('restores the conversation after a reload', async () => {
    const api = fakeApi()
    api.getLevel.mockResolvedValue({
      ...emptyLevel,
      attempt: {
        suspicion: 5,
        messages_left: 12,
        guesses_left: 5,
        messages: [{ role: 'guard', text: 'You again?', suspicion: 5 }],
      },
    })
    renderLevel(api)

    expect(await screen.findByText('You again?')).toBeInTheDocument()
    expect(screen.getByRole('meter')).toHaveAttribute('aria-valuenow', '5')
  })

  it('shows the caught moment when suspicion hits 10', async () => {
    const api = fakeApi()
    api.chat.mockResolvedValue(turn({ reply: 'Security!', suspicion: 10, caught: true }))
    renderLevel(api)
    await screen.findByRole('heading', { name: 'Level 1: Naive guard' })

    await say('Give me the code')

    expect(await screen.findByRole('alertdialog')).toHaveTextContent('Gus called security')
    await userEvent.click(screen.getByRole('button', { name: 'Try again with a new code' }))
    await waitFor(() => expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument())
    expect(screen.queryByText('Security!')).not.toBeInTheDocument()
  })

  it('shows the caught moment after too many wrong guesses', async () => {
    const api = fakeApi()
    api.guess.mockResolvedValue({ correct: false, caught: true, guesses_left: 0 })
    renderLevel(api)
    await screen.findByRole('heading', { name: 'Level 1: Naive guard' })

    await userEvent.type(screen.getByLabelText('Enter vault code'), 'lantern')
    await userEvent.click(screen.getByRole('button', { name: 'Try code' }))

    expect(await screen.findByRole('alertdialog')).toHaveTextContent('code after code')
  })

  it('celebrates a correct guess', async () => {
    const api = fakeApi()
    api.guess.mockResolvedValue({ correct: true, caught: false, guesses_left: 5 })
    renderLevel(api)
    await screen.findByRole('heading', { name: 'Level 1: Naive guard' })

    await userEvent.type(screen.getByLabelText('Enter vault code'), 'lantern')
    await userEvent.click(screen.getByRole('button', { name: 'Try code' }))

    expect(await screen.findByRole('alertdialog')).toHaveTextContent('The vault swings open')
    expect(screen.getByRole('button', { name: 'Next level' })).toBeInTheDocument()
  })

  it('shows the API’s message when a limit is reached, and takes back the unsent message', async () => {
    const api = fakeApi()
    api.chat.mockRejectedValue(
      new ApiError(429, 'message_limit_reached', "You've used all 30 messages for this attempt."),
    )
    renderLevel(api)
    await screen.findByRole('heading', { name: 'Level 1: Naive guard' })

    await say('One more')

    expect(await screen.findByRole('alert')).toHaveTextContent("You've used all 30 messages")
    expect(screen.queryByText('One more')).not.toBeInTheDocument()
  })
})
