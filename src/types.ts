export type LoopStatus =
  | 'detected'
  | 'investigating'
  | 'prepared'
  | 'awaiting_approval'
  | 'executing'
  | 'completed'
  | 'dismissed'

export type LoopCategory = 'money_recover' | 'money_lose' | 'deadline' | 'document'

export interface LifeEvent {
  id: string
  type: 'warranty' | 'bill'
  category: LoopCategory
  title: string
  summary: string
  amount?: number
  amountLabel?: string
  status: LoopStatus
  evidence: string[]
  preparedAction?: string
  createdAt: string
}

export interface TimelineEntry {
  id: string
  timestamp: string
  text: string
  loopId?: string
}

export type NavFilter = 'all' | 'money' | 'deadlines' | 'documents' | 'approvals' | 'activity'
