"""
Unit tests for LOOP's 7 generalized tools.
Tests tools against the synthetic dataset directly before wiring the agent.
"""

import os
import pytest
from tools.scan_workspace import scan_workspace
from tools.access_memory import access_memory
from tools.lookup_rules import lookup_rules
from tools.analyze_record import analyze_record
from tools.prepare_action import prepare_action
from tools.request_approval import request_approval
from tools.commit_action import commit_action
from store.factory import get_store
from models import LifeEvent, LifeEventType, LifeEventCategory, LifeEventStatus


@pytest.fixture(autouse=True)
def clean_store():
    store = get_store()
    store.clear_all()
    yield
    store.clear_all()


def test_scan_workspace():
    docs = scan_workspace()
    assert len(docs) > 0
    filenames = [d["filename"] for d in docs]
    assert "receipt_sony_wh1000.txt" in filenames
    assert "email_headphones_fault.txt" in filenames
    assert "electricity_bills_history.json" in filenames


def test_access_memory():
    store = get_store()
    evt = LifeEvent(
        id="evt_test_1",
        type=LifeEventType.WARRANTY,
        title="Sony WH-1000XM5 Warranty",
        summary="Active warranty for Sony Headphones",
        status=LifeEventStatus.DETECTED,
        category=LifeEventCategory.MONEY_RECOVER,
        dollar_amount=179.0
    )
    store.save_event(evt)

    results = access_memory(query="Sony")
    assert len(results) == 1
    assert results[0]["id"] == "evt_test_1"
    assert results[0]["dollar_amount"] == 179.0


def test_lookup_rules():
    result = lookup_rules(topic="warranty", entity_name="Sony")
    assert result["found"] is True
    assert len(result["policies"]) > 0
    assert "one (1) year" in result["policies"][0]["content"]


def test_analyze_record_bill():
    data = {
        "current_amount": 187.00,
        "historical_amounts": [145.20, 148.50, 142.80, 151.30, 147.20],
        "threshold_pct": 15.0
    }
    result = analyze_record("bill_anomaly", data)
    assert result["success"] is True
    assert result["anomaly_detected"] is True
    assert result["percentage_difference"] > 25.0
    assert result["historical_average"] > 140.0


def test_analyze_record_schedule():
    data = {
        "event_datetime": "2026-10-15T15:00:00",
        "offset_days": 1
    }
    result = analyze_record("schedule_trigger", data)
    assert result["success"] is True
    assert result["trigger_datetime"].startswith("2026-10-14T15:00:00")
    assert "1 day before" in result["summary"]


def test_prepare_action_warranty():
    details = {
        "product_name": "Sony WH-1000XM5 Wireless Headphones",
        "serial_number": "SN-WH5-9832144",
        "order_id": "REC-2026-0392",
        "purchase_date": "March 14, 2026",
        "amount": 179.00
    }
    res = prepare_action("evt_sony_claim", "warranty_claim", details)
    assert res["success"] is True
    assert "Sony WH-1000XM5" in res["prepared_action"]
    assert "REC-2026-0392" in res["prepared_action"]

    # Verify saved in store
    store = get_store()
    saved = store.get_event("evt_sony_claim")
    assert saved is not None
    assert saved.status == LifeEventStatus.PREPARED


def test_request_approval_and_commit():
    store = get_store()
    evt = LifeEvent(
        id="evt_flow_1",
        type=LifeEventType.WARRANTY,
        title="Sony Replacement Claim",
        summary="Claim prepared for approval",
        status=LifeEventStatus.PREPARED,
        category=LifeEventCategory.MONEY_RECOVER,
        dollar_amount=179.0
    )
    store.save_event(evt)

    # Step 1: Request approval
    req_res = request_approval("evt_flow_1", "Submit warranty claim", "Proof attached")
    assert req_res["status"] == "awaiting_approval"
    assert store.get_event("evt_flow_1").status == LifeEventStatus.AWAITING_APPROVAL

    # Step 2: Commit action (User approved)
    commit_res = commit_action("evt_flow_1", decision="approve")
    assert commit_res["success"] is True
    assert commit_res["new_status"] == "completed"

    # Step 3: Check activity timeline
    timeline = store.get_timeline()
    assert len(timeline) >= 2
    messages = [t.message for t in timeline]
    assert any("Awaiting your review" in m for m in messages)
    assert any("Approved and submitted" in m for m in messages)
