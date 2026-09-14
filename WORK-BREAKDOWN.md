# LOOP — Team Work Separation & Technical Architecture

**Hackathon**: Agents for Humans Hackathon (Devpost / AWS)  
**Track**: Everyday Agents  
**Target Deadline**: September 14, 2026, 5:00 PM PDT (September 15, 2026, 12:00 AM UTC)  
**License**: MIT License  

---

## 1. Executive Overview

### The One-Line Pitch
> **LOOP** is an autonomous life-admin agent that discovers unfinished business hiding in a person's everyday information — receipts, bills, complaint emails, invites — and turns it into completed actions, not another reminder.

### Core Philosophy
**"Autonomous by default, human when it matters."**
* **Low-risk tasks run automatically**: Reading documents, extracting information, creating Life Events, evaluating policies, comparing bills, preparing drafts.
* **High-impact tasks pause for human approval**: Submitting claims, paying bills, confirming appointments, cancelling subscriptions.

### The Citable Benchmark
According to a 2024 *Public Administration Review* study (Martin, 2,243 UK adults surveyed), individuals lose between **32 and 85 minutes per day** to administrative life chores across 10 domains (bills, health, benefits, debt, etc.). LOOP directly addresses this time sink.

---

## 2. Major Separation of Work (2-Person Split)

To build at maximum velocity without blocking each other, Developer 1 and Developer 2 work against a **shared contract** (the Life Event Schema and Storage API).

```
┌────────────────────────────────────────────────────────────────────────┐
│                            SHARED CONTRACT                             │
│       • Life Event Schema (models.py)                                  │
│       • Storage Interface (store/base.py)                              │
│       • Ingestion File Protocol (/workspace/inbox/)                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
      ┌───────────────────────┐           ┌───────────────────────┐
      │      DEVELOPER 1      │           │      DEVELOPER 2      │
      │  Agent Engine & Cloud │           │  UI, Design & Data    │
      ├───────────────────────┤           ├───────────────────────┤
      │ • Strands Agent Loop  │           │ • Paper-tone Web UI   │
      │ • 6 Tools Logic       │           │ • UI Design Rules     │
      │ • HITL Checkpoints    │           │ • File Watcher        │
      │ • Dual Store (JSON/DB)│           │ • Synthetic Dataset   │
      │ • Bedrock & AgentCore │           │ • Arc Logo Animation  │
      └───────────────────────┘           └───────────────────────┘
```

### Developer 1: Agent Engine & Cloud Architecture (Backend / AI)
* **Strands Orchestration (`agent.py`)**:
  * Implements the 6-stage reasoning loop: `DETECT -> UNDERSTAND -> RESEARCH -> PREPARE -> ASK -> EXECUTE`.
  * Integrates `strands-agents` with Amazon Bedrock (`Claude 3.5 Sonnet` / `Claude 3 Haiku` in `us-east-1`).
  * Implements native Human-in-the-Loop (`HumanInTheLoop` / intervention hooks) for `request_approval`.
* **Core Agent Tools (`tools/`)**:
  * `get_documents`: Ingests and parses documents from the inbox.
  * `lookup_policy`: Retrieves warranty return windows and meeting scheduling rules.
  * `compare_bill`: Compares new bills against historical averages and detects anomalies.
  * `draft_action`: Generates formatted claim submissions, letters, or pre-filled form payloads.
  * `request_approval`: Pauses the agent execution pending user review.
  * `execute_action`: Commits approved actions to the Life Events store.
* **Storage & Memory Layer (`store/`)**:
  * Implement the `LifeEventsStore` abstraction.
  * `LocalJsonStore`: Zero-dependency file persistence (`data/life_events.json`) for immediate local execution without waiting for AWS credentials.
  * `DynamoDBStore`: `boto3`-backed implementation for cloud deployment.
  * Memory/Trigger Registry: Manages timestamped triggers (e.g. `event_date - 1 day`).
* **Cloud & AgentCore**:
  * AWS IAM and Bedrock client initialization (`boto3`).
  * Bedrock AgentCore configuration and packaging (`@aws/agentcore` / container runtime) for hackathon scoring bonus.

