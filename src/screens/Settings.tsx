import { useState } from 'react'
import { Button } from '../components/Button'
import { useLoop } from '../context/LoopContext'

const scenarios = [
  ['receipt', 'Add simulation: Receipt Arrives'],
  ['complaint', 'Add simulation: Complaint Email'],
  ['bills', 'Add simulation: High Bill'],
  ['appointment', 'Add simulation: Appointment Invite'],
  ['form', 'Add simulation: Reimbursement Form'],
  ['renewal', 'Add simulation: Renewal Notice'],
] as const

export function Settings() {
  const { isDemo, runDiscovery, simulateScenario } = useLoop()
  const [busy, setBusy] = useState<string | null>(null)
  const [confirmed, setConfirmed] = useState<string | null>(null)

  async function run(action: string, callback: () => Promise<void>, showConfirmation = false) {
    setBusy(action)
    try {
      await callback()
      if (showConfirmation) {
        setConfirmed(action)
        window.setTimeout(() => setConfirmed((current) => current === action ? null : current), 1500)
      }
    } finally {
      setBusy(null)
    }
  }

  return (
    <div style={{ maxWidth: 680 }}>
      <h1 style={{ margin: '0 0 32px', fontSize: '2rem' }}>You</h1>
      {isDemo && (
        <section aria-labelledby="demo-scenarios-title">
          <div style={{ marginBottom: 16 }}>
            <h2 id="demo-scenarios-title" style={{ margin: 0, fontSize: '1.25rem' }}>Demo scenarios</h2>
            <p style={{ margin: '4px 0 0', color: 'var(--muted)' }}>Sandbox controls for the LOOP walkthrough.</p>
          </div>
          <div style={{ display: 'grid', gap: 10 }}>
            <Button variant="secondary" onClick={() => run('discovery', runDiscovery)} disabled={busy !== null} fullWidth>
              {busy === 'discovery' ? 'Running discovery...' : 'Run LOOP Discovery'}
            </Button>
            {scenarios.map(([preset, label]) => (
              <Button key={preset} variant="secondary" onClick={() => run(preset, () => simulateScenario(preset), true)} disabled={busy !== null} fullWidth>
                {busy === preset ? 'Adding scenario...' : confirmed === preset ? 'Added ✓' : label}
              </Button>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}