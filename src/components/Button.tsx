import { motion } from 'framer-motion'
import type { ReactNode } from 'react'

interface ButtonProps {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'destructive' | 'ghost'
  onClick?: () => void
  disabled?: boolean
  type?: 'button' | 'submit'
  fullWidth?: boolean
}

const variants = {
  primary: {
    background: 'var(--gradient-primary)',
    color: '#fff',
    boxShadow: 'var(--shadow-button)',
    border: 'none',
  },
  secondary: {
    background: 'var(--surface)',
    color: 'var(--ink)',
    boxShadow: '0 4px 16px rgba(31, 92, 69, 0.08)',
    border: '1.5px solid var(--border)',
  },
  destructive: {
    background: 'transparent',
    color: 'var(--rust)',
    boxShadow: 'none',
    border: 'none',
  },
  ghost: {
    background: 'transparent',
    color: 'var(--muted)',
    boxShadow: 'none',
    border: 'none',
  },
}

export function Button({
  children,
  variant = 'primary',
  onClick,
  disabled,
  type = 'button',
  fullWidth,
}: ButtonProps) {
  const style = variants[variant]

  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled}
      whileHover={disabled ? undefined : { y: -2, boxShadow: variant === 'primary' ? '0 10px 28px rgba(31, 92, 69, 0.35)' : style.boxShadow }}
      whileTap={disabled ? undefined : { y: 0, scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 400, damping: 22 }}
      style={{
        ...style,
        width: fullWidth ? '100%' : undefined,
        padding: variant === 'ghost' || variant === 'destructive' ? '10px 16px' : '12px 24px',
        borderRadius: 'var(--radius-sm)',
        fontWeight: 600,
        fontSize: '0.9375rem',
        opacity: disabled ? 0.5 : 1,
        cursor: disabled ? 'not-allowed' : 'pointer',
      }}
    >
      {children}
    </motion.button>
  )
}
