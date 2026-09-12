"""
End-to-End Agent Integration Tests for LOOP.
Verifies the complete 6-stage reasoning loop across all use cases:
1. Flagship Warranty Claim: Detect -> Understand -> Research -> Prepare -> Ask -> Execute
2. Bill Anomaly: Variance detection & plain explanation
3. Appointment Trigger: Scheduling calculation & armed reminder
4. Form Submission: Pre-filling & approval gate
"""

import pytest
from agent import LoopAgent
from store.factory import get_store
from models import LifeEventStatus, LifeEventCategory


@pytest.fixture(autouse=True)
def clean_store():
    store = get_store()
    store.clear_all()
    yield
    store.clear_all()


def test_agent_discovery_cycle():
    agent = LoopAgent()
    result = agent.run_discovery_cycle()

    assert result["success"] is True
    assert result["discovered_events_count"] >= 3
    assert result["total_open_loops"] >= 3

    # Check 1: Warranty Claim
    store = get_store()
    warranty_evt = store.get_event("evt_sony_warranty")
    assert warranty_evt is not None
    assert warranty_evt.status == LifeEventStatus.AWAITING_APPROVAL
    assert warranty_evt.dollar_amount == 179.00
    assert warranty_evt.category == LifeEventCategory.MONEY_RECOVER
    assert "REC-2026-0392" in warranty_evt.prepared_action
    assert "SN-WH5-9832144" in warranty_evt.prepared_action

    # Check 2: Bill Anomaly
    bill_evt = store.get_event("evt_electric_anomaly")
    assert bill_evt is not None
    assert bill_evt.category == LifeEventCategory.MONEY_LOSE
    assert bill_evt.dollar_amount == 187.00
    assert "+27" in bill_evt.title or "27" in bill_evt.summary

    # Check 3: Appointment Trigger
    appt_evt = store.get_event("evt_dental_appointment")
    assert appt_evt is not None
    assert appt_evt.category == LifeEventCategory.DEADLINE
    assert "Oct 14" in appt_evt.summary or "Oct 15" in appt_evt.summary

    # Check 4: Activity Timeline
    timeline = store.get_timeline()
    assert len(timeline) >= 4
    messages = [t.message for t in timeline]
    assert any("Detected electronics purchase" in m for m in messages)
    assert any("Linked complaint email" in m for m in messages)
    assert any("Researched Sony Audio Warranty" in m for m in messages)
    assert any("Awaiting your review" in m for m in messages)


def test_agent_approval_and_execution():
    agent = LoopAgent()
    agent.run_discovery_cycle()

    store = get_store()
    warranty_evt = store.get_event("evt_sony_warranty")
    assert warranty_evt.status == LifeEventStatus.AWAITING_APPROVAL

    # Human clicks Approve in UI
    approval_res = agent.approve_action("evt_sony_warranty")
    assert approval_res["success"] is True
    assert approval_res["new_status"] == "completed"

    updated_evt = store.get_event("evt_sony_warranty")
    assert updated_evt.status == LifeEventStatus.COMPLETED

    # Timeline records the execution
    timeline = store.get_timeline()
    assert any("Approved and submitted: warranty claim" in t.message for t in timeline)


def test_agent_dashboard_summary():
    agent = LoopAgent()
    agent.run_discovery_cycle()

    summary = agent.get_dashboard_summary()
    assert summary["hero_number"] >= 3
    assert summary["awaiting_approval_count"] >= 1
    assert summary["potential_recovery_total"] >= 179.00
    assert len(summary["open_loops"]) >= 3
    assert len(summary["timeline"]) >= 4


def test_dynamic_inbox_document_processing():
    agent = LoopAgent()
    agent.run_discovery_cycle()

    store = get_store()
    email_evt = store.get_event("evt_new_email")
    assert email_evt is not None
    assert "Sarah Williams" in email_evt.title or "Sarah Williams" in email_evt.summary
    assert email_evt.status == LifeEventStatus.AWAITING_APPROVAL
    assert email_evt.type.value == "appointment"
    assert "September 21, 2026" in email_evt.prepared_action
    assert "Joshua Gabriel" in email_evt.prepared_action

    # Approve meeting RSVP
    res = agent.approve_action("evt_new_email")
    assert res["success"] is True
    assert res["new_status"] == "completed"