### Developer 2: Product UI, Design Rules & Synthetic Data (Frontend / UX)
* **Web UI Implementation (`ui/` / `app.py`)**:
  * Implements the visual system defined in `LOOP-UI-Design-Rules.pdf`.
  * Color tokens: Background `#F3F5F1`, Surface `#FFFFFF`, Ink `#1B2420`, Muted `#5B6B62`, Border `#E1E4DC` (1px, **no drop shadows**), Loop Green `#1F5C45`, Amber `#B8863B` (all money figures), Rust `#B54A2A` (needs you).
  * Typography: Serif (`Georgia`) for hero statement and card titles; Sans-serif (`Inter` / system-ui) for body/buttons; Monospace (`Consolas`) for citations.
  * 3 Views:
    1. **Dashboard**: Left persistent nav + main pane with hero counter (*"LOOP found N open loops"*) and cards with colored left borders.
    2. **Approval View**: Monospace fact citations, full draft claim text, and ordered action buttons: `Approve claim` (primary green) / `Edit` (secondary quiet) / `Reject` (rust text).
    3. **Activity Timeline**: Human-narrated timestamps (*"Linked this to your headphones receipt"*).
  * **Brand Motif**: The open-arc green logo mark that smoothly animates closed when an item is resolved.
* **Workspace File Watcher & Ingestion (`watcher.py`)**:
  * Watches `/workspace/inbox/` (or synthetic folder) for new file arrivals.
  * Provides a UI **"Simulate File Arrival"** panel for deterministic, zero-fail demo video recordings.
* **Synthetic Demo Dataset (`demo_data/`)**:
  * Realistic mock documents:
    1. Electronics receipt (`receipt_sony_wh1000.txt` or `.json`).
    2. Complaint email (*"Headphones keep shutting down"*).
    3. Sony warranty policy document.
    4. 5 electricity bills ($147 avg) + 1 spiked bill ($187).
    5. Meeting invitation / calendar event (*"Strategy Review on Oct 12"*).
    6. Prepared form template (*"Medical Reimbursement Claim"*).
* **Demo Video & Pitch Production**:
  * Prepares slides and records the <5 min walkthrough following the Section 12 demo script.

---

## 3. The Shared Contract

### Data Models (`models.py`)
```python
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class LifeEvent(BaseModel):
    id: str
    type: str                     # "warranty", "bill", "appointment", "submission", "subscription"
    title: str                    # e.g., "Sony WH-1000XM5 Warranty Claim"
    summary: str                  # Plain-language explanation for dashboard card
    status: str                   # "detected" -> "investigating" -> "prepared" -> "awaiting_approval" -> "executing" -> "completed"
    category: str                 # "money_recover", "money_lose", "deadline", "submission"
    dollar_amount: Optional[float] = None  # Always styled in Amber (#B8863B)
    due_or_event_date: Optional[str] = None
    trigger_date: Optional[str] = None     # e.g., "2026-10-11T09:00:00" (1 day before)
    evidence: List[str] = Field(default_factory=list) # Monospace citations (files, dates, amounts)
    prepared_action: Optional[str] = None  # Full drafted text/letter/form
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class TimelineEntry(BaseModel):
    id: str
    timestamp: str
    event_id: str
    message: str                  # Conversational voice: "Linked this to your headphones receipt"
```

### Storage Interface (`store/base.py`)
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from models import LifeEvent, TimelineEntry

class BaseLifeEventsStore(ABC):
    @abstractmethod
    def get_all_events(self) -> List[LifeEvent]:
        pass

    @abstractmethod
    def get_event(self, event_id: str) -> Optional[LifeEvent]:
        pass

    @abstractmethod
    def save_event(self, event: LifeEvent) -> None:
        pass

    @abstractmethod
    def update_status(self, event_id: str, new_status: str) -> None:
        pass

    @abstractmethod
    def get_timeline(self) -> List[TimelineEntry]:
        pass

    @abstractmethod
    def add_timeline_entry(self, entry: TimelineEntry) -> None:
        pass
