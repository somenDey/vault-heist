// Types for the backend API. They mirror backend/app/api/schemas.py:
// change one, change the other.

export interface SessionResponse {
  session_id: string
}

export interface LevelSummary {
  id: number
  name: string
  description: string
  cleared: boolean
}

export interface ChatMessage {
  role: 'player' | 'guard'
  text: string
  /** Gus's suspicion after this reply; null for the player's messages. */
  suspicion: number | null
}

export interface AttemptState {
  suspicion: number
  messages_left: number
  /** Wrong guesses left before Gus hears the dial and calls security. */
  guesses_left: number
  messages: ChatMessage[]
}

export interface LevelState {
  level: LevelSummary
  /** null when no attempt is under way: the next message starts one. */
  attempt: AttemptState | null
}

export interface ChatResponse {
  reply: string
  suspicion: number
  caught: boolean
  blocked_by_filter: boolean
  messages_left: number
}

export interface GuessResponse {
  correct: boolean
  /** That was the last wrong guess allowed: Gus called security. */
  caught: boolean
  guesses_left: number
}

export interface ErrorResponse {
  error: { code: string; message: string }
}
