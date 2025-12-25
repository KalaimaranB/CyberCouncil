#!/usr/bin/env python3
"""
Quick test script to launch the graph visualization with sample data.
Run this to verify the web UI works correctly.
"""

import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.attack_graph import AttackGraph
from graph import graph_server

def create_sample_graph():
    """Create a realistic sample attack graph"""
    graph = AttackGraph("demo_project")
    
    # Target IPs
    graph.add_node("10.10.10.5", node_type="IP", context="DOMAIN_CONTROLLER")
    graph.add_node("10.10.10.20", node_type="IP", context="WEB_SERVER")
    graph.add_node("10.10.10.100", node_type="IP", context="WORKSTATION")
    
    # Services
    graph.add_node("SMB", node_type="SERVICE")
    graph.add_node("Kerberos", node_type="SERVICE")
    graph.add_node("HTTP", node_type="SERVICE")
    graph.add_node("SSH", node_type="SERVICE")
    graph.add_node("LDAP", node_type="SERVICE")
    
    # Ports
    graph.add_node("Port_445", node_type="PORT", port_number="445")
    graph.add_node("Port_88", node_type="PORT", port_number="88")
    graph.add_node("Port_80", node_type="PORT", port_number="80")
    graph.add_node("Port_22", node_type="PORT", port_number="22")
    graph.add_node("Port_389", node_type="PORT", port_number="389")
    
    # Vulnerabilities
    graph.add_node("MS17-010", node_type="VULNERABILITY", severity="CRITICAL")
    graph.add_node("CVE-2021-44228", node_type="VULNERABILITY", severity="CRITICAL")
    graph.add_node("CVE-2020-1472", node_type="VULNERABILITY", severity="HIGH")
    
    # Credentials
    graph.add_node("administrator", node_type="USERNAME")
    graph.add_node("svc_backup", node_type="USERNAME")
    graph.add_node("CRED_9281", node_type="CREDENTIAL", cred_type="password")
    graph.add_node("HASH_a1b2c3d4", node_type="CREDENTIAL", cred_type="hash")
    
    # Domain
    graph.add_node("CORP.LOCAL", node_type="DOMAIN")
    
    # Access nodes
    graph.add_node("ACCESS_SYSTEM", node_type="ACCESS", level="SYSTEM")
    
    # Relationships
    graph.add_edge("10.10.10.5", "SMB", relationship="runs")
    graph.add_edge("10.10.10.5", "Kerberos", relationship="runs")
    graph.add_edge("10.10.10.5", "LDAP", relationship="runs")
    graph.add_edge("10.10.10.20", "HTTP", relationship="runs")
    graph.add_edge("10.10.10.100", "SSH", relationship="runs")
    
    graph.add_edge("SMB", "Port_445", relationship="on_port")
    graph.add_edge("Kerberos", "Port_88", relationship="on_port")
    graph.add_edge("HTTP", "Port_80", relationship="on_port")
    graph.add_edge("SSH", "Port_22", relationship="on_port")
    graph.add_edge("LDAP", "Port_389", relationship="on_port")
    
    graph.add_edge("SMB", "MS17-010", relationship="has_vuln")
    graph.add_edge("HTTP", "CVE-2021-44228", relationship="has_vuln")
    graph.add_edge("LDAP", "CVE-2020-1472", relationship="has_vuln")
    
    graph.add_edge("10.10.10.5", "administrator", relationship="has_account")
    graph.add_edge("10.10.10.5", "svc_backup", relationship="has_account")
    graph.add_edge("10.10.10.5", "CORP.LOCAL", relationship="member_of")
    
    graph.add_edge("MS17-010", "ACCESS_SYSTEM", relationship="enables")
    graph.add_edge("CVE-2020-1472", "ACCESS_SYSTEM", relationship="enables")
    
    graph.add_edge("administrator", "CRED_9281", relationship="has_cred")
    graph.add_edge("svc_backup", "HASH_a1b2c3d4", relationship="has_cred")
    
    return graph


if __name__ == "__main__":
    print("🧠 CyberCouncil Graph Visualization Test")
    print("=" * 50)
    
    # Create sample graph
    graph = create_sample_graph()
    stats = graph.get_statistics()
    print(f"Created sample graph with {stats['total_nodes']} nodes and {stats['total_edges']} edges")
    
    # Start server
    print("\n🌐 Starting visualization server...")
    print("Press Ctrl+C to stop the server\n")
    
    port = graph_server.start_server(graph, open_browser=True)
    
    if port:
        print(f"Server running at http://localhost:{port}")
        print("\nTest the following features:")
        print("  1. Pan/zoom with mouse")
        print("  2. Click nodes to see details")
        print("  3. Use the path finder (source: 10.10.10.5, target: ACCESS_SYSTEM)")
        print("  4. Toggle filters on the left sidebar")
        print("  5. Change layout using the dropdown")
        print("  6. Export as PNG or JSON")
        
        try:
            # Keep running until interrupted
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n💀 Server stopped.")
