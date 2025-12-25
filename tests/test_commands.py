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
        mock_context.attack_graph.get_statistics.return_value = {'total_nodes': 10, 'total_edges': 5}
        
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

    @patch("graph.graph_server.is_running", return_value=True)
    @patch("graph.graph_server.update_graph")
    @patch("core.commands.graph.GraphVisualizer")
    def test_graph_success(self, mock_viz_class, mock_update, mock_is_running, mock_context):
        """Test graph command when server already running"""
        # Mock visualizer to avoid NetworkX graph complexity
        mock_viz_instance = Mock()
        mock_viz_instance.render_statistics.return_value = "Stats"
        mock_viz_instance.render_ascii_graph.return_value = "Graph"
        mock_viz_class.return_value = mock_viz_instance
        
        cmd = GraphCommand()
        cmd._server_port = 5050
        result = cmd.execute(mock_context)
        
        assert result is True
        
        assert result is True

    def test_graph_update_no_project(self, mock_context):
        """Test graph update fails without project"""
        mock_context.current_project = None
        
        cmd = GraphCommand()
        result = cmd.update(mock_context)
        
        assert result is False

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
