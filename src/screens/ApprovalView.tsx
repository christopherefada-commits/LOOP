import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft } from 'lucide-react'
import { Button } from '../components/Button'
import { LoopIcon } from '../components/LoopIcon'
import { StatusPill } from '../components/StatusPill'
import { formatTime, useLoop } from '../context/LoopContext'

export function ApprovalView() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { getLoop, approveLoop, rejectLoop } = useLoop()
  const loop = id ? getLoop(id) : undefined
  const [resolved, setResolved] = useState(false)
  const [action, setAction] = useState<'approved' | 'rejected' | null>(null)

  if (!loop) {
    return (
      <div>
        <p>Open loop not found.</p>
        <Button variant="secondary" onClick={() => navigate('/')}>
          Back to dashboard
        </Button>
      </div>
    )
  }

  const handleApprove = () => {
    setResolved(true)
    setAction('approved')
    setTimeout(() => {
      approveLoop(loop.id)
      navigate('/activity')
    }, 1200)
  }

  const handleReject = () => {
    rejectLoop(loop.id)
    navigate('/')
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      style={{ maxWidth: 640 }}
    >
      <button
        onClick={() => navigate(-1)}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          background: 'none',
          border: 'none',
          color: 'var(--muted)',
          fontSize: '0.9375rem',
          fontWeight: 500,
          padding: '8px 0',
          marginBottom: 24,
          cursor: 'pointer',
        }}
      >
        <ArrowLeft size={18} />
        Back
      </button>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 32 }}>
        <AnimatePresence mode="wait">
          <motion.div key={resolved ? 'closed' : 'open'}>
            <LoopIcon size={48} resolved={resolved} />
          </motion.div>
        </AnimatePresence>
        <div>
          <h1 style={{ margin: '0 0 6px', fontSize: '1.5rem', fontWeight: 700 }}>{loop.title}</h1>
          <StatusPill status={resolved && action === 'approved' ? 'completed' : loop.status} />
        </div>
      </div>

      <section
        style={{
          background: 'var(--surface)',
          borderRadius: 'var(--radius)',
          border: '1px solid var(--border)',
          boxShadow: 'var(--shadow-soft)',
          padding: '24px 28px',
          marginBottom: 20,
        }}
      >
        <h2 style={{ margin: '0 0 16px', fontSize: '0.875rem', fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          Evidence
        </h2>
        <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 10 }}>
          {loop.evidence.map((line) => (
            <li
              key={line}
              style={{
                fontFamily: 'Consolas, "SF Mono", monospace',
                fontSize: '0.8125rem',
                color: 'var(--muted)',
                padding: '10px 14px',
                background: 'var(--bg)',
                borderRadius: 'var(--radius-sm)',
              }}
            >
              {line}
            </li>
          ))}
        </ul>
      </section>

      {loop.preparedAction && (
        <section
          style={{
            background: 'var(--surface)',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border)',
            boxShadow: 'var(--shadow-soft)',
            padding: '24px 28px',
            marginBottom: 28,
          }}
        >
          <h2 style={{ margin: '0 0 16px', fontSize: '0.875rem', fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Prepared action
          </h2>
          <pre
            style={{
              margin: 0,
              whiteSpace: 'pre-wrap',
              fontFamily: 'var(--font)',
              fontSize: '0.9375rem',
              lineHeight: 1.65,
              color: 'var(--ink)',
            }}
          >
            {loop.preparedAction}
          </pre>
        </section>
      )}

      {!resolved && loop.status === 'awaiting_approval' && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}
        >
          <Button variant="primary" onClick={handleApprove}>
            Approve claim
          </Button>
          <Button variant="secondary" onClick={() => {}}>
            Edit
          </Button>
          <Button variant="destructive" onClick={handleReject}>
            Reject
          </Button>
        </motion.div>
      )}

      {resolved && action === 'approved' && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          style={{ color: 'var(--loop-green)', fontWeight: 600 }}
        >
          Submitted at {formatTime(new Date().toISOString())}
        </motion.p>
      )}
    </motion.div>
  )
}
