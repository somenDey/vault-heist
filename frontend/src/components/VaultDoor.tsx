// The vault door: the game's signature picture. Its dial spins once on arrival,
// and when the player wins the door swings open on its hinges to show the lit vault.

const RIM_BOLTS = 24
const DIAL_TICKS = 50

interface Props {
  /** Swing the door open. */
  open?: boolean
  className?: string
}

export function VaultDoor({ open = false, className = '' }: Props) {
  return (
    <div className={`relative aspect-square ${className}`} aria-hidden="true">
      <Frame />

      {/* The door itself: brushed steel underneath, hardware drawn on top. It swings as one. */}
      <div
        className="absolute inset-0 drop-shadow-[0_40px_50px_rgb(0_0_0/0.65)]"
        style={
          open
            ? {
                transformOrigin: '4% 50%',
                animation: 'swing-open 1.8s var(--ease-heavy) 0.3s both',
              }
            : undefined
        }
      >
        <div className="brushed absolute inset-[7%] rounded-full" />
        <svg viewBox="0 0 400 400" className="absolute inset-0 size-full overflow-visible">
          <DoorDefs />

          {/* Bevelled edge, lit from the top left */}
          <circle cx="200" cy="200" r="172" fill="none" stroke="url(#vd-bevel)" strokeWidth="6" />
          <circle cx="200" cy="200" r="168.5" fill="none" stroke="#06080c" strokeWidth="1.5" />

          {/* Locking bolts around the rim */}
          {Array.from({ length: RIM_BOLTS }, (_, bolt) => (
            <g key={bolt} transform={`rotate(${(360 / RIM_BOLTS) * bolt} 200 200)`}>
              <circle cx="200" cy="44" r="6.5" fill="#06080c" opacity="0.6" />
              <circle cx="200" cy="43" r="5.5" fill="url(#vd-bolt)" />
            </g>
          ))}

          {/* Engraved rings and the bank's name */}
          <circle cx="200" cy="200" r="146" fill="none" stroke="#06080c" strokeOpacity="0.7" />
          <circle cx="200" cy="200" r="147" fill="none" stroke="#fff" strokeOpacity="0.06" />
          <path id="vd-name-arc" d="M 67 200 A 133 133 0 0 1 333 200" fill="none" />
          <text
            fontFamily="var(--font-stencil)"
            fontSize="11"
            fontWeight="800"
            letterSpacing="4"
            fill="#c9d2dc"
            fillOpacity="0.45"
          >
            <textPath href="#vd-name-arc" startOffset="50%" textAnchor="middle">
              GRANITE &amp; SONS SAVINGS
            </textPath>
          </text>

          <Wheel />
          <Dial />
        </svg>
      </div>
    </div>
  )
}

/** The steel frame set into the wall, and the lit vault behind the door. */
function Frame() {
  return (
    <svg viewBox="0 0 400 400" className="absolute inset-0 size-full overflow-visible">
      <defs>
        <radialGradient id="vd-inside" cx="50%" cy="38%" r="65%">
          <stop offset="0" stopColor="#ffe7a8" />
          <stop offset="0.35" stopColor="#f5b83d" />
          <stop offset="0.75" stopColor="#7a4d0f" />
          <stop offset="1" stopColor="#1d1406" />
        </radialGradient>
        <linearGradient id="vd-frame" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#4b5a6c" />
          <stop offset="0.45" stopColor="#1d2632" />
          <stop offset="1" stopColor="#090c11" />
        </linearGradient>
        <linearGradient id="vd-bar" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#fff1c4" />
          <stop offset="0.5" stopColor="#f5b83d" />
          <stop offset="1" stopColor="#8f5e12" />
        </linearGradient>
      </defs>

      <circle cx="200" cy="200" r="196" fill="url(#vd-frame)" />
      <circle cx="200" cy="200" r="182" fill="#05070a" />

      {/* Inside the vault: gold light and stacked bars */}
      <circle cx="200" cy="200" r="176" fill="url(#vd-inside)" />
      {[
        [150, 262],
        [200, 262],
        [250, 262],
        [175, 238],
        [225, 238],
        [200, 214],
      ].map(([x, y]) => (
        <g key={`${x}-${y}`}>
          <path
            d={`M ${x - 22} ${y + 20} L ${x - 16} ${y} L ${x + 16} ${y} L ${x + 22} ${y + 20} Z`}
            fill="url(#vd-bar)"
          />
          <path
            d={`M ${x - 22} ${y + 20} L ${x + 22} ${y + 20}`}
            stroke="#6b450c"
            strokeWidth="2"
          />
        </g>
      ))}

      {/* Hinges on the left */}
      {[118, 252].map((y) => (
        <g key={y}>
          <rect x="-8" y={y} width="34" height="30" rx="6" fill="url(#vd-frame)" />
          <rect x="-8" y={y + 6} width="34" height="3" fill="#fff" fillOpacity="0.12" />
        </g>
      ))}
    </svg>
  )
}

