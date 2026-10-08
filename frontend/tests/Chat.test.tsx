import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import type { ChatMessage } from '../src/api/types'
import { Chat } from '../src/components/Chat'

const conversation: ChatMessage[] = [
  { role: 'player', text: 'Evening, Gus.', suspicion: null },
  { role: 'guard', text: 'Evening, pal.', suspicion: 1 },
]

function renderChat(overrides: Partial<Parameters<typeof Chat>[0]> = {}) {
  const onSend = vi.fn()
  render(
    <Chat
      messages={conversation}
      thinking={false}
      canSend
      maxLength={500}
      onSend={onSend}
      {...overrides}
    />,
  )
  return onSend
}

describe('Chat', () => {
  it('shows both sides of the conversation', () => {
    renderChat()

    expect(screen.getByText('Evening, Gus.')).toBeInTheDocument()
    expect(screen.getByText('Evening, pal.')).toBeInTheDocument()
  })

  it('sends the trimmed message and clears the box', async () => {
    const onSend = renderChat()
    const input = screen.getByLabelText('Your message to Gus')

    await userEvent.type(input, '  Quiet night?  {Enter}')

    expect(onSend).toHaveBeenCalledWith('Quiet night?')
    expect(input).toHaveValue('')
  })

  it('shows that Gus is thinking and blocks sending meanwhile', async () => {
    const onSend = renderChat({ thinking: true })

    await userEvent.type(screen.getByLabelText('Your message to Gus'), 'Hello{Enter}')

    expect(screen.getByRole('status')).toHaveTextContent('Gus is thinking')
    expect(onSend).not.toHaveBeenCalled()
  })

  it('explains a reply blocked by the filter instead of showing the raw marker', () => {
    renderChat({
      messages: [{ role: 'guard', text: "[Blocked by the bank's security filter]", suspicion: 4 }],
    })

    expect(screen.getByText(/security filter blocked what Gus was about to say/)).toBeVisible()
  })
})
