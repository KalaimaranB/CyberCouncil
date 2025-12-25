"""
Tests for utility functions in tools.py.
Tests project management, sanitization, and file operations.
"""

import pytest
import os
from pathlib import Path
from utils import tools


class TestSanitization:
    """Test project name sanitization"""
    
    def test_sanitize_basic_name(self):
        """Test basic name passes through"""
        result = tools.sanitize_project_name("My_Project")
        assert result == "My_Project"
    
    def test_sanitize_removes_path_traversal(self):
        """Test that path traversal attacks are blocked"""
        result = tools.sanitize_project_name("../../etc/passwd")
        assert ".." not in result
        assert "/" not in result
        assert result == "passwd"
    
    def test_sanitize_removes_special_chars(self):
        """Test removal of filesystem-dangerous characters"""
        result = tools.sanitize_project_name("Bad<>Name:?*")
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert "?" not in result
        assert "*" not in result
    
    def test_sanitize_whitespace(self):
        """Test whitespace handling"""
        result = tools.sanitize_project_name("  Project Name  ")
        assert not result.startswith(" ")
        assert not result.endswith(" ")
    
    def test_sanitize_empty_name(self):
        """Test that empty names get default"""
        result = tools.sanitize_project_name("")
        prefix, _, ts = result.partition("_")
        assert prefix == "project"
        assert ts.isdigit()
    
    def test_sanitize_removes_leading_dots(self):
        """Test dots are stripped"""
        result = tools.sanitize_project_name("...secret")
        assert not result.startswith(".")


class TestProjectOperations:
    """Test project initialization and management"""
    
    def test_init_project_creates_directory(self, tmp_path, mock_config):
        """Test project directory creation"""
        result = tools.init_project("test_project")
        
        assert "initialized" in result
        project_dir = Path(mock_config.PROJECTS_DIR) / "test_project"
        assert project_dir.exists()
    
    def test_init_project_creates_active_record(self, tmp_path, mock_config):
        """Test active_record.md is created"""
        tools.init_project("test_project")
        
        record_file = Path(mock_config.PROJECTS_DIR) / "test_project" / "active_record.md"
        assert record_file.exists()
        
        content = record_file.read_text()
        assert "ENUMERATION" in content
        assert "EXPLOITATION" in content
        assert "POST-EXPLOITATION" in content
    
    def test_init_project_repairs_corrupt_record(self, tmp_path, mock_config):
        """Test that corrupt active records are repaired"""
        # Create project with corrupt record
        project_dir = Path(mock_config.PROJECTS_DIR) / "test_project"
        project_dir.mkdir(parents=True)
        record_file = project_dir / "active_record.md"
        record_file.write_text("Corrupt content without sections")
        
        # Initialize should repair it
        tools.init_project("test_project")
        
        content = record_file.read_text()
        assert "SECTION: ENUMERATION" in content
    
    def test_update_active_record(self, tmp_path, mock_config):
        """Test updating active record with new content"""
        tools.init_project("test_project")
        
        result = tools.update_active_record("test_project", "ENUMERATION", "Test entry")
        
        assert "Updated" in result
        
        record_file = Path(mock_config.PROJECTS_DIR) / "test_project" / "active_record.md"
        content = record_file.read_text()
        assert "Test entry" in content
    
    def test_get_active_record(self, tmp_path, mock_config):
        """Test retrieving active record content"""
        tools.init_project("test_project")
        tools.update_active_record("test_project", "ENUMERATION", "Test data")
        
        content = tools.get_active_record("test_project")
        
        assert "test_project" in content
        assert "Test data" in content

    def test_update_missing_section_error(self, tmp_path, mock_config):
        tools.init_project("test_project")
        result = tools.update_active_record("test_project", "NONEXISTENT", "data")
        assert "Error" in result



class TestBackup:
    """Test backup functionality"""
    
    def test_backup_creates_file(self, tmp_path, mock_config):
        """Test backup file creation"""
        # Create project with content
        tools.init_project("test_project")
        tools.update_active_record("test_project", "ENUMERATION", "Important data")
        
        # Create backup
        result = tools.backup_active_record("test_project")
        
        assert "Backup created" in result
        
        backup_dir = Path(mock_config.PROJECTS_DIR) / "test_project" / "backups"
        assert backup_dir.exists()
        
        backups = list(backup_dir.glob("active_record_*.md"))
        assert len(backups) > 0
    
    def test_backup_limits_count(self, tmp_path, mock_config):
        """Test that old backups are deleted (keeps only 5)"""
        tools.init_project("test_project")
        
        # Create many backups
        for i in range(10):
            tools.backup_active_record("test_project")
        
        backup_dir = Path(mock_config.PROJECTS_DIR) / "test_project" / "backups"
        backups = list(backup_dir.glob("active_record_*.md"))
        
        # Should keep only 5 most recent
        assert len(backups) <= 5

    def test_backup_no_record(self, tmp_path, mock_config):
        os.makedirs(Path(mock_config.PROJECTS_DIR) / "test_project")
        result = tools.backup_active_record("test_project")
        assert "No active record" in result




class TestLessonsLearned:
    """Test lessons learned functionality"""
    
    def test_save_lessons_learned(self, tmp_path, mock_config):
        """Test saving lessons to project and knowledge base"""
        tools.init_project("test_project")
        
        lessons = "# Lessons\nTest lesson content"
        result = tools.save_lessons_learned("test_project", lessons)
        
        assert "saved" in result.lower()
        
        # Check project summary
        summary_file = Path(mock_config.PROJECTS_DIR) / "test_project" / "summary.md"
        assert summary_file.exists()
        assert "Test lesson content" in summary_file.read_text()
        
        # Check knowledge base
        kb_file = Path(mock_config.NOTES_DIR) / "learned" / "test_project_lessons.md"
        assert kb_file.exists()
        assert "Test lesson content" in kb_file.read_text()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

