import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { VaultCodeInput } from '../src/components/VaultCodeInput'

describe('VaultCodeInput', () => {
  it('submits the trimmed code', async () => {
    const onGuess = vi.fn()
    render(<VaultCodeInput onGuess={onGuess} busy={false} wrongGuesses={0} />)

    await userEvent.type(screen.getByLabelText('Enter vault code'), ' lantern ')
    await userEvent.click(screen.getByRole('button', { name: 'Try code' }))

    expect(onGuess).toHaveBeenCalledWith('lantern')
  })

  it('cannot submit an empty code', () => {
    render(<VaultCodeInput onGuess={vi.fn()} busy={false} wrongGuesses={0} />)

    expect(screen.getByRole('button', { name: 'Try code' })).toBeDisabled()
  })

  it('says when a guess was wrong', () => {
    render(<VaultCodeInput onGuess={vi.fn()} busy={false} wrongGuesses={1} />)

    expect(screen.getByRole('status')).toHaveTextContent('Wrong code')
  })
})
