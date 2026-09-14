import { motion } from 'framer-motion'
import { Calendar, FileText, Receipt, Shield } from 'lucide-react'
import type { LifeEvent } from '../types'
import { StatusPill } from './StatusPill'
import { Button } from './Button'

const categoryAccent: Record<string, string> = {
  money_recover: '#B8863B',
  money_lose: '#B54A2A',
  deadline: '#1F5C45',
  document: '#5B6B62',
}

const categoryIcon = {
  money_recover: Shield,
  money_lose: Receipt,
  deadline: Calendar,
  document: FileText,
}

interface LifeEventCardProps {
  loop: LifeEvent
  index: number
  onReview?: (id: string) => void
  onDismiss?: (id: string) => void
}

export function LifeEventCard({ loop, index, onReview, onDismiss }: LifeEventCardProps) {
  const Icon = categoryIcon[loop.category]
  const accent = categoryAccent[loop.category]
  const isResolved = loop.status === 'completed' || loop.status === 'dismissed'
  const needsReview = loop.status === 'awaiting_approval'

  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.4, ease: 'easeOut' }}
      style={{
        background: 'var(--surface)',
        borderRadius: 'var(--radius)',
        border: '1px solid var(--border)',
        boxShadow: 'var(--shadow-soft)',
        overflow: 'hidden',
        borderLeft: `4px solid ${isResolved ? 'var(--loop-green)' : accent}`,
      }}
    >
      <div style={{ padding: '20px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, marginBottom: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: 12,
                background: 'var(--loop-green-tint)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--loop-green)',
              }}
            >
              <Icon size={18} strokeWidth={2} />
            </div>
            <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>{loop.title}</h3>
          </div>
          <StatusPill status={loop.status} />
        </div>

        <p style={{ margin: '0 0 16px', color: 'var(--muted)', fontSize: '0.9375rem', lineHeight: 1.55 }}>
          {loop.summary}
        </p>

        {loop.amount != null && (
          <p style={{ margin: '0 0 16px', fontSize: '1.125rem', fontWeight: 700, color: 'var(--amber)' }}>
            ${loop.amount.toLocaleString()}
            {loop.amountLabel && (
              <span style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--muted)', marginLeft: 8 }}>
                {loop.amountLabel}
              </span>
            )}
          </p>
        )}

        {loop.evidence[0] && (
          <p
            style={{
              margin: '0 0 16px',
              fontSize: '0.8125rem',
              color: 'var(--muted)',
              fontFamily: 'Consolas, "SF Mono", monospace',
            }}
          >
            {loop.evidence[0]}
          </p>
        )}

        {!isResolved && (
          <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
            {needsReview && onReview && (
              <Button variant="primary" onClick={() => onReview(loop.id)}>
                Review
              </Button>
            )}
            {!needsReview && loop.status === 'prepared' && onReview && (
              <Button variant="secondary" onClick={() => onReview(loop.id)}>
                View details
              </Button>
            )}
            {onDismiss && (
              <Button variant="ghost" onClick={() => onDismiss(loop.id)}>
                Dismiss
              </Button>
            )}
          </div>
        )}
      </div>
    </motion.article>
  )
}
