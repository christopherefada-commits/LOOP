import type { LoopStatus } from '../types'

const labels: Record<LoopStatus, string> = {
  detected: 'New',
  investigating: 'Looking into it',
  prepared: 'Ready to review',
  awaiting_approval: 'Needs you',
  executing: 'In progress',
  completed: 'Done',
  dismissed: 'Dismissed',
}

interface StatusPillProps {
  status: LoopStatus
}

export function StatusPill({ status }: StatusPillProps) {
  const isResolved = status === 'completed' || status === 'dismissed'

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '6px 14px',
        borderRadius: 'var(--radius-pill)',
        fontSize: '0.8125rem',
        fontWeight: 600,
        border: isResolved ? 'none' : '1.5px solid var(--loop-green)',
        color: isResolved ? 'var(--loop-green)' : 'var(--loop-green)',
        background: isResolved ? 'var(--loop-green-tint)' : 'transparent',
      }}
    >
      {labels[status]}
    </span>
  )
}
