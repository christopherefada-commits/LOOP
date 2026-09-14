import { NavLink, Outlet } from 'react-router-dom'
import {
  Activity,
  Calendar,
  FileText,
  LayoutGrid,
  Receipt,
  Settings,
  ShieldCheck,
} from 'lucide-react'
import { LoopIcon } from './LoopIcon'

const navItems = [
  { to: '/', label: 'All', icon: LayoutGrid, end: true },
  { to: '/money', label: 'Money', icon: Receipt },
  { to: '/deadlines', label: 'Deadlines', icon: Calendar },
  { to: '/documents', label: 'Documents', icon: FileText },
  { to: '/approvals', label: 'Approvals', icon: ShieldCheck },
  { to: '/activity', label: 'Activity', icon: Activity },
]

export function Layout() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <aside
        style={{
          width: 220,
          padding: '28px 16px',
          background: 'var(--surface)',
          borderRight: '1px solid var(--border)',
          display: 'flex',
          flexDirection: 'column',
          flexShrink: 0,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '0 12px', marginBottom: 32 }}>
          <LoopIcon size={32} />
          <span style={{ fontSize: '1.375rem', fontWeight: 700, letterSpacing: '-0.02em' }}>LOOP</span>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: 1 }}>
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '12px 16px',
                borderRadius: 'var(--radius-sm)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.9375rem',
                color: isActive ? 'var(--loop-green)' : 'var(--muted)',
                background: isActive ? 'var(--loop-green-tint)' : 'transparent',
                transition: 'background 0.2s, color 0.2s',
              })}
            >
              <Icon size={18} strokeWidth={2} />
              {label}
            </NavLink>
          ))}
        </nav>

        <NavLink
          to="/settings"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            padding: '12px 16px',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--muted)',
            fontSize: '0.9375rem',
            fontWeight: 500,
          }}
        >
          <Settings size={18} strokeWidth={2} />
            You
        </NavLink>
      </aside>

      <main style={{ flex: 1, padding: '40px 48px', overflow: 'auto' }}>
        <Outlet />
      </main>
    </div>
  )
}
