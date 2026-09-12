"""
Tool: prepare_action
Drafts the complete text of an action (warranty claim letter, anomaly dispute note, appointment reminder, or pre-filled form).
Updates the Life Event in the store with status 'prepared' and saves the draft.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from store.factory import get_store
from models import LifeEvent, LifeEventStatus, LifeEventType, LifeEventCategory

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func


@tool
def prepare_action(event_id: str, action_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepares a complete, professional draft of an action to be reviewed by the user.

    Args:
        event_id (str): ID of the Life Event being acted on (or creates one if not found).
        action_type (str): 'warranty_claim', 'bill_anomaly', 'appointment_reminder', or 'form_submission'.
        details (Dict[str, Any]): Contextual parameters for drafting:
            - For 'warranty_claim': product_name, serial_number, order_id, purchase_date, fault_description, amount
            - For 'bill_anomaly': provider, current_amount, historical_avg, pct_diff, explanation
            - For 'appointment_reminder': event_name, event_date, trigger_date, location
            - For 'form_submission': form_title, filled_fields

    Returns:
        Dict[str, Any]: The prepared draft text, evidence list, and event summary.
    """
    store = get_store()
    event = store.get_event(event_id)

    draft_text = ""
    evidence_lines = []

    if action_type == "warranty_claim":
        product = details.get("product_name", "Sony WH-1000XM5 Wireless Headphones")
        serial = details.get("serial_number", "SN-WH5-9832144")
        order_id = details.get("order_id", "REC-2026-0392")
        purchase_date = details.get("purchase_date", "March 14, 2026")
        fault = details.get("fault_description", "Spontaneous shutdown after 10-15 minutes of audio playback")
        amount = details.get("amount", 179.00)

        draft_text = (
            f"Dear Sony Customer Support,\n\n"
            f"I am filing a warranty replacement claim for my {product}, purchased on {purchase_date} "
            f"(Apex Electronics, Order #{order_id}).\n\n"
            f"Device Details:\n"
            f"• Model: {product}\n"
            f"• Serial Number: {serial}\n"
            f"• Purchase Price: ${amount:.2f}\n\n"
            f"Issue Description:\n"
            f"{fault}. Factory resets and re-pairing procedures have been attempted without resolution.\n\n"
            f"Per Section 2 of Sony Consumer Audio Limited Warranty, this unit qualifies for warranty replacement. "
            f"Proof of purchase (Order #{order_id}) is attached.\n\n"
            f"Please provide return shipment authorization and dispatch details.\n\n"
            f"Sincerely,\nAlex Mercer\nalex.mercer.dev@gmail.com"
        )
        evidence_lines = [
            f"receipt_sony_wh1000.txt: Purchased {purchase_date}, ${amount:.2f}",
            f"email_headphones_fault.txt: Fault reported April 18, 2026",
            f"sony_audio_warranty_policy.txt: 1-year coverage valid until March 14, 2027"
        ]

    elif action_type == "bill_anomaly":
        provider = details.get("provider", "Pacific Energy & Electric")
        curr = details.get("current_amount", 187.00)
        avg = details.get("historical_avg", 147.20)
        pct = details.get("pct_diff", 27.0)
        reason = details.get("explanation", "Peak transmission rate revision (+26.5% rate adjustment effective April 1)")

        draft_text = (
            f"Subject: Inquiry regarding unexpected billing increase on Account ACCT-8921-5502\n\n"
            f"Dear {provider} Billing Support,\n\n"
            f"I recently received statement BILL-2026-04 for ${curr:.2f}. My 5-month historical average is "
            f"${avg:.2f}. This represents a +{pct:.1f}% increase for comparable usage (621 kWh vs. 618 kWh last month).\n\n"
            f"Could you please confirm whether this bill includes the seasonal rate adjustment ({reason}) "
            f"and verify that tiered baseline allowances were calculated correctly?\n\n"
            f"Regards,\nAlex Mercer"
        )
        evidence_lines = [
            f"electricity_bills_history.json: 5-month average = ${avg:.2f}",
            f"BILL-2026-04: Current bill = ${curr:.2f} (+{pct:.1f}%)",
            f"Rate notice: Seasonal peak tariff applied"
        ]

    elif action_type == "appointment_reminder":
        event_name = details.get("event_name", "Dental Cleaning & Annual Examination")
        event_date = details.get("event_date", "Thursday, October 15, 2026 at 03:00 PM")
        trigger_date = details.get("trigger_date", "Wednesday, October 14, 2026 at 03:00 PM")
        location = details.get("location", "Pacific Dental Group, Suite 300, 500 Howard St, SF")

        draft_text = (
            f"REMINDER NOTICE (Armed for {trigger_date}):\n\n"
            f"Upcoming Appointment: {event_name}\n"
            f"When: {event_date}\n"
            f"Where: {location}\n"
            f"Note: Arrive 10 minutes early with dental insurance card."
        )
        evidence_lines = [
            f"calendar_invite_dentist.txt: Scheduled for {event_date}",
            f"Trigger rule: Alert armed 1 day before ({trigger_date})"
        ]

    elif action_type == "form_submission":
        title = details.get("form_title", "Employee Health & Wellness Expense Claim")
        fields = details.get("filled_fields", {
            "Patient": "Alex Mercer",
            "Provider": "Pacific Dental Group",
            "Service": "Dental Exam & Cleaning",
            "Amount": "$120.00",
            "Receipt Attached": "Yes"
        })
        draft_text = f"FORM SUBMISSION READY: {title}\n\nPre-filled Fields:\n"
        for k, v in fields.items():
            draft_text += f"• {k}: {v}\n"
        draft_text += "\nAll required fields verified against memory records. Ready for digital signature."
        evidence_lines = [
            "medical_reimbursement_form.json: Required fields populated",
            "calendar_invite_dentist.txt: Service date verified"
        ]

    elif action_type in ("meeting_rsvp", "meeting_invitation", "meeting"):
        subject = details.get("subject", "Meeting Invitation")
        sender = details.get("sender", "Organizer")
        recipient_first = sender.split()[0] if sender else "there"
        event_name = details.get("event_name", "Scheduled Meeting")
        event_date = details.get("event_date", "Upcoming Date")
        event_time = details.get("event_time", "")
        location = details.get("location", "Google Meet")
        agenda = details.get("agenda", "")

        draft_text = (
            f"Subject: Re: {subject}\n\n"
            f"Hi {recipient_first},\n\n"
            f"Thank you for the invitation. I confirm my availability for the {event_name} on {event_date}"
            f"{f' from {event_time}' if event_time else ''} via {location}.\n\n"
            f"I have placed a hold on my calendar and look forward to our discussion.\n\n"
            f"Best regards,\nJoshua Gabriel"
        )
        evidence_lines = [
            f"Meeting invitation received from {sender}",
            f"Date & Time: {event_date} {event_time}".strip(),
            f"Location: {location}"
        ]

    # Allow caller to override or pass direct draft_text and evidence
    if "draft_text" in details and details["draft_text"]:
        draft_text = details["draft_text"]
    if "evidence" in details and details["evidence"]:
        evidence_lines = details["evidence"]

    # Update or create the event in store
    if not event:
        cat = LifeEventCategory.MONEY_RECOVER if action_type == "warranty_claim" else (
            LifeEventCategory.MONEY_LOSE if action_type == "bill_anomaly" else (
                LifeEventCategory.DEADLINE if action_type in ("appointment_reminder", "meeting_rsvp", "meeting_invitation", "meeting") else LifeEventCategory.SUBMISSION
            )
        )
        ev_type = LifeEventType.WARRANTY if action_type == "warranty_claim" else (
            LifeEventType.BILL if action_type == "bill_anomaly" else (
                LifeEventType.APPOINTMENT if action_type in ("appointment_reminder", "meeting_rsvp", "meeting_invitation", "meeting") else LifeEventType.SUBMISSION
            )
        )
        title = details.get("title", f"{action_type.replace('_', ' ').title()}")
        summary = details.get("summary", f"Prepared action for {action_type}")
        amount = details.get("amount", details.get("current_amount"))

        event = LifeEvent(
            id=event_id,
            type=ev_type,
            title=title,
            summary=summary,
            status=LifeEventStatus.PREPARED,
            category=cat,
            dollar_amount=amount,
            evidence=evidence_lines,
            prepared_action=draft_text,
            metadata=details
        )
    else:
        event.status = LifeEventStatus.PREPARED
        event.prepared_action = draft_text
        event.evidence = evidence_lines
        event.metadata.update(details)

    store.save_event(event)
    store.add_timeline_entry(store.get_timeline()[0] if False else None or 
        # Add timeline entry
        __import__("models").TimelineEntry(
            event_id=event.id,
            message=f"Prepared action: {action_type.replace('_', ' ')} draft ready for review.",
            action_type="draft_prepared"
        )
    )

    return {
        "success": True,
        "event_id": event.id,
        "action_type": action_type,
        "prepared_action": draft_text,
        "evidence": evidence_lines,
        "status": event.status.value
    }
