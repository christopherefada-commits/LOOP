"""
LOOP — Gmail OAuth2 & Automated Ingestion Module
Connects user's real Gmail account via Google OAuth 2.0 (read-only)
and syncs life-admin documents (receipts, bills, orders, bookings, warranties)
directly into workspace/inbox/ for autonomous agent processing.
"""

import os
import re
import json
import base64
from typing import Optional, Dict, Any, List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "google_token.json")
INBOX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workspace", "inbox")

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly"
]

# Ensure insecure transport is allowed for localhost development
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def get_client_config() -> Dict[str, Any]:
    """Builds client config dictionary from environment variables."""
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env")

    return {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [
                "http://localhost:5050/oauth2callback",
                "http://127.0.0.1:5050/oauth2callback"
            ]
        }
    }


def create_oauth_flow(redirect_uri: str) -> Flow:
    """Creates a Google OAuth Flow instance."""
    config = get_client_config()
    flow = Flow.from_client_config(
        config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    return flow


def save_credentials(creds: Credentials):
    """Saves OAuth credentials to local json file."""
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    creds_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(creds_data, f, indent=2)
    print(f"[GmailSync] Saved Google credentials to {TOKEN_FILE}")


def load_credentials() -> Optional[Credentials]:
    """Loads and refreshes OAuth credentials if available."""
    if not os.path.exists(TOKEN_FILE):
        return None

    try:
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)

        creds = Credentials(
            token=data.get("token"),
            refresh_token=data.get("refresh_token"),
            token_uri=data.get("token_uri"),
            client_id=data.get("client_id") or os.environ.get("GOOGLE_CLIENT_ID"),
            client_secret=data.get("client_secret") or os.environ.get("GOOGLE_CLIENT_SECRET"),
            scopes=data.get("scopes") or SCOPES
        )

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_credentials(creds)

        return creds
    except Exception as e:
        print(f"[GmailSync] Error loading credentials: {e}")
        return None


def get_user_profile(creds: Optional[Credentials] = None) -> Optional[Dict[str, Any]]:
    """Fetches user profile (name, email, picture) using OAuth2 / UserInfo API."""
    if not creds:
        creds = load_credentials()
    if not creds:
        return None

    try:
        service = build("oauth2", "v2", credentials=creds)
        user_info = service.userinfo().get().execute()
        email = user_info.get("email", "")
        name = user_info.get("name") or (email.split("@")[0].capitalize() if email else "User")
        given_name = user_info.get("given_name") or name.split()[0]
        return {
            "email": email,
            "name": name,
            "given_name": given_name,
            "picture": user_info.get("picture", "")
        }
    except Exception as e:
        print(f"[GmailSync] Notice fetching oauth2 userinfo: {e}")
        # Fallback to Gmail profile if oauth2 userinfo is restricted
        try:
            gmail_service = build("gmail", "v1", credentials=creds)
            profile = gmail_service.users().getProfile(userId="me").execute()
            email = profile.get("emailAddress", "")
            name = email.split("@")[0].replace(".", " ").title() if email else "User"
            return {
                "email": email,
                "name": name,
                "given_name": name.split()[0],
                "picture": ""
            }
        except Exception as e2:
            print(f"[GmailSync] Error fetching gmail profile: {e2}")
            return None


def get_connected_user() -> Optional[Dict[str, Any]]:
    """Returns connected Google account info or None."""
    creds = load_credentials()
    if not creds:
        return None

    try:
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        return {
            "email": profile.get("emailAddress"),
            "messages_total": profile.get("messagesTotal"),
            "threads_total": profile.get("threadsTotal")
        }
    except Exception as e:
        print(f"[GmailSync] Error retrieving profile: {e}")
        return None


def disconnect_google():
    """Removes stored token file."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print("[GmailSync] Disconnected Google account.")


def sync_gmail_inbox(max_results: int = 15) -> Dict[str, Any]:
    """
    Queries the user's Gmail for life-admin related emails:
    receipts, bills, orders, subscriptions, appointments, and warranties.
    Saves newly detected emails into workspace/inbox/ as markdown files.
    """
    creds = load_credentials()
    if not creds:
        return {"success": False, "error": "Not connected to Google"}

    try:
        service = build("gmail", "v1", credentials=creds)
        os.makedirs(INBOX_DIR, exist_ok=True)

        # Smart query for everyday admin documents
        query = (
            "subject:(receipt OR invoice OR bill OR warranty OR appointment OR booking "
            "OR confirmation OR order OR subscription OR statement OR reservation OR 'meeting invitation') "
            "OR filename:pdf"
        )

        response = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=max_results
        ).execute()

        messages = response.get("messages", [])
        if not messages:
            return {"success": True, "synced_count": 0, "messages": [], "note": "No matching life-admin emails found"}

        synced = []

        for msg_summary in messages:
            msg_id = msg_summary["id"]
            dest_file = os.path.join(INBOX_DIR, f"gmail_{msg_id}.md")

            # Skip if already ingested
            if os.path.exists(dest_file):
                continue

            msg = service.users().messages().get(
                userId="me",
                id=msg_id,
                format="full"
            ).execute()

            headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
            subject = headers.get("subject", "No Subject")
            sender = headers.get("from", "Unknown Sender")
            date_str = headers.get("date", "")

            # Extract body text
            body_text = _extract_body(msg.get("payload", {}))
            snippet = msg.get("snippet", "")

            # Format as clean markdown document
            content = (
                f"# {subject}\n\n"
                f"**From:** {sender}\n"
                f"**Date:** {date_str}\n"
                f"**Source:** Gmail (ID: {msg_id})\n\n"
                f"## Summary Snippet\n{snippet}\n\n"
                f"## Message Content\n\n"
                f"{body_text.strip() if body_text.strip() else snippet}\n"
            )

            with open(dest_file, "w", encoding="utf-8") as f:
                f.write(content)

            synced.append({
                "id": msg_id,
                "subject": subject,
                "sender": sender,
                "filename": f"gmail_{msg_id}.md"
            })
            print(f"[GmailSync] Ingested email into inbox: {subject} ({f'gmail_{msg_id}.md'})")

        return {
            "success": True,
            "synced_count": len(synced),
            "synced_emails": synced
        }

    except Exception as e:
        print(f"[GmailSync] Error during inbox sync: {e}")
        return {"success": False, "error": str(e)}


def _extract_body(payload: Dict[str, Any]) -> str:
    """Recursively extracts plain text body from a Gmail message payload."""
    body_data = ""

    if "parts" in payload:
        for part in payload["parts"]:
            mime_type = part.get("mimeType", "")
            if mime_type == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    try:
                        body_data += base64.urlsafe_b64decode(data).decode("utf-8", errors="replace") + "\n"
                    except Exception:
                        pass
            elif mime_type == "text/html" and not body_data:
                # Fallback to HTML stripped of tags if no plain text
                data = part.get("body", {}).get("data", "")
                if data:
                    try:
                        html = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                        # Basic tag stripper
                        clean_text = re.sub(r'<[^>]+>', ' ', html)
                        clean_text = re.sub(r'\s+', ' ', clean_text)
                        body_data += clean_text[:2000] + "\n"
                    except Exception:
                        pass
            elif "parts" in part:
                body_data += _extract_body(part)
    else:
        data = payload.get("body", {}).get("data", "")
        if data:
            try:
                body_data = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            except Exception:
                pass

    return body_data
