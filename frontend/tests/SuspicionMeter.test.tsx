import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { SuspicionMeter } from '../src/components/SuspicionMeter'
import { needleAngle } from '../src/components/suspicion'

describe('SuspicionMeter', () => {
  it('reports its value to assistive technology', () => {
    render(<SuspicionMeter value={4} />)

    const meter = screen.getByRole('meter', { name: "Gus's suspicion" })
    expect(meter).toHaveAttribute('aria-valuenow', '4')
    expect(meter).toHaveAttribute('aria-valuetext', '4 out of 10: Curious')
  })

  it('says when Gus is calling security', () => {
    render(<SuspicionMeter value={10} />)

    expect(screen.getByText('Calling security')).toBeInTheDocument()
  })

  it('sweeps the needle from far left to far right, and no further', () => {
    expect(needleAngle(0)).toBe(-90)
    expect(needleAngle(5)).toBe(0)
    expect(needleAngle(10)).toBe(90)
    expect(needleAngle(12)).toBe(90)
  })
})
