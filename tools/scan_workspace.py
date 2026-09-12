"""
Tool: scan_workspace
Scans the workspace inbox (or demo datasets) for incoming receipts, emails, bills, calendar invites, and forms.
"""

import os
import json
from typing import List, Dict, Any

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func


@tool
def scan_workspace(category: str = "all") -> List[Dict[str, Any]]:
    """
    Scans the user workspace inbox for incoming files, emails, bills, receipts, and calendar invitations.

    Args:
        category (str): Filter by document category ('all', 'receipts', 'emails', 'bills', 'invites', 'forms').

    Returns:
        List[Dict[str, Any]]: List of discovered documents with filename, file_type, and text content.
    """
    results = []
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check live inbox first, then fallback to demo_data
    inbox_dir = os.path.join(base_dir, "workspace", "inbox")
    demo_dir = os.path.join(base_dir, "demo_data")
    
    scan_paths = []
    if os.path.exists(inbox_dir) and os.listdir(inbox_dir):
        scan_paths.append(("inbox", inbox_dir))
    if os.path.exists(demo_dir):
        scan_paths.append(("demo_data", demo_dir))

    for source_type, path in scan_paths:
        for root, _, files in os.walk(path):
            for file in sorted(files):
                if file.startswith("."):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                
                # Smart category filtering
                if category != "all":
                    cat_clean = category.rstrip("s").lower()
                    rel_lower = rel_path.lower()
                    content_lower = ""
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                            content_preview = f.read(500).lower()
                    except Exception:
                        content_preview = ""
                    
                    matches = (
                        cat_clean in rel_lower or
                        category.lower() in rel_lower or
                        (cat_clean in ("email", "mail") and any(k in content_preview for k in ["from:", "subject:", "to:"])) or
                        (cat_clean in ("receipt", "invoice") and any(k in content_preview for k in ["receipt", "order #", "purchase", "total:"])) or
                        (cat_clean in ("bill", "utility") and any(k in content_preview for k in ["bill", "statement", "kwh", "tariff", "due date"])) or
                        (cat_clean in ("invite", "calendar", "appointment") and any(k in content_preview for k in ["meeting", "invite", "appointment", "calendar", "agenda"])) or
                        (cat_clean in ("form", "claim") and any(k in content_preview for k in ["form", "claim", "reimbursement"]))
                    )
                    if not matches:
                        continue
                
                try:
                    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                        
                    results.append({
                        "filename": file,
                        "relative_path": rel_path,
                        "source": source_type,
                        "size_bytes": os.path.getsize(full_path),
                        "content": content
                    })
                except Exception as e:
                    print(f"[scan_workspace] Could not read {full_path}: {e}")

    return results
