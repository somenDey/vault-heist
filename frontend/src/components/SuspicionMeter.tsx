// Gus's suspicion as a brass-rimmed instrument gauge: the needle swings, the arc fills,
// and everything warms from gold to alarm red as he gets closer to calling security.

import type { CSSProperties } from 'react'
import { describeSuspicion, MAX_SUSPICION as MAX, needleAngle } from './suspicion'

/** Gold at 0, alarm red at 10, following --heat. */
const HEAT_COLOUR =
  'color-mix(in oklab, var(--color-gold) calc(100% - var(--heat) * 100%), var(--color-alarm))'

const CX = 120
const CY = 120
const ARC_R = 86
const ARC = `M ${CX - ARC_R} ${CY} A ${ARC_R} ${ARC_R} 0 0 1 ${CX + ARC_R} ${CY}`
/** The red band from 8 to 10: Gus is alarmed. */
const DANGER = `M ${CX + ARC_R * Math.cos((Math.PI * 2) / 10)} ${CY - ARC_R * Math.sin((Math.PI * 2) / 10)} A ${ARC_R} ${ARC_R} 0 0 1 ${CX + ARC_R} ${CY}`

interface Props {
  value: number
  className?: string
}

export function SuspicionMeter({ value, className = '' }: Props) {
  const alarmed = value >= 8
  const filled = (Math.min(Math.max(value, 0), MAX) / MAX) * 100
  return (
    <figure
      role="meter"
      aria-label="Gus's suspicion"
      aria-valuemin={0}
      aria-valuemax={MAX}
      aria-valuenow={value}
      aria-valuetext={`${value} out of ${MAX}: ${describeSuspicion(value)}`}
      className={`flex flex-col items-center transition-[--heat] duration-1000 ease-heavy ${className}`}
      style={{ '--heat': value / MAX } as CSSProperties}
    >
      <svg viewBox="0 0 240 142" className="w-full max-w-80 overflow-visible" aria-hidden="true">
        <defs>
          <linearGradient id="sm-rim" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#ffe3a1" />
            <stop offset="0.45" stopColor="#c58a24" />
            <stop offset="1" stopColor="#5a3a0b" />
          </linearGradient>
          <radialGradient id="sm-face" cx="50%" cy="85%" r="90%">
            <stop offset="0" stopColor="#1d2632" />
            <stop offset="1" stopColor="#0a0e14" />
          </radialGradient>
          <linearGradient id="sm-glass" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#fff" stopOpacity="0.14" />
            <stop offset="0.6" stopColor="#fff" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Brass rim and dark face */}
        <path
          d={`M 6 ${CY} A 114 114 0 0 1 234 ${CY} L 234 ${CY + 14} L 6 ${CY + 14} Z`}
          fill="url(#sm-rim)"
        />
        <path
          d={`M 14 ${CY} A 106 106 0 0 1 226 ${CY} L 226 ${CY + 8} L 14 ${CY + 8} Z`}
          fill="url(#sm-face)"
        />

        {/* Scale: track, danger band, live fill */}
        <path d={ARC} fill="none" stroke="#2c3846" strokeWidth="10" />
        <path
          d={DANGER}
          fill="none"
          stroke="var(--color-alarm)"
          strokeOpacity="0.35"
          strokeWidth="10"
        />
        <path
          d={ARC}
          pathLength={100}
          fill="none"
          strokeWidth="10"
          strokeDasharray={`${filled} 100`}
          className="transition-[stroke-dasharray] duration-1000 ease-heavy"
          style={{ stroke: HEAT_COLOUR, filter: `drop-shadow(0 0 5px ${HEAT_COLOUR})` }}
        />
        {Array.from({ length: MAX + 1 }, (_, tick) => (
          <g key={tick} transform={`rotate(${needleAngle(tick)} ${CX} ${CY})`}>
            <line
              x1={CX}
              y1={CY - ARC_R + 9}
              x2={CX}
              y2={CY - ARC_R + (tick % 5 === 0 ? 20 : 15)}
              stroke="#e9eef3"
              strokeOpacity={tick % 5 === 0 ? 0.9 : 0.45}
              strokeWidth={tick % 5 === 0 ? 2 : 1.2}
            />
          </g>
        ))}
        {[0, 5, 10].map((n) => {
          const angle = (needleAngle(n) * Math.PI) / 180
          return (
            <text
              key={n}
              x={CX + Math.sin(angle) * (ARC_R - 32)}
              y={CY - Math.cos(angle) * (ARC_R - 32) + (n === 5 ? 4 : -8)}
              textAnchor="middle"
              fontFamily="var(--font-stencil)"
              fontSize="13"
              fontWeight="700"
              fill="#93a0b0"
            >
              {n}
            </text>
          )
        })}

        {/* Needle on a brass pivot */}
        <g
          className="transition-transform duration-1000 ease-spring"
          style={{
            transform: `rotate(${needleAngle(value)}deg)`,
            transformOrigin: `${CX}px ${CY}px`,
          }}
        >
          <path
            d={`M ${CX - 3.5} ${CY} L ${CX} ${CY - ARC_R + 6} L ${CX + 3.5} ${CY} Z`}
            style={{ fill: HEAT_COLOUR }}
          />
        </g>
        <circle cx={CX} cy={CY} r="10" fill="url(#sm-rim)" />
        <circle cx={CX} cy={CY} r="4" fill="#0a0e14" />

        {/* Glass reflection across the face */}
        <path d={`M 14 ${CY} A 106 106 0 0 1 226 ${CY} Z`} fill="url(#sm-glass)" />
      </svg>
      <figcaption className="mt-3 text-center">
        <span className="font-stencil text-7xl leading-none font-black text-chalk tabular-nums">
          {value}
        </span>
        <span className="font-stencil text-3xl font-bold text-fog"> / {MAX}</span>
        <span
          className={`mt-1 block font-stencil text-2xl font-bold tracking-wide ${alarmed ? 'text-alarm' : 'text-gold'}`}
        >
          {describeSuspicion(value)}
        </span>
      </figcaption>
    </figure>
  )
}
