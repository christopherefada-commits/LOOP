# LOOP — System Architecture Diagram

This document contains the generalized system architecture for **LOOP**, built for the **Agents for Humans Hackathon** using the **Strands Agents SDK on Amazon Bedrock**.

```mermaid
flowchart TB
    %% Styling Classes matching LOOP UI Design System
    classDef userLayer fill:#FFFFFF,stroke:#1F5C45,stroke-width:2px,color:#1B2420;
    classDef uiLayer fill:#F3F5F1,stroke:#1F5C45,stroke-width:2px,color:#1B2420;
    classDef agentLayer fill:#1F5C45,stroke:#153F30,stroke-width:2px,color:#FFFFFF;
    classDef toolLayer fill:#FFFFFF,stroke:#5B6B62,stroke-width:1.5px,color:#1B2420;
    classDef storeLayer fill:#FFFFFF,stroke:#B8863B,stroke-width:2px,color:#1B2420;
    classDef externalLayer fill:#FFFFFF,stroke:#E1E4DC,stroke-width:1.5px,color:#5B6B62;

    subgraph USER_EXPERIENCE ["User & Interface Layer"]
        USER["User (Human Decision Maker)"]:::userLayer
        UI["LOOP Dashboard & Approval UI<br/>• Open Loops Hero Counter<br/>• Monospace Evidence Citations<br/>• Approval View (Approve / Edit / Reject)<br/>• Deadlines & Timeline View"]:::uiLayer
    end

    subgraph INGESTION ["Workspace Ingestion"]
        WATCHER["Workspace Inbox Watcher<br/>(/workspace/inbox/ + UI Simulation)"]:::externalLayer
    end

    subgraph AGENT_CORE ["Agent Intelligence (Amazon Bedrock)"]
        AGENT["LOOP Orchestrator Agent<br/>Strands Agents SDK (Python)<br/>Claude 3.5 Sonnet / Haiku (us-east-1)"]:::agentLayer
    end

    subgraph TOOLS ["Generalized Toolset"]
        T1["scan_workspace<br/>(Reads files, emails, invites, forms)"]:::toolLayer
        T2["access_memory<br/>(Queries active loops & past events)"]:::toolLayer
        T3["lookup_rules<br/>(Checks warranties, windows, policies)"]:::toolLayer
        T4["analyze_record<br/>(Flags bill spikes OR calculates date - 1 day)"]:::toolLayer
        T5["prepare_action<br/>(Drafts claim letters, forms, reminders)"]:::toolLayer
        T6["request_approval<br/>(Strands HITL Checkpoint)"]:::toolLayer
        T7["commit_action<br/>(Resolves loop & arms trigger)"]:::toolLayer
    end

    subgraph DATA_MEMORY ["Dual-Store & Reference Memory"]
        KB["Reference Policy Docs<br/>(Warranty terms, rate schedules)"]:::externalLayer
        STORE["Life Events Memory Store<br/>(Dual: Local JSON + DynamoDB)<br/>• Open Loops State<br/>• Armed Triggers & Deadlines<br/>• Narrative Activity Timeline"]:::storeLayer
    end

    subgraph RUNTIME ["Deployment (Scoring Bonus)"]
        AGENTCORE["Amazon Bedrock AgentCore Runtime<br/>(Session Isolation & Long-Running State)"]:::externalLayer
    end

    %% Flows
    WATCHER -->|"New file detected"| AGENT
    UI -->|"Dispatches run / Polls state"| STORE
    
    AGENT --- AGENTCORE
    AGENT -->|"Orchestrates loop"| TOOLS

    T1 -->|"Ingests raw evidence"| WATCHER
    T2 <-->|"Reads/Links context"| STORE
    T3 -->|"Queries clauses"| KB
    T4 -->|"Performs math & date calc"| AGENT
    T5 -->|"Prepares drafted payload"| STORE
    
    T6 -.->|"HIGH IMPACT: Pauses execution"| USER
    USER -.->|"Approves claim / Confirms trigger"| UI
    UI -->|"Triggers resolution"| T7
    T7 -->|"Commits status: completed"| STORE

    %% Decision Point Styling
    linkStyle 11 stroke:#B54A2A,stroke-width:2px,stroke-dasharray: 5 5;
    linkStyle 12 stroke:#1F5C45,stroke-width:2px,stroke-dasharray: 5 5;
    linkStyle 13 stroke:#1F5C45,stroke-width:2px;
```

---

## Component Description

### 1. User & Interface Layer
* **Human in the Loop**: The user remains the authoritative decision-maker for all high-impact actions.
* **Paper-Toned UI**: Implements the `LOOP-UI-Design-Rules.pdf` specification (sage paper `#F3F5F1`, serif headers, mono citations, amber money highlights, and animated arc mark).

### 2. Ingestion & Workspace Watcher
* Ingests receipts, bills, emails, calendar invites, and forms as they enter `/workspace/inbox/`.
* Includes deterministic UI simulation triggers for smooth, reproducible live demo presentations.

### 3. Agent Intelligence
* Powered by the **Strands Agents SDK** running against **Amazon Bedrock** (`Claude 3.5 Sonnet` / `Claude 3 Haiku` in `us-east-1`).
* Implements the **Autonomous by default, human when it matters** reasoning loop.

### 4. Generalized Toolset
* Replaces narrow, single-purpose tools with 7 robust domain-agnostic tools capable of handling money recovery, billing anomalies, appointment triggers, and form-filling.

### 5. Dual-Store Memory & Policy Reference
* **Local JSON**: Zero-dependency instant local execution for testing and offline presentations.
* **DynamoDB**: Managed AWS cloud table for production scalability and multi-session persistence.

### 6. Bedrock AgentCore Runtime
* Packages the Strands orchestrator for serverless session management and automated logging to secure the hackathon's technical bonus points.
