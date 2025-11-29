"""
Tests for Command Handlers
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from core.commands.sitrep import SitrepCommand
from core.commands.graph import GraphCommand
from core.commands.finalize import FinalizeCommand

class TestCommands:
    """Test suite for command handlers"""
    
    @pytest.fixture
    def mock_context(self):
        """Mock CyberCouncil context"""
        context = Mock()
        context.current_project = "test_project"
        context.attack_graph = Mock()
        context.renderer = Mock()
        context.ollama_client = Mock()
        context.logger = Mock()
        context.logger.pending_logs = []
        return context

    # --- SitRep Tests ---
    def test_sitrep_no_project(self):
        """Test SitRep fails without project"""
        cmd = SitrepCommand()
        context = Mock()
        context.current_project = None
        
        assert cmd.execute(context) is False

    @patch("builtins.open", new_callable=MagicMock)
    def test_sitrep_success(self, mock_open, mock_context):
        """Test successful SitRep generation"""
        # Mock file read
        mock_file = Mock()
        mock_file.read.return_value = "Active Record Content"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock attack graph stats
        mock_context.attack_graph.get_statistics.return_value = {'nodes': 10, 'edges': 5}
        
        # Mock AI response
        mock_context.ollama_client.call_strategist.return_value = "SitRep Summary"
        mock_context.renderer.render.return_value = "Formatted SitRep"
        
        cmd = SitrepCommand()
        assert cmd.execute(mock_context) is True
        
        mock_context.ollama_client.call_strategist.assert_called_once()
        mock_context.renderer.render.assert_called_once_with("SitRep Summary")

    # --- Graph Tests ---
    def test_graph_no_graph(self):
        """Test Graph command fails without initialized graph"""
        cmd = GraphCommand()
        context = Mock()
        context.attack_graph = None
        
        assert cmd.execute(context) is False

    @patch("core.commands.graph.GraphVisualizer")
    def test_graph_success(self, mock_viz, mock_context):
        """Test successful graph visualization"""
        cmd = GraphCommand()
        assert cmd.execute(mock_context) is True
        mock_viz.render_graph.assert_called_once_with(mock_context.attack_graph)

    def test_graph_update(self, mock_context):
        """Test graph update"""
        cmd = GraphCommand()
        assert cmd.update(mock_context) is True
        mock_context.attack_graph.build_from_active_record.assert_called_once()

    # --- Finalize Tests ---
    def test_finalize_no_project(self):
        """Test Finalize fails without project"""
        cmd = FinalizeCommand()
        context = Mock()
        context.current_project = None
        
        assert cmd.execute(context) is False

    @patch("core.commands.finalize.project_status")
    @patch("builtins.open", new_callable=MagicMock)
    @patch("builtins.input")
    def test_finalize_success(self, mock_input, mock_open, mock_status, mock_context):
        """Test successful project finalization"""
        # Mock input (no pending logs commit)
        mock_input.return_value = 'n'
        
        # Mock file operations
        mock_file = Mock()
        mock_file.read.return_value = "Full Log"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock AI
        mock_context.ollama_client.call_strategist.return_value = "Final Report"
        
        cmd = FinalizeCommand()
        assert cmd.execute(mock_context) is True
        
        # Verify report generation
        mock_context.ollama_client.call_strategist.assert_called_once()
        
        # Verify graph export
        mock_context.attack_graph.save_graph.assert_called_once()
        
        # Verify project closed
        mock_status.mark_project_closed.assert_called_once_with("test_project")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
