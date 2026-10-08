// Gus at his booth: who the player is talking to, and how he's feeling right now.

import { describeSuspicion } from './suspicion'

export function GuardBadge({ suspicion }: { suspicion: number }) {
  const alarmed = suspicion >= 8
  return (
    <div className="flex items-center gap-4 border-b border-rivet/60 bg-night/40 px-4 py-3 sm:px-8">
      <span
        aria-hidden="true"
        className="grid size-12 shrink-0 place-items-center rounded-full bg-gradient-to-br from-[#ffe3a1] via-gold to-gold-deep p-[3px]"
      >
        <span className="grid size-full place-items-center rounded-full bg-steel font-stencil text-2xl font-black text-gold">
          G
        </span>
      </span>
      <span className="leading-tight">
        <span className="block font-stencil text-2xl font-black text-chalk">Gus</span>
        <span className="block text-sm text-fog">
          Night guard<span className="hidden sm:inline">, Granite &amp; Sons Savings</span>
        </span>
      </span>
      <span
        aria-hidden="true"
        className={`ml-auto flex items-center gap-2 rounded-full border px-3 py-1 text-sm font-semibold transition-colors duration-700 ${
          alarmed ? 'border-alarm/60 text-alarm' : 'border-rivet text-chalk'
        }`}
      >
        <span
          className={`size-2 rounded-full transition-colors duration-700 ${alarmed ? 'bg-alarm' : 'bg-gold'}`}
        />
        {describeSuspicion(suspicion)}
      </span>
    </div>
  )
}
