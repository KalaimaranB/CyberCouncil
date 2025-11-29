"""
Tests for Attack Graph module.
Tests entity extraction, relationship inference, and graph persistence.
"""

import pytest
import json
from pathlib import Path
from graph.attack_graph import AttackGraph


class TestAttackGraph:
    """Test suite for AttackGraph class"""
    
    def test_init(self, tmp_path, mock_config):
        """Test graph initialization"""
        # Create project directory
        project_dir = tmp_path / "projects" / "test_project"
        project_dir.mkdir(parents=True)
        
        graph = AttackGraph("test_project")
        
        assert graph.project_name == "test_project"
        assert graph.graph.number_of_nodes() == 0
        assert graph.graph.number_of_edges() == 0
    
    def test_add_node(self):
        """Test adding nodes to graph"""
        graph = AttackGraph("test_project")
        
        graph.add_node("10.10.10.5", node_type="IP", context="DC")
        
        assert graph.graph.number_of_nodes() == 1
        assert "10.10.10.5" in graph.graph.nodes()
        assert graph.graph.nodes["10.10.10.5"]["type"] == "IP"
        assert graph.graph.nodes["10.10.10.5"]["context"] == "DC"
    
    def test_add_edge(self):
        """Test adding edges to graph"""
        graph = AttackGraph("test_project")
        
        graph.add_node("10.10.10.5", node_type="IP")
        graph.add_node("SMB", node_type="SERVICE")
        graph.add_edge("10.10.10.5", "SMB", relationship="runs")
        
        assert graph.graph.number_of_edges() == 1
        assert graph.graph.has_edge("10.10.10.5", "SMB")
        assert graph.graph.edges["10.10.10.5", "SMB"]["relationship"] == "runs"
    
    def test_parse_ip_address(self, sample_active_record):
        """Test parsing IP addresses from active_record.md"""
        graph = AttackGraph("test_project")
        graph.parse_active_record(str(sample_active_record))
        
        # Should have extracted IP
        ips = graph.get_nodes_by_type("IP")
        assert len(ips) > 0
        assert "10.10.10.5" in ips
    
    def test_parse_service(self, sample_active_record):
        """Test parsing services from active_record.md"""
        graph = AttackGraph("test_project")
        graph.parse_active_record(str(sample_active_record))
        
        # Should have extracted services
        services = graph.get_nodes_by_type("SERVICE")
        assert "SMB" in services or "Kerberos" in services
    
    def test_parse_port(self, sample_active_record):
        """Test parsing ports from active_record.md"""
        graph = AttackGraph("test_project")
        graph.parse_active_record(str(sample_active_record))
        
        # Should have extracted ports
        ports = graph.get_nodes_by_type("PORT")
        assert "Port_445" in ports or "Port_88" in ports
    
    def test_parse_vulnerability(self, sample_active_record):
        """Test parsing vulnerabilities from active_record.md"""
        graph = AttackGraph("test_project")
        graph.parse_active_record(str(sample_active_record))
        
        # Should have extracted vulnerability
        vulns = graph.get_nodes_by_type("VULNERABILITY")
        assert "MS17-010" in vulns
    
    def test_relationship_inference(self):
        """Test automatic relationship inference"""
        graph = AttackGraph("test_project")
        
        # Add nodes
        graph.add_node("10.10.10.5", node_type="IP")
        graph.add_node("SMB", node_type="SERVICE")
        graph.add_node("Port_445", node_type="PORT", port_number="445")
        
        # Run inference
        graph._infer_relationships()
        
        # Should have inferred relationships
        assert graph.graph.number_of_edges() > 0
        
        # SMB should be connected to Port_445
        neighbors = graph.get_neighbors("SMB")
        assert "Port_445" in neighbors or len(neighbors) > 0
    
    def test_get_statistics(self):
        """Test statistics generation"""
        graph = AttackGraph("test_project")
        
        graph.add_node("10.10.10.5", node_type="IP")
        graph.add_node("SMB", node_type="SERVICE")
        graph.add_edge("10.10.10.5", "SMB", relationship="runs")
        
        stats = graph.get_statistics()
        
        assert stats["total_nodes"] == 2
        assert stats["total_edges"] == 1
        assert stats["IP"] == 1
        assert stats["SERVICE"] == 1
    
    def test_save_and_load_json(self, tmp_path, mock_config):
        """Test graph persistence to/from JSON"""
        # Create project directory
        project_dir = tmp_path / "projects" / "test_project"
        project_dir.mkdir(parents=True)
        
        # Create and populate graph
        graph1 = AttackGraph("test_project")
        graph1.add_node("10.10.10.5", node_type="IP", context="DC")
        graph1.add_node("SMB", node_type="SERVICE")
        graph1.add_edge("10.10.10.5", "SMB", relationship="runs")
        
        # Save
        graph1.save_to_json()
        
        # Load into new graph
        graph2 = AttackGraph("test_project")
        
        # Should have same structure
        assert graph2.graph.number_of_nodes() == 2
        assert graph2.graph.number_of_edges() == 1
        assert "10.10.10.5" in graph2.graph.nodes()
        assert graph2.graph.nodes["10.10.10.5"]["type"] == "IP"
    
    def test_get_nodes_by_type(self):
        """Test filtering nodes by type"""
        graph = AttackGraph("test_project")
        
        graph.add_node("10.10.10.5", node_type="IP")
        graph.add_node("10.10.10.20", node_type="IP")
        graph.add_node("SMB", node_type="SERVICE")
        
        ips = graph.get_nodes_by_type("IP")
        services = graph.get_nodes_by_type("SERVICE")
        ports = graph.get_nodes_by_type("PORT")
        
        assert len(ips) == 2
        assert len(services) == 1
        assert len(ports) == 0
        assert "10.10.10.5" in ips
        assert "10.10.10.20" in ips
        assert "SMB" in services
    
    def test_get_neighbors(self):
        """Test getting node neighbors"""
        graph = AttackGraph("test_project")
        
        graph.add_node("10.10.10.5", node_type="IP")
        graph.add_node("SMB", node_type="SERVICE")
        graph.add_node("HTTP", node_type="SERVICE")
        graph.add_edge("10.10.10.5", "SMB", relationship="runs")
        graph.add_edge("10.10.10.5", "HTTP", relationship="runs")
        
        neighbors = graph.get_neighbors("10.10.10.5")
        
        assert len(neighbors) == 2
        assert "SMB" in neighbors
        assert "HTTP" in neighbors
    
    def test_empty_graph_statistics(self):
        """Test statistics on empty graph"""
        graph = AttackGraph("test_project")
        stats = graph.get_statistics()
        
        assert stats["total_nodes"] == 0
        assert stats["total_edges"] == 0
    
    def test_service_port_mapping(self):
        """Test that service-to-port mappings are correctly inferred"""
        graph = AttackGraph("test_project")
        
        # Add service and its standard port
        graph.add_node("SMB", node_type="SERVICE")
        graph.add_node("Port_445", node_type="PORT", port_number="445")
        graph.add_node("HTTP", node_type="SERVICE")
        graph.add_node("Port_80", node_type="PORT", port_number="80")
        
        # Run inference
        graph._infer_relationships()
        
        # Check SMB -> Port_445
        smb_neighbors = graph.get_neighbors("SMB")
        assert "Port_445" in smb_neighbors
        
        # Check HTTP -> Port_80
        http_neighbors = graph.get_neighbors("HTTP")
        assert "Port_80" in http_neighbors


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
