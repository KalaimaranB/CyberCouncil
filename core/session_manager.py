"""
Session Manager Module

Handles project selection, mode management, and session state.
Separates project management concerns from AI orchestration.
"""

import os
from typing import List, Optional, Tuple
from core import config
from utils import project_status, tools
from graph.attack_graph import AttackGraph


class SessionManager:
    """
    Manages session state including current project and context mode.
    """
    
    def __init__(self):
        """Initialize session manager."""
        self.current_project: Optional[str] = None
        self.context_mode: str = "GENERAL"
        self.attack_graph: Optional[AttackGraph] = None
    
    def list_recent_projects(self) -> List[str]:
        """
        Returns the top 5 most recently modified project folders.
        
        Returns:
            List of project names (most recent first)
        """
        if not os.path.exists(config.PROJECTS_DIR):
            os.makedirs(config.PROJECTS_DIR)
            return []
        
        try:
            # Get all subdirectories in projects/
            projects = [f.path for f in os.scandir(config.PROJECTS_DIR) if f.is_dir()]
            
            # Prevent race conditions during modification time check
            valid_projects = []
            for p in projects:
                try:
                    mtime = os.path.getmtime(p)
                    valid_projects.append((p, mtime))
                except (FileNotFoundError, OSError) as e:
                    # Project was deleted or modified during scan
                    print(f"⚠️  Skipping {os.path.basename(p)}: {e}")
                    continue
            
            # Sort by modification time (newest first)
            valid_projects.sort(key=lambda x: x[1], reverse=True)
            
            # Return just the folder names (top 5)
            return [os.path.basename(p[0]) for p in valid_projects[:config.RECENT_PROJECTS_COUNT]]
        except Exception as e:
            print(f"Error scanning projects: {e}")
            return []
    
    def search_projects(self, query: str) -> List[str]:
        """
        Search for projects containing the query string.
        
        Args:
            query: Search term
            
        Returns:
            List of matching project names
        """
        if not os.path.exists(config.PROJECTS_DIR):
            return []
        
        projects = [f.name for f in os.scandir(config.PROJECTS_DIR) if f.is_dir()]
        matches = [p for p in projects if query.lower() in p.lower()]
        return matches
    
    def is_project_closed(self) -> Tuple[bool, dict]:
        """
        Check if current project is closed.
        
        Returns:
            Tuple of (is_closed, status_data)
        """
        if not self.current_project:
            return False, {}
        
        return project_status.is_project_closed(self.current_project)
    
    def initialize_project(self, project_name: str):
        """
        Initialize a project (set as current, load attack graph).
        
        Args:
            project_name: Name of project to initialize
        """
        self.current_project = project_name
        self.context_mode = "PROJECT"
        self.attack_graph = AttackGraph(project_name)
        print("🧠 Attack graph initialized")
    
    def set_mode(self, mode: str):
        """
        Set context mode.
        
        Args:
            mode: "PROJECT" or "GENERAL"
        """
        self.context_mode = mode
    
    def create_new_project(self, name: str) -> str:
        """
        Create a new project.
        
        Args:
            name: Project name
            
        Returns:
            Sanitized project name
        """
        result = tools.init_project(name)
        print(result)
        return tools.sanitize_project_name(name)
