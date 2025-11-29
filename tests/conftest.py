"""
Test configuration for CyberCouncil test suite.
Provides fixtures and common utilities for all tests.
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory for testing"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create active_record.md
    active_record = project_dir / "active_record.md"
    active_record.write_text("""# Active Investigation Record: test_project

<!-- SECTION: ENUMERATION -->

<!-- SECTION: EXPLOITATION -->

<!-- SECTION: POST-EXPLOITATION -->
""")
    
    return project_dir


@pytest.fixture
def sample_active_record(tmp_path):
    """Create a sample active_record.md with test data"""
    record_file = tmp_path / "active_record.md"
    record_file.write_text("""# Active Investigation Record: test_project

<!-- SECTION: ENUMERATION -->
- 🎯 IP [DOMAIN_CONTROLLER]: 10.10.10.5
- ✅ Open Port [OPEN]: 445
- ✅ Open Port [OPEN]: 88
- ⚙️ Service: SMB
- ⚙️ Service: Kerberos
- 🏰 Domain: CORP

<!-- SECTION: EXPLOITATION -->
- 🚨 Vulnerability: MS17-010
- 👤 Username [CREDENTIAL]: administrator
- 🔑 Password [CREDENTIAL]: Admin123!

<!-- SECTION: POST-EXPLOITATION -->
""")
    
    return record_file


@pytest.fixture
def mock_config(monkeypatch, tmp_path):
    """Mock config module for testing"""
    from core import config
    
    # Create temporary directories
    projects_dir = tmp_path / "projects"
    notes_dir = tmp_path / "notes"
    db_dir = tmp_path / "chroma_db"
    
    projects_dir.mkdir()
    notes_dir.mkdir()
    db_dir.mkdir()
    
    # Patch config values
    monkeypatch.setattr(config, 'PROJECTS_DIR', str(projects_dir))
    monkeypatch.setattr(config, 'NOTES_DIR', str(notes_dir))
    monkeypatch.setattr(config, 'DB_DIR', str(db_dir))
    
    return config
