import { useState } from 'react'
import { Button } from '../components/Button'
import { useLoop } from '../context/LoopContext'

const scenarios = [
  ['receipt', 'Simulate: Receipt Arrives'],
  ['complaint', 'Simulate: Complaint Email'],
  ['bills', 'Simulate: High Bill'],
  ['appointment', 'Simulate: Appointment Invite'],
  ['form', 'Simulate: Reimbursement Form'],
  ['renewal', 'Simulate: Renewal Notice'],
] as const

export function Settings() {
  const { isDemo, runDiscovery, simulateScenario } = useLoop()
  const [busy, setBusy] = useState<string | null>(null)

  async function run(action: string, callback: () => Promise<void>) {
    setBusy(action)
    try {
      await callback()
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
              <Button key={preset} variant="secondary" onClick={() => run(preset, () => simulateScenario(preset))} disabled={busy !== null} fullWidth>
                {busy === preset ? 'Adding scenario...' : label}
              </Button>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}