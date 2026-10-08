// The start screen: what the game is, and the three vaults.

import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { ApiError, type Api } from '../api/client'
import type { LevelSummary } from '../api/types'
import { LevelCard } from '../components/LevelCard'
import { VaultDoor } from '../components/VaultDoor'

const REPO_URL = 'https://github.com/somenDey/vault-heist'

export function LevelSelect({ api }: { api: Pick<Api, 'listLevels'> }) {
  const [levels, setLevels] = useState<LevelSummary[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .listLevels()
      .then(setLevels)
      .catch((err: unknown) =>
        setError(err instanceof ApiError ? err.message : 'Could not load the levels.'),
      )
  }, [api])

  // The call to action points at the first level the player hasn't cracked yet.
  const next = levels?.find((level) => !level.cleared) ?? levels?.[0]
  const started = levels?.some((level) => level.cleared) ?? false

  return (
    <div className="overflow-x-clip">
      <div className="roomlight" />
      <main className="mx-auto max-w-6xl px-5 sm:px-8">
        <section className="relative grid items-center gap-8 pt-10 pb-16 sm:pt-16 lg:min-h-[88dvh] lg:grid-cols-[1fr_1.1fr] lg:gap-4 lg:pb-20">
          <div className="relative z-10">
            <h1
              translate="no"
              className="animate-rise font-stencil text-[clamp(5.5rem,16vw,11.5rem)] leading-[0.78] font-black tracking-tight text-gold [text-shadow:0_2px_0_var(--color-gold-deep),0_18px_60px_rgb(245_184_61/0.25)]"
            >
              Vault
              <br />
              Heist
            </h1>
            <p className="mt-8 max-w-[30ch] animate-rise text-xl text-pretty text-chalk/90 [animation-delay:150ms] sm:text-2xl">
              Gus guards the vault at Granite &amp; Sons Savings, and he knows the code. Talk him
              out of it before he calls security.
            </p>
            {next && (
              <div className="mt-10 flex animate-rise flex-wrap items-center gap-x-6 gap-y-3 [animation-delay:300ms]">
                <Link to={`/levels/${next.id}`} className="btn-gold px-8 py-4 text-lg">
                  {started ? `Continue with level ${next.id}` : 'Start level 1'}
                </Link>
                <a
                  href="#vaults"
                  className="text-fog underline decoration-rivet underline-offset-[6px] transition hover:text-chalk hover:decoration-fog"
                >
                  See all three vaults
                </a>
              </div>
            )}
          </div>

          {/* The door, under a lamp. The pool of light is drawn behind it. */}
          <div className="relative mx-auto w-full max-w-[19rem] sm:max-w-md lg:max-w-none lg:translate-x-10">
            <div className="absolute -inset-[18%] -z-10 rounded-full bg-[radial-gradient(closest-side,rgb(245_184_61/0.22),transparent)]" />
            <VaultDoor />
          </div>
        </section>

        <section id="vaults" aria-labelledby="vaults-title" className="scroll-mt-8 pb-24">
          <h2 id="vaults-title" className="font-stencil text-5xl font-black text-chalk sm:text-6xl">
            Three vaults
          </h2>
          <p className="mt-3 max-w-[56ch] text-lg text-fog">
            Each one guards the code a little better. Play them in any order.
          </p>
          {error && (
            <p role="alert" className="mt-6 text-alarm">
              {error}
            </p>
          )}
          {!levels && !error && (
            <div className="mt-10 grid gap-5 md:grid-cols-3" aria-label="Loading levels">
              {[0, 1, 2].map((box) => (
                <div key={box} className="h-80 animate-pulse rounded-[1.25rem] bg-vault" />
              ))}
            </div>
          )}
          {levels && (
            <ol className="mt-10 grid gap-5 md:grid-cols-3">
              {levels.map((level) => (
                <LevelCard key={level.id} level={level} />
              ))}
            </ol>
          )}
        </section>

        <footer className="border-t border-rivet/60 py-8 text-sm text-fog">
          A portfolio project about prompt injection.{' '}
          <a href={REPO_URL} className="text-chalk underline underline-offset-4 hover:text-gold">
            Source on GitHub
          </a>
        </footer>
      </main>
    </div>
  )
}
