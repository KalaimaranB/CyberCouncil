"""
Attack Graph Module

Builds a knowledge graph from active_record.md discoveries showing relationships between:
- IPs, hosts, services, ports
- Vulnerabilities and credentials
- Attack paths and access levels

The graph is used for visualization and future GNN-based attack path prediction.
"""

import os
import json
import re
from typing import Dict, List, Tuple, Optional
import networkx as nx
from parsing.discovery_parser import DiscoveryParser
from core import config


class AttackGraph:
    """
    Manages the attack graph for a cybersecurity investigation.
    Parses active_record.md to extract entities and relationships.
    """
    
    def __init__(self, project_name: str):
        """
        Initialize attack graph for a given project.
        
        Args:
            project_name: Name of the project to build graph for
        """
        self.project_name = project_name
        self.graph = nx.DiGraph()  # Directed graph (attacks flow in one direction)
        self.discovery_parser = DiscoveryParser()
        self.graph_file = f"{config.PROJECTS_DIR}/{project_name}/attack_graph.json"
        
        # Load existing graph if available
        if os.path.exists(self.graph_file):
            self.load_from_json()
    
    def parse_active_record(self, active_record_path: str):
        """
        Parse active_record.md and build/update the graph.
        
        Args:
            active_record_path: Path to active_record.md file
        """
        if not os.path.exists(active_record_path):
            print(f"⚠️  Active record not found: {active_record_path}")
            return
        
        with open(active_record_path, 'r') as f:
            content = f.read()
        
        # Parse discoveries from each line
        # active_record.md format:
        # - 🎯 IP [DC]: 10.10.10.5
        # - ✅ Open Port [OPEN]: 445
        # - ⚙️ Service: SMB
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('<!--'):
                continue
            
            # Extract entity from formatted log lines
            self._parse_log_line(line)
        
        # Infer relationships between nodes
        self._infer_relationships()
        
        # Save updated graph
        self.save_to_json()
    
    def _parse_log_line(self, line: str):
        """Extract entities from a single log line and add to graph"""
        
        # IP Address pattern: 🎯 IP [CONTEXT]: 10.10.10.5
        ip_match = re.search(r'🎯 IP.*?:\s*([\d\.]+)', line)
        if ip_match:
            ip = ip_match.group(1)
            context = re.search(r'\[(.*?)\]', line)
            context_str = context.group(1) if context else "DISCOVERED"
            self.add_node(ip, node_type='IP', context=context_str)
            return
        
        # Port pattern: ✅ Open Port [OPEN]: 445
        port_match = re.search(r'(✅|🔌)\s+(?:Open\s+)?Port.*?:\s*(\d+)', line)
        if port_match:
            port = port_match.group(2)
            self.add_node(f"Port_{port}", node_type='PORT', port_number=port)
            return
        
        # Service pattern: ⚙️ Service: SMB
        service_match = re.search(r'⚙️ Service:\s*(\w+)', line)
        if service_match:
            service = service_match.group(1)
            self.add_node(service, node_type='SERVICE')
            return
        
        # Vulnerability pattern: 🚨 Vulnerability: MS17-010
        vuln_match = re.search(r'🚨 Vulnerability:\s*(.+?)(?:\n|$)', line)
        if vuln_match:
            vuln = vuln_match.group(1).strip()
            self.add_node(vuln, node_type='VULNERABILITY', severity='HIGH')
            return
        
        # Credential patterns: 👤 Username, 🔑 Password, 🔐 Hash
        username_match = re.search(r'👤 Username.*?:\s*(\w+)', line)
        if username_match:
            username = username_match.group(1)
            self.add_node(username, node_type='USERNAME')
            return
        
        password_match = re.search(r'🔑 Password.*?:\s*(.+?)(?:\n|$)', line)
        if password_match:
            password = password_match.group(1).strip()
            # Store password hash instead of plaintext in graph
            self.add_node(f"CRED_{hash(password) % 10000}", node_type='CREDENTIAL', cred_type='password')
            return
        
        hash_match = re.search(r'🔐 Hash.*?:\s*([a-fA-F0-9]+)', line)
        if hash_match:
            hash_val = hash_match.group(1)
            self.add_node(f"HASH_{hash_val[:8]}", node_type='CREDENTIAL', cred_type='hash')
            return
        
        # Domain pattern: 🏰 Domain
        domain_match = re.search(r'🏰 Domain.*?:\s*(\S+)', line)
        if domain_match:
            domain = domain_match.group(1)
            self.add_node(domain, node_type='DOMAIN')
            return
    
    def _infer_relationships(self):
        """
        Infer relationships between nodes based on common patterns.
        Example: If we have IP 10.10.10.5, Port_445, and SMB service,
        we can infer: IP --runs--> SMB --on_port--> Port_445
        """
        nodes_by_type = {}
        for node, data in self.graph.nodes(data=True):
            node_type = data.get('type', 'UNKNOWN')
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append(node)
        
        # Rule 1: Connect IPs to Services (if mentioned together in timeline)
        if 'IP' in nodes_by_type and 'SERVICE' in nodes_by_type:
            for ip in nodes_by_type['IP']:
                for service in nodes_by_type['SERVICE']:
                    self.add_edge(ip, service, relationship='runs')
        
        # Rule 2: Connect Services to Ports (common mappings)
        service_port_map = {
            'SMB': ['Port_445', 'Port_139'],
            'HTTP': ['Port_80', 'Port_8080'],
            'HTTPS': ['Port_443'],
            'SSH': ['Port_22'],
            'RDP': ['Port_3389'],
            'Kerberos': ['Port_88'],
            'LDAP': ['Port_389', 'Port_636'],
        }
        
        if 'SERVICE' in nodes_by_type and 'PORT' in nodes_by_type:
            for service in nodes_by_type['SERVICE']:
                if service in service_port_map:
                    for port in service_port_map[service]:
                        if port in nodes_by_type['PORT']:
                            self.add_edge(service, port, relationship='on_port')
        
        # Rule 3: Connect Services to Vulnerabilities
        if 'SERVICE' in nodes_by_type and 'VULNERABILITY' in nodes_by_type:
            for service in nodes_by_type['SERVICE']:
                for vuln in nodes_by_type['VULNERABILITY']:
                    # Check if vuln name mentions the service
                    if service.lower() in vuln.lower():
                        self.add_edge(service, vuln, relationship='has_vuln')
        
        # Rule 4: Connect IPs to Credentials (ownership)
        if 'IP' in nodes_by_type and 'USERNAME' in nodes_by_type:
            for ip in nodes_by_type['IP']:
                for username in nodes_by_type['USERNAME']:
                    self.add_edge(ip, username, relationship='has_account')
        
        # Rule 5: Connect Vulnerabilities to Access (implicit gain)
        if 'VULNERABILITY' in nodes_by_type:
            for vuln in nodes_by_type['VULNERABILITY']:
                # Create access node if vuln exists
                access_node = f"ACCESS_from_{vuln}"
                self.add_node(access_node, node_type='ACCESS', level='SYSTEM')
                self.add_edge(vuln, access_node, relationship='enables')
    
    def add_node(self, node_id: str, node_type: str, **attributes):
        """
        Add a node to the graph.
        
        Args:
            node_id: Unique identifier for the node
            node_type: Type of node (IP, SERVICE, PORT, etc.)
            **attributes: Additional attributes for the node
        """
        self.graph.add_node(node_id, type=node_type, **attributes)
    
    def add_edge(self, source: str, target: str, relationship: str, **attributes):
        """
        Add an edge (relationship) between two nodes.
        
        Args:
            source: Source node ID
            target: Target node ID
            relationship: Type of relationship (runs, has_vuln, etc.)
            **attributes: Additional edge attributes
        """
        self.graph.add_edge(source, target, relationship=relationship, **attributes)
    
    def get_statistics(self) -> Dict[str, int]:
        """Get graph statistics"""
        stats = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
        }
        
        # Count by type
        type_counts = {}
        for node, data in self.graph.nodes(data=True):
            node_type = data.get('type', 'UNKNOWN')
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        
        stats.update(type_counts)
        return stats
    
    def save_to_json(self):
        """Save graph to JSON file"""
        try:
            # Convert NetworkX graph to JSON-serializable format
            data = {
                'nodes': [],
                'edges': []
            }
            
            for node, attrs in self.graph.nodes(data=True):
                data['nodes'].append({
                    'id': node,
                    **attrs
                })
            
            for source, target, attrs in self.graph.edges(data=True):
                data['edges'].append({
                    'source': source,
                    'target': target,
                    **attrs
                })
            
            with open(self.graph_file, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            print(f"⚠️  Error saving graph: {e}")
    
    def load_from_json(self):
        """Load graph from JSON file"""
        try:
            with open(self.graph_file, 'r') as f:
                data = json.load(f)
            
            # Clear existing graph
            self.graph.clear()
            
            # Reconstruct nodes
            for node_data in data.get('nodes', []):
                node_id = node_data.pop('id')
                self.graph.add_node(node_id, **node_data)
            
            # Reconstruct edges
            for edge_data in data.get('edges', []):
                source = edge_data.pop('source')
                target = edge_data.pop('target')
                self.graph.add_edge(source, target, **edge_data)
                
        except Exception as e:
            print(f"⚠️  Error loading graph: {e}")
    
    def get_nodes_by_type(self, node_type: str) -> List[str]:
        """Get all nodes of a specific type"""
        return [node for node, data in self.graph.nodes(data=True) 
                if data.get('type') == node_type]
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get all neighbors of a node"""
        if node_id in self.graph:
            return list(self.graph.neighbors(node_id))
        return []