function DoorDefs() {
  return (
    <defs>
      <linearGradient id="vd-bevel" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor="#8ea0b4" />
        <stop offset="0.4" stopColor="#334152" />
        <stop offset="1" stopColor="#090c11" />
      </linearGradient>
      <radialGradient id="vd-bolt" cx="35%" cy="30%" r="75%">
        <stop offset="0" stopColor="#dfe6ee" />
        <stop offset="0.45" stopColor="#7c8a9b" />
        <stop offset="1" stopColor="#2a3442" />
      </radialGradient>
      {/* Polished gold, shaded across its width so each spoke reads as round */}
      <linearGradient id="vd-spoke" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stopColor="#6e470d" />
        <stop offset="0.35" stopColor="#ffe3a1" />
        <stop offset="0.6" stopColor="#f5b83d" />
        <stop offset="1" stopColor="#7a4f10" />
      </linearGradient>
      <radialGradient id="vd-knob" cx="35%" cy="30%" r="80%">
        <stop offset="0" stopColor="#fff4cf" />
        <stop offset="0.4" stopColor="#f5b83d" />
        <stop offset="1" stopColor="#7a4f10" />
      </radialGradient>
      <radialGradient id="vd-dial" cx="40%" cy="30%" r="85%">
        <stop offset="0" stopColor="#2b3542" />
        <stop offset="1" stopColor="#0b0f15" />
      </radialGradient>
    </defs>
  )
}

/** The three-bar handle that draws the bolts back. */
function Wheel() {
  return (
    <g>
      {[30, 90, 150].map((angle) => (
        <g key={angle} transform={`rotate(${angle} 200 200)`}>
          <rect
            x="193"
            y="88"
            width="14"
            height="224"
            rx="7"
            fill="#06080c"
            opacity="0.45"
            transform="translate(3 5)"
          />
          <rect x="193" y="88" width="14" height="224" rx="7" fill="url(#vd-spoke)" />
          {[86, 314].map((cy) => (
            <circle key={cy} cx="200" cy={cy} r="15" fill="url(#vd-knob)" />
          ))}
        </g>
      ))}
    </g>
  )
}

/** The combination dial at the centre. It spins once when the page loads. */
function Dial() {
  return (
    <g>
      <circle cx="200" cy="200" r="62" fill="url(#vd-knob)" />
      <circle cx="200" cy="200" r="54" fill="url(#vd-dial)" />
      <g
        style={{ transformOrigin: '200px 200px' }}
        className="animate-spin-once motion-reduce:animate-none"
      >
        {Array.from({ length: DIAL_TICKS }, (_, tick) => (
          <line
            key={tick}
            x1="200"
            y1="148"
            x2="200"
            y2={tick % 5 === 0 ? 158 : 153}
            stroke="#e9eef3"
            strokeOpacity={tick % 5 === 0 ? 0.9 : 0.45}
            strokeWidth={tick % 5 === 0 ? 1.8 : 1}
            transform={`rotate(${(360 / DIAL_TICKS) * tick} 200 200)`}
          />
        ))}
        {Array.from({ length: 10 }, (_, n) => (
          <text
            key={n}
            x="200"
            y="171"
            textAnchor="middle"
            fontFamily="var(--font-stencil)"
            fontSize="11"
            fontWeight="700"
            fill="#e9eef3"
            fillOpacity="0.8"
            transform={`rotate(${n * 36} 200 200)`}
          >
            {n * 10}
          </text>
        ))}
        <circle cx="200" cy="200" r="20" fill="url(#vd-knob)" />
        <circle cx="200" cy="200" r="20" fill="none" stroke="#6e470d" strokeWidth="1.5" />
      </g>
      {/* The index mark the dial is read against */}
      <path d="M 194 136 L 206 136 L 200 146 Z" fill="var(--color-gold)" />
    </g>
  )
}