```

---

## 4. Feature Specifications & Scenarios

### Feature 1: Warranty Claim (*"Money you're entitled to recover"*) — Flagship MVP
1. **Detect**: Ingests receipt for Sony Headphones ($179, purchased March 14, 2026, 1-year warranty).
2. **Understand**: Creates `warranty` Life Event (`status: active`).
3. **Detect (Later)**: Ingests user email: *"My headphones keep shutting down."*
4. **Understand**: Links email to existing warranty Life Event (`status: investigating`).
5. **Research**: Consults `lookup_policy` for return window & claim procedure.
6. **Prepare**: Prepares formal claim letter with proof of purchase (`status: awaiting_approval`).
7. **Ask**: Surfaces approval view: *"Warranty claim ready — submit?"*
8. **Execute**: On approval, marks submitted (`status: completed`), closes arc logo, logs timeline.

### Feature 2: Bill Anomaly (*"Money you're about to lose"*) — Second MVP Case
1. **Detect**: Ingests new electricity bill ($187).
2. **Understand / Research**: Compares against 5-month historical average ($147).
3. **Analyze**: Flags +27% spike exceeding the 15–20% anomaly threshold.
4. **Prepare**: Prepares clear explanation (rate increase detected in provider terms).
5. **Surface**: Surfaces card on dashboard (stops before execution to prove model breadth).

### Feature 3: Appointment / Meeting Trigger (*"Deadlines you're about to miss"*) — Extension 1
1. **Detect**: Ingests meeting invite / appointment document (e.g. *"Doctor Appointment on Oct 15 at 3:00 PM"*).
2. **Understand**: Extracts event timestamp (`2026-10-15T15:00:00`).
3. **Prepare Trigger**: Calculates reminder date (`event_date - 1 day` -> `2026-10-14T15:00:00`).
4. **Store**: Persists to memory store under `deadlines` category.
5. **Surface**: Dashboard displays upcoming reminder state under Deadlines view.

### Feature 4: Form-Filling Submissions (*"Things you need to submit"*) — Extension 2
1. **Detect**: Ingests incoming form request (e.g. expense reimbursement or renewal application).
2. **Prepare**: Uses stored memory (user details, prior receipts) to pre-populate required fields.
3. **Ask**: Surfaces pre-filled form in Approval View for one-click signature/review.

### Feature 5: Subscriptions & Expense Breakdown (*Roadmap / If Time Permits*)
1. Detect recurring charges across bills/statements.
2. Provide one-click cancellation letter preparation.
3. Monthly summary breakdown of total expenses.

---

## 5. File Watcher & Trigger Architecture

```
User drops file into
/workspace/inbox/  ──►  watcher.py (watchdog)  ──►  agent.process_new_document()
                                                            │
                                        ┌───────────────────┴───────────────────┐
                                        ▼                                       ▼
                                [Receipt / Bill / Form]             [Meeting / Appointment]
                                        │                                       │
                                Extract Event & Policy              Extract Event Timestamp
                                        │                                       │
                                Draft Action & Wait                 Set Trigger (Date - 1 Day)
                                        │                                       │
                                        ▼                                       ▼
                                 Approval Center                      Deadlines Timeline
```

* **Production mode**: Background `watchdog` monitoring `/workspace/inbox/`.
* **Demo/Presentation mode**: UI simulation buttons (*"Simulate: Receipt Arrives"*, *"Simulate: Complaint Email Arrives"*, *"Simulate: Meeting Invite Arrives"*) ensuring immediate, deterministic responses on camera.

---

## 6. UI Design Rules Reference (`LOOP-UI-Design-Rules.pdf`)

### Tokens
| Token | Hex | Usage |
| :--- | :--- | :--- |
| **Background** | `#F3F5F1` | Sage-tinted paper background |
| **Surface** | `#FFFFFF` | Cards, panels, approval view |
| **Ink** | `#1B2420` | Primary text (near-black with green undertone) |
| **Muted** | `#5B6B62` | Citations, timestamps, evidence lines |
| **Border** | `#E1E4DC` | 1px hairlines (no drop shadows) |
| **Loop Green**| `#1F5C45` | Primary actions, brand mark, resolved state |
| **Green Hover**| `#153F30` | Hover state for Loop Green |
| **Amber** | `#B8863B` | **All** dollar amounts (never green) |
| **Rust** | `#B54A2A` | Awaiting review emphasis & destructive reject button |

### Typography Hierarchy
* **Headlines**: Serif (`Georgia`, `Source Serif 4`) — Dashboard hero (28px Bold), Card titles (16px Bold).
* **UI & Body**: Sans-serif (`Inter`, `system-ui`) — Section headers (14px Bold), Body text (13px Regular).
* **Evidence Citations**: Monospace (`Consolas`, `SF Mono`) — 12px Regular for filenames, dates, line items.

---

## 7. Phased 5-Day Delivery Schedule

| Day | Developer 1 (Agent & Cloud) | Developer 2 (UI & Data) | Target Milestone |
| :--- | :--- | :--- | :--- |
| **Day 1** | Project setup, `models.py`, `LocalJsonStore`, base Strands agent setup | UI shell (paper palette, serif fonts, nav), synthetic files in `demo_data/` | Shared contract locked; UI runs on mock data |
| **Day 2** | The 6 tools implementation; Flagship Warranty Claim loop end-to-end | Dashboard Cards (colored borders), Approval View, Activity Timeline | Warranty claim functional from agent to UI |
| **Day 3** | Bill anomaly tool + Meeting/Appointment trigger logic | Watcher integration + UI simulation buttons + Arc closing animation | Bill anomaly & Appointment trigger functional |
| **Day 4** | DynamoDB store switch + Bedrock AgentCore deployment packaging | Form submission draft view + UI styling polish & accessibility contrast check | Full MVP + AgentCore deployment ready |
| **Day 5** | Public repo setup (MIT License, setup README, architecture diagram export) | Demo video recording (<5 mins against script) + Devpost text writeup | Final submission ready for Devpost |
