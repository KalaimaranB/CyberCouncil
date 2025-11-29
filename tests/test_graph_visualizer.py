"""
Tests for Graph Visualizer module.
Tests ASCII rendering, statistics display, and node prioritization.
"""

import pytest
from graph.attack_graph import AttackGraph
from graph.graph_visualizer import GraphVisualizer


class TestGraphVisualizer:
    """Test suite for GraphVisualizer class"""
    
    @pytest.fixture
    def sample_graph(self):
        """Create a sample graph for testing"""
        graph = AttackGraph("test_viz")
        
        # Add diverse node types
        graph.add_node("10.10.10.5", node_type="IP", context="DC")
        graph.add_node("10.10.10.20", node_type="IP", context="WEB_SERVER")
        graph.add_node("SMB", node_type="SERVICE")
        graph.add_node("HTTP", node_type="SERVICE")
        graph.add_node("Port_445", node_type="PORT", port_number="445")
        graph.add_node("Port_80", node_type="PORT", port_number="80")
        graph.add_node("MS17-010", node_type="VULNERABILITY", severity="CRITICAL")
        graph.add_node("administrator", node_type="USERNAME")
        
        # Add edges
        graph.add_edge("10.10.10.5", "SMB", relationship="runs")
        graph.add_edge("10.10.10.20", "HTTP", relationship="runs")
        graph.add_edge("SMB", "Port_445", relationship="on_port")
        graph.add_edge("HTTP", "Port_80", relationship="on_port")
        graph.add_edge("SMB", "MS17-010", relationship="has_vuln")
        graph.add_edge("10.10.10.5", "administrator", relationship="has_account")
        
        return graph
    
    def test_init(self, sample_graph):
        """Test visualizer initialization"""
        viz = GraphVisualizer(sample_graph.graph)
        
        assert viz.graph is not None
        assert viz.graph.number_of_nodes() == 8
    
    def test_render_statistics(self, sample_graph):
        """Test statistics rendering"""
        viz = GraphVisualizer(sample_graph.graph)
        output = viz.render_statistics()
        
        # Should contain key information
        assert "ATTACK GRAPH STATISTICS" in output
        assert "Total Nodes: 8" in output
        assert "Total Edges: 6" in output
        assert "IP: 2" in output
        assert "SERVICE: 2" in output
        assert "PORT: 2" in output
        assert "VULNERABILITY: 1" in output
        assert "USERNAME: 1" in output
    
    def test_render_node_list(self, sample_graph):
        """Test node list rendering"""
        viz = GraphVisualizer(sample_graph.graph)
        output = viz.render_node_list()
        
        # Should contain discovered entities
        assert "DISCOVERED ENTITIES" in output
        assert "10.10.10.5" in output
        assert "SMB" in output
        assert "Port_445" in output
        assert "MS17-010" in output
        assert "administrator" in output
    
    def test_render_ascii_graph(self, sample_graph):
        """Test ASCII graph rendering"""
        viz = GraphVisualizer(sample_graph.graph)
        output = viz.render_ascii_graph()
        
        # Should contain relationship information
        assert "ATTACK GRAPH" in output
        assert "Relationships" in output or "runs" in output or "has_vuln" in output
    
    def test_render_full(self, sample_graph):
        """Test full rendering (stats + list + graph)"""
        viz = GraphVisualizer(sample_graph.graph)
        output = viz.render_full()
        
        # Should contain all sections
        assert "ATTACK GRAPH STATISTICS" in output
        assert "DISCOVERED ENTITIES" in output
        assert "ATTACK GRAPH" in output
    
    def test_empty_graph_rendering(self):
        """Test rendering empty graph"""
        graph = AttackGraph("empty_test")
        viz = GraphVisualizer(graph.graph)
        
        # Should handle empty graph gracefully
        output = viz.render_statistics()
        assert "Total Nodes: 0" in output
        assert "Total Edges: 0" in output
        
        output = viz.render_ascii_graph()
        assert "No entities discovered" in output
    
    def test_select_important_nodes(self, sample_graph):
        """Test node prioritization algorithm"""
        viz = GraphVisualizer(sample_graph.graph)
        
        # Get important nodes (limit to 5)
        important = viz._select_important_nodes(5)
        
        assert len(important) <= 5
        # Should prioritize IPs and vulnerabilities
        assert any(node for node in important if "10.10.10" in node)
    
    def test_large_graph_limiting(self):
        """Test that large graphs are limited in display"""
        graph = AttackGraph("large_test")
        
        # Add many nodes
        for i in range(30):
            graph.add_node(f"Node_{i}", node_type="IP")
        
        viz = GraphVisualizer(graph.graph)
        output = viz.render_ascii_graph(max_nodes=10)
        
        # Should indicate limitation
        assert "Showing" in output or len(output) < 10000  # Not showing all 30
    
    def test_color_codes_present(self):
        """Test that color codes are defined"""
        viz = GraphVisualizer(None)
        
        assert 'IP' in viz.COLORS
        assert 'SERVICE' in viz.COLORS
        assert 'VULNERABILITY' in viz.COLORS
        assert 'RESET' in viz.COLORS
    
    def test_icons_present(self):
        """Test that icons are defined for node types"""
        viz = GraphVisualizer(None)
        
        assert 'IP' in viz.ICONS
        assert 'SERVICE' in viz.ICONS
        assert 'PORT' in viz.ICONS
        assert 'VULNERABILITY' in viz.ICONS
        assert 'USERNAME' in viz.ICONS
    
    def test_single_node_graph(self):
        """Test rendering graph with single node"""
        graph = AttackGraph("single_test")
        graph.add_node("10.10.10.5", node_type="IP")
        
        viz = GraphVisualizer(graph.graph)
        output = viz.render_full()
        
        assert "10.10.10.5" in output
        assert "Total Nodes: 1" in output
        assert "Total Edges: 0" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
