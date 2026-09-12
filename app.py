"""
LOOP — Web Application Server
Serves the paper-toned UI adhering strictly to LOOP-UI-Design-Rules.pdf.
Provides REST endpoints for dashboard state, approval actions, and demo simulation triggers.
"""

import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from agent import LoopAgent, _load_env_file
from store.factory import get_store
from watcher import WorkspaceWatcher
from models import LifeEventStatus, LifeEventCategory
from tools.gmail_sync import (
    create_oauth_flow, save_credentials, get_connected_user,
    get_user_profile, sync_gmail_inbox, disconnect_google
)

# Ensure environment variables are loaded
_load_env_file()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "loop-agent-hackathon-2026-auth-gate")
agent = LoopAgent()
watcher = WorkspaceWatcher()

def on_inbox_file_detected(filepath: str):
    """Callback triggered whenever a document is dropped into workspace/inbox."""
    print(f"[App] Processing incoming file from inbox: {filepath}")
    agent.process_incoming_file(filepath)

# Start real-time background file watcher
try:
    watcher.start(on_inbox_file_detected)
except Exception as e:
    print(f"[App] Watcher startup notice: {e}")

# Run an initial discovery scan on server startup so dashboard opens populated
agent.run_discovery_cycle()


@app.route("/login")
def login():
    """Serves the paper-toned welcome and Google sign-in gate."""
    if session.get("user"):
        return redirect("/")
    return render_template("login.html")


@app.route("/")
def index():
    """Serves the main dashboard (requires authentication or demo mode)."""
    user = session.get("user")
    if not user:
        return redirect("/login")
    return render_template("index.html", user=user)


@app.route("/api/summary", methods=["GET"])
def get_summary():
    """Returns the live state for the dashboard, approval views, and timeline."""
    # Ensure any new inbox items are captured
    agent.run_discovery_cycle()
    summary = agent.get_dashboard_summary()
    return jsonify(summary)


@app.route("/api/event/<event_id>", methods=["GET"])
def get_event(event_id):
    """Returns full details for a single Life Event (used by the Approval View modal/screen)."""
    store = get_store()
    evt = store.get_event(event_id)
    if not evt:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(evt.to_dict())


@app.route("/api/run-discovery", methods=["POST"])
def run_discovery():
    """Triggers the agent's 6-stage autonomous reasoning loop."""
    result = agent.run_discovery_cycle()
    summary = agent.get_dashboard_summary()
    return jsonify({"result": result, "summary": summary})


@app.route("/api/approve/<event_id>", methods=["POST"])
def approve_event(event_id):
    """Approves and executes the prepared action for a Life Event."""
    res = agent.approve_action(event_id)
    summary = agent.get_dashboard_summary()
    return jsonify({"result": res, "summary": summary})


@app.route("/api/reject/<event_id>", methods=["POST"])
def reject_event(event_id):
    """Dismisses an open loop."""
    res = agent.reject_action(event_id)
    summary = agent.get_dashboard_summary()
    return jsonify({"result": res, "summary": summary})


@app.route("/api/edit/<event_id>", methods=["POST"])
def edit_event(event_id):
    """Saves user modifications to a prepared draft."""
    data = request.get_json() or {}
    new_text = data.get("text", "")
    res = agent.edit_action(event_id, new_text)
    summary = agent.get_dashboard_summary()
    return jsonify({"result": res, "summary": summary})


@app.route("/api/simulate/<preset_name>", methods=["POST"])
def simulate_drop(preset_name):
    """Simulates dropping a synthetic document into the workspace inbox for live video recordings."""
    try:
        dest = watcher.simulate_file_drop(preset_name)
        # Process the newly arrived document
        agent.run_discovery_cycle()
        summary = agent.get_dashboard_summary()
        return jsonify({"success": True, "file": dest, "summary": summary})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/reset", methods=["POST"])
def reset_demo():
    """Resets the store and re-runs initial discovery for a clean demo recording restart."""
    store = get_store()
    store.clear_all()
    agent.run_discovery_cycle()
    summary = agent.get_dashboard_summary()
    return jsonify({"success": True, "summary": summary})


# ------------------------------------------------------------------
# Google OAuth & Gmail Ingestion Endpoints
# ------------------------------------------------------------------
@app.route("/auth/google")
def auth_google():
    """Initiates Google OAuth 2.0 flow."""
    redirect_uri = request.host_url.rstrip("/") + "/oauth2callback"
    flow = create_oauth_flow(redirect_uri)
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return redirect(auth_url)


@app.route("/oauth2callback")
def oauth2callback():
    """OAuth redirect callback handler from Google."""
    redirect_uri = request.host_url.rstrip("/") + "/oauth2callback"
    try:
        flow = create_oauth_flow(redirect_uri)
        flow.fetch_token(authorization_response=request.url)
        save_credentials(flow.credentials)
        profile = get_user_profile(flow.credentials) or {}
        session["user"] = {
            "name": profile.get("name", "Google User"),
            "given_name": profile.get("given_name", "User"),
            "email": profile.get("email", ""),
            "picture": profile.get("picture", ""),
            "is_demo": False
        }
        # Perform initial sync
        sync_gmail_inbox(max_results=10)
        return redirect("/?google_connected=true")
    except Exception as e:
        print(f"[App] OAuth callback error: {e}")
        return redirect(f"/login?error={str(e)}")


@app.route("/auth/demo")
def auth_demo():
    """Bypasses Google OAuth for hackathon judges and evaluators."""
    session["user"] = {
        "name": "Alex Mercer (Demo)",
        "given_name": "Alex",
        "email": "demo.sandbox@loopagent.internal",
        "picture": "",
        "is_demo": True
    }
    return redirect("/")


@app.route("/auth/logout")
def auth_logout():
    """Logs the user out and redirects to the sign-in gate."""
    session.clear()
    return redirect("/login")


@app.route("/api/me", methods=["GET"])
def get_current_user():
    """Returns currently authenticated user session details."""
    user = session.get("user")
    if not user:
        return jsonify({"authenticated": False}), 401
    return jsonify({"authenticated": True, "user": user})


@app.route("/api/google/status", methods=["GET"])
def google_status():
    """Returns Google account connection status and email."""
    user = session.get("user")
    user_info = get_connected_user()
    return jsonify({
        "connected": user_info is not None or (user and not user.get("is_demo")),
        "user": user_info or ({"email": user.get("email")} if user else None),
        "session_user": user
    })


@app.route("/api/google/sync", methods=["POST"])
def google_sync():
    """Manually triggers Gmail inbox sync for life-admin documents."""
    res = sync_gmail_inbox(max_results=15)
    agent.run_discovery_cycle()
    summary = agent.get_dashboard_summary()
    return jsonify({"result": res, "summary": summary})


@app.route("/api/google/disconnect", methods=["POST"])
def google_disconnect():
    """Disconnects Google account and clears session."""
    disconnect_google()
    session.clear()
    return jsonify({"success": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Starting LOOP web server on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
