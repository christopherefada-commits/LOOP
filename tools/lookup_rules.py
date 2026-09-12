"""
Tool: lookup_rules
Retrieves reference warranty policies, return windows, and dispute guidelines.
"""

import os
from typing import Dict, Any, Optional

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func


@tool
def lookup_rules(topic: str, entity_name: str = "") -> Dict[str, Any]:
    """
    Searches the reference policy knowledge base for warranty coverage, return windows, and terms.

    Args:
        topic (str): The subject of lookup (e.g. 'warranty', 'return_policy', 'billing_dispute').
        entity_name (str): Company or manufacturer name (e.g. 'Sony', 'Pacific Energy').

    Returns:
        Dict[str, Any]: Policy rules found, including coverage terms and contact info.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    policies_dir = os.path.join(base_dir, "demo_data", "policies")

    results = []
    if os.path.exists(policies_dir):
        for file in os.listdir(policies_dir):
            full_path = os.path.join(policies_dir, file)
            if os.path.isfile(full_path):
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                    
                match = False
                if not entity_name or entity_name.lower() in content.lower() or entity_name.lower() in file.lower():
                    if not topic or topic.lower() in content.lower() or topic.lower() in file.lower():
                        match = True
                
                if match:
                    results.append({
                        "policy_document": file,
                        "content": content
                    })

    if results:
        return {
            "found": True,
            "policies": results,
            "summary": f"Found {len(results)} matching policy document(s) for {entity_name or topic}."
        }
    
    return {
        "found": False,
        "policies": [],
        "summary": f"No specific policy document found for topic '{topic}' and entity '{entity_name}'."
    }
