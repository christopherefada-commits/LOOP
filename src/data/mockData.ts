import type { LifeEvent, TimelineEntry } from '../types'

export const initialLoops: LifeEvent[] = [
  {
    id: 'warranty-1',
    type: 'warranty',
    category: 'money_recover',
    title: 'Sony WH-1000XM5 headphones',
    summary:
      'Your headphones may qualify for a warranty claim — LOOP linked a complaint email to your March receipt.',
    amount: 349,
    amountLabel: 'potential recovery',
    status: 'awaiting_approval',
    evidence: [
      'receipt_392.pdf — Sony WH-1000XM5, purchased 2026-03-14, $349.00',
      'email_complaint.txt — "my headphones keep shutting down" (2026-09-08)',
      'policy_sony_warranty.txt — 12-month defect warranty, receipt required',
    ],
    preparedAction: `Subject: Warranty claim — Sony WH-1000XM5 (Order #392)

Dear Sony Support,

I purchased Sony WH-1000XM5 headphones on March 14, 2026 (receipt attached). The headphones repeatedly shut down during use despite being fully charged. I believe this may qualify under your 12-month defect warranty.

Please advise on next steps for repair or replacement.

Attached: receipt_392.pdf`,
    createdAt: '2026-09-11T18:30:00',
  },
  {
    id: 'bill-1',
    type: 'bill',
    category: 'money_lose',
    title: 'Electricity bill — September',
    summary:
      'LOOP found a possible issue — your electricity bill is 27% higher than your recent average.',
    amount: 40,
    amountLabel: 'above average',
    status: 'prepared',
    evidence: [
      'bill_sep_2026.pdf — $187.00 due 2026-09-20',
      'Historical average (Apr–Aug 2026): $147.00/month',
      'Rate change notice in bill: new peak-hour tariff effective August 1',
    ],
    createdAt: '2026-09-11T17:15:00',
  },
  {
    id: 'delivery-1',
    type: 'bill',
    category: 'document',
    title: 'Package delivery confirmation',
    summary: 'New delivery confirmation from Amazon — no action needed right now.',
    status: 'detected',
    evidence: ['email_delivery.txt — Package arriving Sep 13'],
    createdAt: '2026-09-11T16:00:00',
  },
]

export const initialTimeline: TimelineEntry[] = [
  {
    id: 't1',
    timestamp: '2026-09-11T18:44:00',
    text: 'Linked the complaint email to your headphones receipt.',
    loopId: 'warranty-1',
  },
  {
    id: 't2',
    timestamp: '2026-09-11T18:42:00',
    text: 'Looked up Sony warranty policy — 12-month defect coverage may apply.',
    loopId: 'warranty-1',
  },
  {
    id: 't3',
    timestamp: '2026-09-11T18:40:00',
    text: 'Drafted a warranty claim for your review.',
    loopId: 'warranty-1',
  },
  {
    id: 't4',
    timestamp: '2026-09-11T17:20:00',
    text: 'Compared your September electricity bill to the last five months.',
    loopId: 'bill-1',
  },
  {
    id: 't5',
    timestamp: '2026-09-11T17:18:00',
    text: 'Found a possible issue — bill is 27% above your average.',
    loopId: 'bill-1',
  },
  {
    id: 't6',
    timestamp: '2026-09-11T16:02:00',
    text: 'New delivery confirmation detected.',
    loopId: 'delivery-1',
  },
  {
    id: 't7',
    timestamp: '2026-09-11T15:30:00',
    text: 'Scanned 12 documents and emails from your demo inbox.',
  },
]
