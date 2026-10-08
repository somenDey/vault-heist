// The suspicion scale, shared by the meter and its tests.

export const MAX_SUSPICION = 10

/** The needle's angle in degrees: -90 (far left, 0) to +90 (far right, 10). */
export function needleAngle(value: number): number {
  const clamped = Math.min(Math.max(value, 0), MAX_SUSPICION)
  return -90 + (clamped / MAX_SUSPICION) * 180
}

/** Gus's mood, in words, for a suspicion value. */
export function describeSuspicion(value: number): string {
  if (value >= MAX_SUSPICION) return 'Calling security'
  if (value >= 8) return 'Alarmed'
  if (value >= 5) return 'Wary'
  if (value >= 3) return 'Curious'
  return 'Relaxed'
}
