// Playing one level: chat with Gus, watch his suspicion, guess the code.

import { useCallback, useEffect, useState, type CSSProperties } from 'react'
import { Link, useNavigate } from 'react-router'
import { ApiError, type Api } from '../api/client'
import type { ChatMessage, LevelState, LevelSummary } from '../api/types'
import { Chat } from '../components/Chat'
import { OutcomeDialog } from '../components/OutcomeDialog'
import { SuspicionMeter } from '../components/SuspicionMeter'
import { MAX_SUSPICION } from '../components/suspicion'
import { VaultCodeInput } from '../components/VaultCodeInput'
import { VaultDoor } from '../components/VaultDoor'
import { GuardBadge } from '../components/GuardBadge'

const LAST_LEVEL = 3
const MAX_MESSAGE_CHARS = 500

type Outcome = 'playing' | 'caught' | 'won'

/** What to tell the player when a request fails. API messages are written for players. */
function errorMessage(err: unknown): string {
  return err instanceof ApiError ? err.message : 'Something went wrong. Try again.'
}

interface Props {
  levelId: number
  api: Pick<Api, 'getLevel' | 'chat' | 'guess' | 'reset'>
}

export function LevelPlay({ levelId, api }: Props) {
  const navigate = useNavigate()
  const [level, setLevel] = useState<LevelSummary | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [suspicion, setSuspicion] = useState(0)
  const [messagesLeft, setMessagesLeft] = useState<number | null>(null)
  const [outcome, setOutcome] = useState<Outcome>('playing')
  const [busy, setBusy] = useState(false)
  const [wrongGuesses, setWrongGuesses] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const showError = useCallback((err: unknown) => setError(errorMessage(err)), [])

  /** Show a level exactly as the server has it. */
  const apply = useCallback((state: LevelState) => {
    setLevel(state.level)
    setMessages(state.attempt?.messages ?? [])
    setSuspicion(state.attempt?.suspicion ?? 0)
    setMessagesLeft(state.attempt?.messages_left ?? null)
    setOutcome('playing')
    setWrongGuesses(0)
    setError(null)
  }, [])

  const load = useCallback(
    () => api.getLevel(levelId).then(apply).catch(showError),
    [api, levelId, apply, showError],
  )

  useEffect(() => {
    let current = true // Ignore a slow reply that arrives after leaving this level.
    api
      .getLevel(levelId)
      .then((state) => current && apply(state))
      .catch((err: unknown) => current && showError(err))
    return () => {
      current = false
    }
  }, [api, levelId, apply, showError])

  async function send(text: string) {
    setError(null)
    setBusy(true)
    setMessages((current) => [...current, { role: 'player', text, suspicion: null }])
    try {
      const turn = await api.chat(levelId, text)
      setMessages((current) => [
        ...current,
        { role: 'guard', text: turn.reply, suspicion: turn.suspicion },
      ])
      setSuspicion(turn.suspicion)
      setMessagesLeft(turn.messages_left)
      if (turn.caught) setOutcome('caught')
    } catch (err) {
      setMessages((current) => current.slice(0, -1)) // The message wasn't delivered.
      showError(err)
    } finally {
      setBusy(false)
    }
  }

  async function guess(code: string) {
    setError(null)
    setBusy(true)
    try {
      const result = await api.guess(levelId, code)
      if (result.correct) setOutcome('won')
      else setWrongGuesses((count) => count + 1)
    } catch (err) {
      showError(err)
    } finally {
      setBusy(false)
    }
  }

  async function reset() {
    setBusy(true)
    try {
      apply(await api.reset(levelId))
    } catch (err) {
      showError(err)
    } finally {
      setBusy(false)
    }
  }

  const outOfMessages = messagesLeft === 0
  const heat = { '--heat': suspicion / MAX_SUSPICION } as CSSProperties

  return (
    <div className="flex min-h-dvh flex-col lg:h-dvh" style={heat}>
      <div className="roomlight" />
      <header className="flex flex-wrap items-center gap-x-6 gap-y-2 border-b border-rivet/60 px-4 py-3 sm:px-8">
        <Link to="/" className="text-fog underline-offset-4 hover:text-chalk hover:underline">
          All levels
        </Link>
        {level && (
          <div className="order-last basis-full md:order-none md:basis-auto md:flex-1">
            <h1 className="flex items-baseline gap-3 font-stencil leading-none">
              <span className="text-lg font-bold whitespace-nowrap text-fog">
                Level {level.id}
                <span className="sr-only">:</span>
              </span>{' '}
              <span className="text-3xl font-black text-gold">{level.name}</span>
            </h1>
            <p className="mt-1 hidden text-sm text-fog md:block">{level.description}</p>
          </div>
        )}
        <p className="ml-auto shrink-0 text-right font-stencil text-lg leading-tight font-bold text-chalk tabular-nums">
          <span className="text-fog">
            {messagesLeft === null
              ? 'No messages yet'
              : outOfMessages
                ? 'No messages left'
                : `${messagesLeft} messages left`}
          </span>
        </p>
      </header>

      {error && (
        <p
          role="alert"
          className="border-b border-alarm/50 bg-alarm/15 px-4 py-2.5 text-chalk sm:px-8"
        >
          {error}
        </p>
      )}

      <div className="flex flex-1 flex-col lg:min-h-0 lg:flex-row">
        <div className="relative flex flex-1 flex-col overflow-hidden lg:min-h-0">
          {/* The vault itself, looming behind the conversation. */}
          <div
            aria-hidden="true"
            className="pointer-events-none absolute top-1/2 right-0 -z-10 hidden w-[44rem] translate-x-[55%] -translate-y-1/2 opacity-40 [mask-image:linear-gradient(to_right,black_20%,transparent_70%)] lg:block"
          >
            <VaultDoor />
          </div>
          <GuardBadge suspicion={suspicion} />
          <Chat
            messages={messages}
            thinking={busy && messages.at(-1)?.role === 'player'}
            canSend={outcome === 'playing' && !outOfMessages}
            maxLength={MAX_MESSAGE_CHARS}
            onSend={(text) => void send(text)}
          />
        </div>

        <aside className="flex flex-col gap-4 border-t border-rivet/60 p-4 sm:p-6 lg:w-96 lg:overflow-y-auto lg:border-t-0 lg:border-l">
          <div className="plate">
            <div className="plate-core px-4 pt-6 pb-5">
              <SuspicionMeter value={suspicion} />
            </div>
          </div>
          <div className="plate">
            <div className="plate-core p-5">
              <VaultCodeInput
                busy={busy || outcome !== 'playing'}
                wrongGuesses={wrongGuesses}
                onGuess={(code) => void guess(code)}
              />
            </div>
          </div>
          <button
            type="button"
            onClick={() => void reset()}
            disabled={busy}
            className="mt-auto py-2 text-sm text-fog underline underline-offset-4 transition hover:text-chalk disabled:opacity-40"
          >
            Start over with a new code
          </button>
        </aside>
      </div>

      {outcome === 'caught' && (
        <OutcomeDialog
          tone="caught"
          title="Gus called security"
          actions={
            <button type="button" autoFocus onClick={() => void load()} className="btn-alarm">
              Try again with a new code
            </button>
          }
        >
          His suspicion hit 10. The code has been changed and Gus won’t remember you.
        </OutcomeDialog>
      )}

      {outcome === 'won' && (
        <OutcomeDialog
          tone="won"
          title="The vault swings open"
          actions={
            <>
              {levelId < LAST_LEVEL && (
                <button
                  type="button"
                  autoFocus
                  onClick={() => navigate(`/levels/${levelId + 1}`)}
                  className="btn-gold"
                >
                  Next level
                </button>
              )}
              <Link to="/" className="btn-ghost" autoFocus={levelId >= LAST_LEVEL}>
                All levels
              </Link>
            </>
          }
        >
          {levelId < LAST_LEVEL
            ? `Level ${levelId} cracked. Gus is going to have some explaining to do.`
            : 'You’ve cracked every vault. Gus is updating his CV.'}
        </OutcomeDialog>
      )}
    </div>
  )
}
