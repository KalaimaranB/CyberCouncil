"""
Tests for Session Manager module.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch
from core.session_manager import SessionManager


class TestSessionManager:
    """Test suite for SessionManager class"""
    
    @pytest.fixture
    def manager(self):
        """Create a SessionManager instance"""
        return SessionManager()
    
    def test_init(self, manager):
        """Test session manager initialization"""
        assert manager.current_project is None
        assert manager.context_mode == "GENERAL"
        assert manager.attack_graph is None
    
    def test_list_recent_projects(self, manager, tmp_path, monkeypatch):
        """Test listing recent projects"""
        # Create projects directory with test projects
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        
        # Create test project directories
        (projects_dir / "project1").mkdir()
        (projects_dir / "project2").mkdir()
        
        monkeypatch.setattr('core.config.PROJECTS_DIR', str(projects_dir))
        monkeypatch.setattr('core.config.RECENT_PROJECTS_COUNT', 5)
        
        projects = manager.list_recent_projects()
        
        assert len(projects) == 2
        assert "project1" in projects
        assert "project2" in projects
    
    def test_list_recent_projects_empty(self, manager, tmp_path, monkeypatch):
        """Test listing projects when directory is empty"""
        projects_dir = tmp_path / "empty_projects"
        monkeypatch.setattr('core.config.PROJECTS_DIR', str(projects_dir))
        
        projects = manager.list_recent_projects()
        
        assert projects == []
        assert projects_dir.exists()  # Should create directory
    
    def test_search_projects(self, manager, tmp_path, monkeypatch):
        """Test project search"""
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        
        (projects_dir / "htb_machine1").mkdir()
        (projects_dir / "htb_machine2").mkdir()
        (projects_dir / "thm_room1").mkdir()
        
        monkeypatch.setattr('core.config.PROJECTS_DIR', str(projects_dir))
        
        matches = manager.search_projects("htb")
        
        assert len(matches) == 2
        assert "htb_machine1" in matches
        assert "htb_machine2" in matches
        assert "thm_room1" not in matches
    
    def test_search_projects_case_insensitive(self, manager, tmp_path, monkeypatch):
        """Test project search is case-insensitive"""
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        
        (projects_dir / "MyProject").mkdir()
        
        monkeypatch.setattr('core.config.PROJECTS_DIR', str(projects_dir))
        
        matches = manager.search_projects("myproject")
        
        assert len(matches) == 1
        assert "MyProject" in matches
    
    def test_search_projects_no_directory(self, manager, tmp_path, monkeypatch):
        """Test search when projects directory doesn't exist"""
        monkeypatch.setattr('core.config.PROJECTS_DIR', str(tmp_path / "nonexistent"))
        
        matches = manager.search_projects("test")
        
        assert matches == []
    
    @patch('core.session_manager.project_status.is_project_closed')
    def test_is_project_closed(self, mock_is_closed, manager):
        """Test checking if project is closed"""
        manager.current_project = "test_project"
        mock_is_closed.return_value = (True, {'closed_at': '2024-01-01'})
        
        is_closed, data = manager.is_project_closed()
        
        assert is_closed is True
        assert 'closed_at' in data
        mock_is_closed.assert_called_once_with("test_project")
    
    def test_is_project_closed_no_project(self, manager):
        """Test is_project_closed when no project is set"""
        is_closed, data = manager.is_project_closed()
        
        assert is_closed is False
        assert data == {}
    
    @patch('core.session_manager.AttackGraph')
    def test_initialize_project(self, mock_attack_graph, manager):
        """Test project initialization"""
        manager.initialize_project("test_project")
        
        assert manager.current_project == "test_project"
        assert manager.context_mode == "PROJECT"
        mock_attack_graph.assert_called_once_with("test_project")
    
    def test_set_mode(self, manager):
        """Test setting context mode"""
        manager.set_mode("PROJECT")
        assert manager.context_mode == "PROJECT"
        
        manager.set_mode("GENERAL")
        assert manager.context_mode == "GENERAL"
    
    @patch('core.session_manager.tools.init_project')
    @patch('core.session_manager.tools.sanitize_project_name')
    def test_create_new_project(self, mock_sanitize, mock_init, manager):
        """Test creating a new project"""
        mock_init.return_value = "✅ Project created"
        mock_sanitize.return_value = "sanitized_name"
        
        result = manager.create_new_project("Test Project!")
        
        assert result == "sanitized_name"
        mock_init.assert_called_once_with("Test Project!")
        mock_sanitize.assert_called_once_with("Test Project!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
