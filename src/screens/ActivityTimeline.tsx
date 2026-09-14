import { motion } from 'framer-motion'
import { LoopIcon } from '../components/LoopIcon'
import { formatTime, useLoop } from '../context/LoopContext'

export function ActivityTimeline() {
  const { timeline, loops } = useLoop()

  return (
    <div style={{ maxWidth: 640 }}>
      <motion.header
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ marginBottom: 36 }}
      >
        <h1 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 700, letterSpacing: '-0.02em' }}>
          Activity
        </h1>
        <p style={{ margin: '8px 0 0', color: 'var(--muted)', fontSize: '0.9375rem' }}>
          Everything LOOP has done, in order.
        </p>
      </motion.header>

      <ol style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 0 }}>
        {timeline.map((entry, i) => {
          const linkedLoop = entry.loopId ? loops.find((l) => l.id === entry.loopId) : undefined
          const isCompleted = linkedLoop?.status === 'completed'

          return (
            <motion.li
              key={entry.id}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05, duration: 0.35 }}
              style={{
                display: 'flex',
                gap: 16,
                padding: '18px 0',
                borderBottom: i < timeline.length - 1 ? '1px solid var(--border)' : 'none',
              }}
            >
              <div style={{ paddingTop: 2, flexShrink: 0 }}>
                {isCompleted ? (
                  <LoopIcon size={22} resolved />
                ) : (
                  <div
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: '50%',
                      background: 'var(--loop-green)',
                      marginTop: 6,
                      marginLeft: 6,
                      opacity: 0.5,
                    }}
                  />
                )}
              </div>
              <div>
                <time
                  style={{
                    display: 'block',
                    fontSize: '0.8125rem',
                    color: 'var(--muted)',
                    fontFamily: 'Consolas, "SF Mono", monospace',
                    marginBottom: 4,
                  }}
                >
                  {formatTime(entry.timestamp)}
                </time>
                <p style={{ margin: 0, fontSize: '0.9375rem', lineHeight: 1.5 }}>{entry.text}</p>
              </div>
            </motion.li>
          )
        })}
      </ol>
    </div>
  )
}
