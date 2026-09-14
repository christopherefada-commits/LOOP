"""
LOOP — Workspace File Watcher & Ingestion Simulator.
1. Monitors /workspace/inbox/ for real dropped files.
2. Provides deterministic simulation triggers for live demo video presentations.
"""

import os
import shutil
import time
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class InboxHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str], None]):
        super().__init__()
        self.callback = callback
        self._last_event_time = 0

    def _handle_event(self, path: str):
        if os.path.basename(path).startswith("."):
            return
        now = time.time()
        if now - self._last_event_time < 0.8:
            return
        self._last_event_time = now
        time.sleep(0.3)
        print(f"[Watcher] Inbox file event detected: {path}")
        self.callback(path)

    def on_created(self, event):
        if not event.is_directory:
            self._handle_event(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._handle_event(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._handle_event(event.dest_path)


class WorkspaceWatcher:
    def __init__(self, workspace_dir: Optional[str] = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.workspace_dir = workspace_dir or os.path.join(base_dir, "workspace")
        self.inbox_dir = os.path.join(self.workspace_dir, "inbox")
        self.processed_dir = os.path.join(self.workspace_dir, "processed")
        self.demo_dir = os.path.join(base_dir, "demo_data")
        
        os.makedirs(self.inbox_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        self.observer: Optional[Observer] = None

    def start(self, on_file_added: Callable[[str], None]):
        """Starts the background directory watcher."""
        handler = InboxHandler(on_file_added)
        self.observer = Observer()
        self.observer.schedule(handler, path=self.inbox_dir, recursive=False)
        self.observer.start()
        print(f"[Watcher] Observing inbox at: {self.inbox_dir}")

    def stop(self):
        """Stops the directory watcher."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("[Watcher] Observer stopped.")

    def simulate_file_drop(self, preset_name: str) -> str:
        """
        Copies a synthetic document from demo_data into the inbox.
        Guarantees 100% deterministic, instant simulation for live demo videos.
        """
        preset_map = {
            "receipt": ("receipts", "receipt_sony_wh1000.txt"),
            "complaint": ("emails", "email_headphones_fault.txt"),
            "bills": ("bills", "electricity_bills_history.json"),
            "appointment": ("invites", "calendar_invite_dentist.txt"),
            "form": ("forms", "medical_reimbursement_form.json"),
            "renewal": ("emails", "streaming_renewal_notice.txt")
        }

        if preset_name not in preset_map:
            raise ValueError(f"Unknown preset '{preset_name}'. Supported: {list(preset_map.keys())}")

        subfolder, filename = preset_map[preset_name]
        src = os.path.join(self.demo_dir, subfolder, filename)
        dest = os.path.join(self.inbox_dir, filename)

        if not os.path.exists(src):
            raise FileNotFoundError(f"Source demo file not found: {src}")

        shutil.copyfile(src, dest)
        print(f"[Watcher] Simulated drop of '{filename}' into inbox.")
        return dest
