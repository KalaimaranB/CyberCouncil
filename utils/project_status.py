"""
Project Status Tracking Module

Manages project lifecycle and prevents reopening of finalized investigations.
Creates .status files in project directories to track active/closed state.

Key Functions:
- mark_project_closed(): Marks a project as finalized
- is_project_closed(): Checks if a project is closed  
- get_project_info(): Returns project status information

Closed projects cannot be reopened to preserve investigation integrity.

Usage:
    import project_status
    project_status.mark_project_closed("Operation_Phoenix")
    is_closed, data = project_status.is_project_closed("Operation_Phoenix")

Author: CyberCouncil Project
"""

import os
import json
import time
from core import config
from utils.tools import sanitize_project_name

def mark_project_closed(project_name):
    """
    Mark a project as closed/finalized.
    Creates a .status file to prevent reopening.
    """
    project_name = sanitize_project_name(project_name)
    project_dir = f"{config.PROJECTS_DIR}/{project_name}"
    
    if not os.path.exists(project_dir):
        return "Error: Project not found."
    
    status_file = f"{project_dir}/.status"
    status_data = {
        "status": "closed",
        "closed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "finalized": True
    }
    
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)
    
    return f"✅ Project '{project_name}' marked as closed"


def is_project_closed(project_name):
    """
    Check if a project is closed/finalized.
    Returns: (is_closed: bool, status_data: dict)
    """
    project_name = sanitize_project_name(project_name)
    project_dir = f"{config.PROJECTS_DIR}/{project_name}"
    status_file = f"{project_dir}/.status"
    
    if not os.path.exists(status_file):
        return False, None
    
    try:
        with open(status_file, 'r') as f:
            status_data = json.load(f)
        
        return status_data.get('status') == 'closed', status_data
    except Exception:
        return False, None


def get_project_info(project_name):
    """Get project status information"""
    is_closed, status_data = is_project_closed(project_name)
    
    if is_closed and status_data:
        return f"🔒 CLOSED on {status_data.get('closed_at', 'unknown')}"
    else:
        return "✅ Active"