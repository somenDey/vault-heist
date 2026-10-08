// The moment an attempt ends: the alarm going off, or the vault swinging open.

import type { ReactNode } from 'react'
import { VaultDoor } from './VaultDoor'

interface Props {
  tone: 'caught' | 'won'
  title: string
  children: ReactNode
  actions: ReactNode
}

export function OutcomeDialog({ tone, title, children, actions }: Props) {
  const caught = tone === 'caught'
  return (
    <div className="fixed inset-0 z-30 flex overscroll-contain items-center justify-center bg-night/80 p-4 backdrop-blur-sm">
      {caught && (
        <div
          aria-hidden="true"
          className="pointer-events-none fixed inset-0 animate-alarm bg-[radial-gradient(circle_at_50%_50%,transparent_20%,var(--color-alarm)_120%)]"
        />
      )}
      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="outcome-title"
        className={`plate relative w-full max-w-xl animate-rise ${caught ? 'border-alarm/60' : 'border-gold/60'}`}
      >
        <div className="plate-core p-6 text-center sm:p-8">
          {!caught && <VaultDoor open className="mx-auto mb-6 w-44" />}
          <h2
            id="outcome-title"
            className={`font-stencil text-4xl leading-none sm:text-5xl font-black ${caught ? 'text-alarm' : 'text-gold'}`}
          >
            {title}
          </h2>
          <div className="mx-auto mt-4 max-w-[40ch] text-lg text-balance text-chalk/90">
            {children}
          </div>
          <div className="mt-8 flex flex-wrap justify-center gap-3">{actions}</div>
        </div>
      </div>
    </div>
  )
}
