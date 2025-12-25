"""
Tests for Graph Server module.
Tests API endpoints and Cytoscape format conversion.
"""

import pytest
import json
from graph.attack_graph import AttackGraph
from graph.graph_server import create_app


@pytest.fixture
def sample_graph():
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


@pytest.fixture
def empty_graph():
    """Create an empty graph for testing"""
    return AttackGraph("empty_test")


@pytest.fixture
def client(sample_graph):
    """Create test client for Flask app"""
    app = create_app(sample_graph)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def empty_client(empty_graph):
    """Create test client with empty graph"""
    app = create_app(empty_graph)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestCytoscapeFormat:
    """Test Cytoscape.js format conversion"""
    
    def test_to_cytoscape_format_returns_dict(self, sample_graph):
        """Test that to_cytoscape_format returns a dict"""
        result = sample_graph.to_cytoscape_format()
        assert isinstance(result, dict)
        assert 'elements' in result
        assert 'stats' in result
    
    def test_cytoscape_format_nodes(self, sample_graph):
        """Test that nodes have correct Cytoscape structure"""
        result = sample_graph.to_cytoscape_format()
        nodes = [e for e in result['elements'] if 'source' not in e.get('data', {})]
        
        assert len(nodes) == 8
        
        # Check node structure
        for node in nodes:
            assert 'data' in node
            assert 'id' in node['data']
            assert 'label' in node['data']
            assert 'type' in node['data']
            assert 'color' in node['data']
            assert 'classes' in node
    
    def test_cytoscape_format_edges(self, sample_graph):
        """Test that edges have correct Cytoscape structure"""
        result = sample_graph.to_cytoscape_format()
        edges = [e for e in result['elements'] if 'source' in e.get('data', {})]
        
        assert len(edges) == 6
        
        # Check edge structure
        for edge in edges:
            assert 'data' in edge
            assert 'id' in edge['data']
            assert 'source' in edge['data']
            assert 'target' in edge['data']
            assert 'label' in edge['data']
            assert 'relationship' in edge['data']
    
    def test_cytoscape_format_empty_graph(self, empty_graph):
        """Test Cytoscape format with empty graph"""
        result = empty_graph.to_cytoscape_format()
        
        assert result['elements'] == []
        assert result['stats']['total_nodes'] == 0
        assert result['stats']['total_edges'] == 0
    
    def test_node_colors_assigned(self, sample_graph):
        """Test that node colors are properly assigned"""
        result = sample_graph.to_cytoscape_format()
        nodes = [e for e in result['elements'] if 'source' not in e.get('data', {})]
        
        # IP should be blue
        ip_node = next(n for n in nodes if n['data']['type'] == 'IP')
        assert ip_node['data']['color'] == '#3B82F6'
        
        # Vulnerability should be red
        vuln_node = next(n for n in nodes if n['data']['type'] == 'VULNERABILITY')
        assert vuln_node['data']['color'] == '#EF4444'


class TestGraphAPI:
    """Test Graph Server API endpoints"""
    
    def test_index_returns_html(self, client):
        """Test that index route returns HTML"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data or b'CyberCouncil' in response.data
    
    def test_graph_api_returns_json(self, client):
        """Test that /api/graph returns valid JSON"""
        response = client.get('/api/graph')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert 'elements' in data
        assert 'stats' in data
    
    def test_graph_api_has_nodes_and_edges(self, client):
        """Test that /api/graph contains expected data"""
        response = client.get('/api/graph')
        data = json.loads(response.data)
        
        # Should have 8 nodes and 6 edges = 14 elements
        assert len(data['elements']) == 14
        assert data['stats']['total_nodes'] == 8
        assert data['stats']['total_edges'] == 6
    
    def test_stats_api_returns_json(self, client):
        """Test that /api/stats returns valid JSON"""
        response = client.get('/api/stats')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert 'total_nodes' in data
        assert 'total_edges' in data
    
    def test_empty_graph_api(self, empty_client):
        """Test API with empty graph"""
        response = empty_client.get('/api/graph')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['elements'] == []
        assert data['stats']['total_nodes'] == 0


class TestGraphAPIWithNone:
    """Test API when no graph is provided"""
    
    @pytest.fixture
    def none_client(self):
        """Create test client with no graph"""
        app = create_app(None)
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_graph_api_with_none(self, none_client):
        """Test /api/graph handles None graph gracefully"""
        response = none_client.get('/api/graph')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['elements'] == []
        assert data['stats']['total_nodes'] == 0
    
    def test_stats_api_with_none(self, none_client):
        """Test /api/stats handles None graph gracefully"""
        response = none_client.get('/api/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['total_nodes'] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
