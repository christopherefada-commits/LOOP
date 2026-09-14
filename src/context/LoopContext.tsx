import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react'
import { initialLoops, initialTimeline } from '../data/mockData'
import type { LifeEvent, TimelineEntry } from '../types'

interface LoopContextValue {
  loops: LifeEvent[]
  timeline: TimelineEntry[]
  isDemo: boolean
  runDiscovery: () => Promise<void>
  simulateScenario: (preset: string) => Promise<void>
  approveLoop: (id: string) => Promise<void>
  rejectLoop: (id: string) => Promise<void>
  dismissLoop: (id: string) => void
  getLoop: (id: string) => LifeEvent | undefined
  openLoopCount: number
}

const LoopContext = createContext<LoopContextValue | null>(null)

function nowIso() {
  return new Date().toISOString()
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
}

function mapSummary(summary: Record<string, unknown>) {
  const events = (summary.open_loops as Record<string, unknown>[] | undefined) ?? []
  const timelineItems = (summary.timeline as Record<string, unknown>[] | undefined) ?? []
  return {
    loops: events.map((event) => ({
      ...event,
      amount: event.dollar_amount,
      preparedAction: event.prepared_action,
      createdAt: event.created_at,
      evidence: event.evidence ?? [],
    })) as unknown as LifeEvent[],
    timeline: timelineItems.map((item) => ({
      id: String(item.id ?? `timeline-${Date.now()}`),
      timestamp: String(item.iso_timestamp ?? item.timestamp ?? new Date().toISOString()),
      text: String(item.message ?? ''),
      loopId: item.event_id ? String(item.event_id) : undefined,
    })),
  }
}

export function LoopProvider({ children }: { children: ReactNode }) {
  const [loops, setLoops] = useState<LifeEvent[]>(initialLoops)
  const [timeline, setTimeline] = useState<TimelineEntry[]>(initialTimeline)
  const [isDemo, setIsDemo] = useState(false)

  const refreshData = useCallback(async () => {
    const response = await fetch('/api/summary')
    if (!response.ok) throw new Error('Unable to load LOOP summary')
    const summary = mapSummary(await response.json())
    setLoops(summary.loops)
    setTimeline(summary.timeline)
  }, [])

  const runDiscovery = useCallback(async () => {
    const response = await fetch('/api/run-discovery', { method: 'POST' })
    if (!response.ok) throw new Error('Unable to run LOOP discovery')
    const result = await response.json()
    if (result.summary) {
      const summary = mapSummary(result.summary)
      setLoops(summary.loops)
      setTimeline(summary.timeline)
    } else {
      await refreshData()
    }
  }, [refreshData])

  const simulateScenario = useCallback(async (preset: string) => {
    const response = await fetch(`/api/simulate/${encodeURIComponent(preset)}`, { method: 'POST' })
    if (!response.ok) throw new Error('Unable to simulate scenario')
    const result = await response.json()
    if (result.summary) {
      const summary = mapSummary(result.summary)
      setLoops(summary.loops)
      setTimeline(summary.timeline)
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    async function initialize() {
      try {
        const response = await fetch('/api/me')
        if (!response.ok) return
        const session = await response.json()
        if (cancelled || !session.user?.is_demo) return
        setIsDemo(true)
        await runDiscovery()
      } catch {
        // Keep the local demo data when the API is unavailable.
      }
    }
    initialize()
    return () => { cancelled = true }
  }, [runDiscovery])

  const addTimeline = useCallback((text: string, loopId?: string) => {
    setTimeline((prev) => [
      { id: `t-${Date.now()}`, timestamp: nowIso(), text, loopId },
      ...prev,
    ])
  }, [])

  const approveLoop = useCallback(async (id: string) => {
    const response = await fetch(`/api/approve/${encodeURIComponent(id)}`, { method: 'POST' })
    if (!response.ok) throw new Error('Unable to approve LOOP action')
    const result = await response.json()
    if (result.summary) {
      const summary = mapSummary(result.summary)
      setLoops(summary.loops)
      setTimeline(summary.timeline)
    }
  }, [])

  const rejectLoop = useCallback(
    async (id: string) => {
      const response = await fetch(`/api/reject/${encodeURIComponent(id)}`, { method: 'POST' })
      if (!response.ok) throw new Error('Unable to reject LOOP action')
      const result = await response.json()
      if (result.summary) {
        const summary = mapSummary(result.summary)
        setLoops(summary.loops)
        setTimeline(summary.timeline)
      }
    },
    [],
  )

  const dismissLoop = useCallback(
    (id: string) => {
      setLoops((prev) =>
        prev.map((l) => (l.id === id ? { ...l, status: 'dismissed' as const } : l)),
      )
      addTimeline('Dismissed this open loop.', id)
    },
    [addTimeline],
  )

  const getLoop = useCallback((id: string) => loops.find((l) => l.id === id), [loops])

  const openLoopCount = loops.filter(
    (l) => l.status !== 'completed' && l.status !== 'dismissed',
  ).length

  return (
    <LoopContext.Provider
      value={{ loops, timeline, isDemo, runDiscovery, simulateScenario, approveLoop, rejectLoop, dismissLoop, getLoop, openLoopCount }}
    >
      {children}
    </LoopContext.Provider>
  )
}

export function useLoop() {
  const ctx = useContext(LoopContext)
  if (!ctx) throw new Error('useLoop must be used within LoopProvider')
  return ctx
}

export { formatTime }
