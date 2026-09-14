import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { LifeEventCard } from '../components/LifeEventCard'
import { useLoop } from '../context/LoopContext'
import type { LoopCategory } from '../types'

interface DashboardProps {
  filter?: 'all' | 'money' | 'deadlines' | 'documents' | 'approvals'
}

const filterMap: Record<string, (c: LoopCategory) => boolean> = {
  all: () => true,
  money: (c) => c === 'money_recover' || c === 'money_lose',
  deadlines: (c) => c === 'deadline',
  documents: (c) => c === 'document',
  approvals: () => true,
}

export function Dashboard({ filter = 'all' }: DashboardProps) {
  const { loops, openLoopCount, dismissLoop } = useLoop()
  const navigate = useNavigate()

  const filtered = useMemo(() => {
    let list = loops.filter((l) => l.status !== 'completed' && l.status !== 'dismissed')
    if (filter !== 'all') {
      list = list.filter((l) => filterMap[filter]?.(l.category))
    }
    if (filter === 'approvals') {
      list = list.filter((l) => l.status === 'awaiting_approval')
    }
    return list
  }, [loops, filter])

  const greeting = useMemo(() => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 17) return 'Good afternoon'
    return 'Good evening'
  }, [])

  const heroCount = filter === 'all' ? openLoopCount : filtered.length

  return (
    <div>
      <motion.header
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45 }}
        style={{ marginBottom: 40 }}
      >
        <p style={{ margin: '0 0 8px', color: 'var(--muted)', fontSize: '1rem' }}>{greeting}.</p>
        <h1
          style={{
            margin: 0,
            fontSize: '2rem',
            fontWeight: 700,
            letterSpacing: '-0.03em',
            lineHeight: 1.2,
          }}
        >
          LOOP found{' '}
          <span
            style={{
              background: 'var(--gradient-primary)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            {heroCount}
          </span>{' '}
          open {heroCount === 1 ? 'loop' : 'loops'}.
        </h1>
      </motion.header>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16, maxWidth: 680 }}>
        {filtered.length === 0 ? (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ color: 'var(--muted)', fontSize: '1rem' }}
          >
            Nothing here right now — LOOP is watching your inbox quietly.
          </motion.p>
        ) : (
          filtered.map((loop, i) => (
            <LifeEventCard
              key={loop.id}
              loop={loop}
              index={i}
              onReview={(id) => navigate(`/approval/${id}`)}
              onDismiss={dismissLoop}
            />
          ))
        )}
      </div>
    </div>
  )
}
