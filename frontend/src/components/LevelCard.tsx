// One level on the start screen, drawn as a safe-deposit box. The number of keyholes
// shows how well guarded it is; the lamp lights up once the player has cracked it.

import { Link } from 'react-router'
import type { LevelSummary } from '../api/types'

function Keyhole() {
  return (
    <svg viewBox="0 0 20 30" className="h-7 w-5" aria-hidden="true">
      <circle cx="10" cy="10" r="9" fill="#06080c" stroke="#3a4757" strokeWidth="1.5" />
      <path d="M10 6.5a3 3 0 0 1 1.6 5.5l1.4 6h-6l1.4-6A3 3 0 0 1 10 6.5Z" fill="#93a0b0" />
    </svg>
  )
}

export function LevelCard({ level }: { level: LevelSummary }) {
  return (
    <li>
      <Link
        to={`/levels/${level.id}`}
        className="group plate block h-full transition duration-500 ease-heavy hover:-translate-y-1.5 hover:border-gold/60 hover:shadow-[0_36px_60px_-30px_rgb(245_184_61/0.35)]"
      >
        <span className="brushed flex h-full flex-col rounded-[calc(1.25rem-0.375rem)] p-6 shadow-[inset_0_1px_0_rgb(255_255_255/0.08)]">
          <span className="flex items-start justify-between">
            {/* The number plate */}
            <span
              aria-hidden="true"
              className="rounded-lg border border-rivet bg-night/70 px-4 py-1 font-stencil text-6xl leading-none font-black text-gold shadow-[inset_0_2px_6px_rgb(0_0_0/0.6)]"
            >
              {level.id}
            </span>
            <span className="flex items-center gap-2 text-sm font-semibold">
              <span
                aria-hidden="true"
                className={`size-3 rounded-full ${
                  level.cleared
                    ? 'bg-gold shadow-[0_0_14px_2px_rgb(245_184_61/0.7)]'
                    : 'border border-rivet bg-night'
                }`}
              />
              <span className={level.cleared ? 'text-gold' : 'text-fog'}>
                {level.cleared ? 'Cracked' : 'Not cracked'}
              </span>
            </span>
          </span>

          <span className="mt-10 block font-stencil text-4xl leading-none font-black text-chalk transition-colors group-hover:text-gold">
            <span className="sr-only">Level {level.id}: </span>
            {level.name}
          </span>
          <span className="mt-3 block text-fog">{level.description}</span>

          <span className="mt-auto flex items-center justify-between pt-8">
            <span className="flex gap-2" aria-hidden="true">
              {Array.from({ length: level.id }, (_, lock) => (
                <Keyhole key={lock} />
              ))}
            </span>
            <span className="font-semibold text-chalk transition group-hover:text-gold">Play</span>
          </span>
        </span>
      </Link>
    </li>
  )
}
