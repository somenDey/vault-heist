// The box for guessing the vault code. Separate from the chat: Gus never sees guesses.

import { useState, type FormEvent } from 'react'

interface Props {
  onGuess: (guess: string) => void
  busy: boolean
  /** Bumped by the parent after a wrong guess, to shake the input. */
  wrongGuesses: number
}

export function VaultCodeInput({ onGuess, busy, wrongGuesses }: Props) {
  const [code, setCode] = useState('')

  function submit(event: FormEvent) {
    event.preventDefault()
    const guess = code.trim()
    if (!guess || busy) return
    onGuess(guess)
  }

  return (
    <form onSubmit={submit}>
      <label htmlFor="vault-code" className="block font-stencil text-2xl font-bold text-chalk">
        Enter vault code
      </label>
      <p className="mt-1 text-sm text-fog">One word. Gus never sees your guesses.</p>
      <div
        key={wrongGuesses}
        className={`mt-4 space-y-2 ${wrongGuesses > 0 ? 'animate-shake' : ''}`}
      >
        <input
          id="vault-code"
          name="code"
          value={code}
          onChange={(event) => setCode(event.target.value)}
          maxLength={64}
          autoComplete="off"
          spellCheck={false}
          className={`w-full rounded-[0.625rem] border bg-night/80 px-4 py-3 text-center font-stencil text-3xl font-bold tracking-[0.3em] text-gold uppercase shadow-[inset_0_2px_8px_rgb(0_0_0/0.5)] transition-colors focus:border-gold focus:outline-none ${
            wrongGuesses > 0 ? 'border-alarm/70' : 'border-rivet'
          }`}
        />
        <button type="submit" disabled={busy || !code.trim()} className="w-full btn-gold">
          Try code
        </button>
      </div>
      {wrongGuesses > 0 && (
        <p role="status" className="mt-3 text-sm text-alarm">
          Wrong code. The vault stays shut.
        </p>
      )}
    </form>
  )
}
