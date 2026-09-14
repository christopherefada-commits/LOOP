import { motion } from 'framer-motion'

interface LoopIconProps {
  size?: number
  resolved?: boolean
  className?: string
}

export function LoopIcon({ size = 28, resolved = false, className }: LoopIconProps) {
  const strokeWidth = size * 0.11
  const radius = (size - strokeWidth) / 2 - 1

  return (
    <motion.svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      fill="none"
      className={className}
      aria-hidden
    >
      {resolved && (
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius + 4}
          fill="url(#loopGlow)"
          initial={{ opacity: 0, scale: 0.6 }}
          animate={{ opacity: [0, 0.6, 0.3], scale: [0.6, 1.3, 1] }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      )}
      <defs>
        <linearGradient id="loopGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#1F5C45" />
          <stop offset="100%" stopColor="#34D399" />
        </linearGradient>
        <radialGradient id="loopGlow">
          <stop offset="0%" stopColor="#34D399" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#34D399" stopOpacity="0" />
        </radialGradient>
      </defs>
      <motion.circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke="url(#loopGradient)"
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        fill="none"
        initial={false}
        animate={{
          strokeDasharray: resolved ? `${2 * Math.PI * radius} 0` : `${2 * Math.PI * radius * 0.82} ${2 * Math.PI * radius * 0.18}`,
          rotate: resolved ? 0 : 0,
        }}
        transition={
          resolved
            ? { type: 'spring', stiffness: 260, damping: 14, mass: 0.8 }
            : { duration: 0 }
        }
        style={{ originX: '50%', originY: '50%' }}
      />
    </motion.svg>
  )
}
