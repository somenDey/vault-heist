// The conversation with Gus, and the box for talking to him.

import { useEffect, useRef, useState, type FormEvent } from 'react'
import type { ChatMessage } from '../api/types'

const BLOCKED_REPLY = "[Blocked by the bank's security filter]"

/** Ways in for a first-time player. Choosing one fills the box; it isn't sent. */
const OPENERS = [
  'Evening, Gus. Quiet night?',
  'Head office sent me. Routine audit.',
  'Stuck on the crossword?',
]

interface Props {
  messages: ChatMessage[]
  /** True while waiting for Gus's reply. */
  thinking: boolean
  /** False when the player can't send (e.g. caught, or out of messages). */
  canSend: boolean
  maxLength: number
  onSend: (text: string) => void
}

export function Chat({ messages, thinking, canSend, maxLength, onSend }: Props) {
  const [draft, setDraft] = useState('')
  const endRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView?.({ behavior: 'smooth', block: 'end' })
  }, [messages.length, thinking])

  function submit(event: FormEvent) {
    event.preventDefault()
    const text = draft.trim()
    if (!text || thinking || !canSend) return
    onSend(text)
    setDraft('')
  }

  function chooseOpener(text: string) {
    setDraft(text)
    inputRef.current?.focus()
  }

  return (
    <section
      aria-label="Conversation with Gus"
      className="relative flex h-[72dvh] flex-col overflow-hidden lg:h-auto lg:min-h-0 lg:flex-1"
    >
      <ol className="flex-1 space-y-5 overflow-y-auto px-4 py-6 sm:px-8" aria-live="polite">
        {messages.length === 0 && (
          <li className="mx-auto max-w-md py-10 text-center">
            <p className="font-stencil text-4xl font-black text-chalk">Gus is on duty</p>
            <p className="mt-3 text-lg text-fog">
              He’s in his booth by the vault door, crossword on the desk, radio murmuring. Say
              something to him.
            </p>
            {canSend && (
              <div className="mt-6 flex flex-wrap justify-center gap-2">
                {OPENERS.map((opener) => (
                  <button
                    key={opener}
                    type="button"
                    onClick={() => chooseOpener(opener)}
                    className="rounded-full border border-rivet bg-steel/80 px-4 py-2 text-sm text-chalk transition hover:border-gold/60 hover:text-gold active:scale-[0.98]"
                  >
                    {opener}
                  </button>
                ))}
              </div>
            )}
          </li>
        )}
        {messages.map((message, index) => (
          <Message key={index} message={message} />
        ))}
        {thinking && (
          <li className="flex items-center gap-3 text-fog" role="status">
            <span className="font-stencil text-lg font-bold text-gold">Gus</span>
            <span className="flex gap-1" aria-hidden="true">
              {[0, 1, 2].map((dot) => (
                <span
                  key={dot}
                  className="size-1.5 animate-blink rounded-full bg-fog"
                  style={{ animationDelay: `${dot * 0.2}s` }}
                />
              ))}
            </span>
            <span className="sr-only">Gus is thinking…</span>
          </li>
        )}
        <div ref={endRef} />
      </ol>

      <form onSubmit={submit} className="px-4 pb-4 sm:px-8 sm:pb-6">
        <div className="plate flex gap-1.5 transition focus-within:border-gold/70">
          <label htmlFor="chat-input" className="sr-only">
            Your message to Gus
          </label>
          <input
            id="chat-input"
            name="message"
            ref={inputRef}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            maxLength={maxLength}
            disabled={!canSend}
            placeholder={canSend ? 'Say something to Gus…' : 'The conversation is over'}
            autoComplete="off"
            className="min-w-0 flex-1 rounded-[0.875rem] bg-transparent px-4 py-3 text-lg text-chalk placeholder:text-fog/70 focus:outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!canSend || thinking || !draft.trim()}
            className="btn-gold"
          >
            Send
          </button>
        </div>
      </form>
    </section>
  )
}

function Message({ message }: { message: ChatMessage }) {
  if (message.role === 'player') {
    return (
      <li className="ml-auto w-fit max-w-[85%] animate-rise rounded-2xl rounded-tr-sm border border-rivet bg-steel break-words px-5 py-3 text-lg text-chalk sm:max-w-[65%]">
        <span className="sr-only">You: </span>
        {message.text}
      </li>
    )
  }
  if (message.text === BLOCKED_REPLY) {
    return (
      <li className="w-fit max-w-[85%] animate-rise rounded-2xl rounded-tl-sm border-2 border-dashed border-alarm/80 bg-alarm/10 px-5 py-3 sm:max-w-[65%]">
        <span className="block font-stencil text-xl font-black tracking-wide text-alarm">
          Blocked by the filter
        </span>
        <span className="text-lg text-chalk">
          The bank’s security filter blocked what Gus was about to say.
        </span>
      </li>
    )
  }
  return (
    <li className="w-fit max-w-[85%] animate-rise rounded-2xl rounded-tl-sm bg-paper break-words px-5 py-3 text-ink shadow-[0_14px_30px_-16px_rgb(0_0_0/0.9),inset_0_-2px_0_rgb(0_0_0/0.08)] sm:max-w-[65%]">
      <span className="block font-stencil text-xl font-black tracking-wide text-gold-deep">
        Gus
      </span>
      <span className="text-lg">{message.text}</span>
    </li>
  )
}
