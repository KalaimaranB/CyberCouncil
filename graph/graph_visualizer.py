"""
Graph Visualizer Module

Converts NetworkX attack graphs into ASCII art for terminal display.
Provides statistics and visual representation of the attack surface.
"""

from typing import Dict, List
import networkx as nx


class GraphVisualizer:
    """Renders attack graphs as ASCII art for terminal display"""
    
    # Color codes for terminal output
    COLORS = {
        'IP': '\033[94m',          # Blue
        'SERVICE': '\033[92m',      # Green
        'PORT': '\033[93m',         # Yellow
        'VULNERABILITY': '\033[91m', # Red
        'CREDENTIAL': '\033[95m',   # Magenta
        'USERNAME': '\033[96m',     # Cyan
        'DOMAIN': '\033[97m',       # White
        'ACCESS': '\033[92m',       # Bright green
        'RESET': '\033[0m',         # Reset
    }
    
    # Icons for node types
    ICONS = {
        'IP': '🎯',
        'SERVICE': '⚙️',
        'PORT': '🔌',
        'VULNERABILITY': '🚨',
        'CREDENTIAL': '🔑',
        'USERNAME': '👤',
        'DOMAIN': '🏰',
        'ACCESS': '✅',
    }
    
    def __init__(self, graph: nx.DiGraph):
        """
        Initialize visualizer with a graph.
        
        Args:
            graph: NetworkX DiGraph to visualize
        """
        self.graph = graph
    
    def render_statistics(self) -> str:
        """
        Render graph statistics.
        
        Returns:
            Formatted statistics string
        """
        output = []
        output.append("\n📊 ATTACK GRAPH STATISTICS")
        output.append("━" * 60)
        
        # Total counts
        output.append(f"Total Nodes: {self.graph.number_of_nodes()}")
        output.append(f"Total Edges: {self.graph.number_of_edges()}")
        output.append("")
        
        # Count by type
        type_counts = {}
        for node, data in self.graph.nodes(data=True):
            node_type = data.get('type', 'UNKNOWN')
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        
        output.append("Breakdown by Type:")
        for node_type, count in sorted(type_counts.items()):
            icon = self.ICONS.get(node_type, '📍')
            output.append(f"  {icon} {node_type}: {count}")
        
        output.append("━" * 60)
        return "\n".join(output)
    
    def render_node_list(self) -> str:
        """
        Render a simple list view of all nodes grouped by type.
        
        Returns:
            Formatted node list string
        """
        output = []
        output.append("\n🗂️  DISCOVERED ENTITIES")
        output.append("━" * 60)
        
        # Group nodes by type
        nodes_by_type = {}
        for node, data in self.graph.nodes(data=True):
            node_type = data.get('type', 'UNKNOWN')
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append((node, data))
        
        # Display each type
        for node_type in sorted(nodes_by_type.keys()):
            icon = self.ICONS.get(node_type, '📍')
            color = self.COLORS.get(node_type, '')
            reset = self.COLORS['RESET']
            
            output.append(f"\n{icon} {node_type}:")
            for node, data in nodes_by_type[node_type]:
                # Add context if available
                context =  data.get('context', '')
                if context:
                    output.append(f"  {color}├─ {node}{reset} [{context}]")
                else:
                    output.append(f"  {color}├─ {node}{reset}")
        
        output.append("\n" + "━" * 60)
        return "\n".join(output)
    
    def render_ascii_graph(self, max_nodes: int = 20) -> str:
        """
        Render graph as ASCII art showing relationships.
        Limited to prevent overwhelming output.
        
        Args:
            max_nodes: Maximum number of nodes to display
            
        Returns:
            ASCII art representation
        """
        output = []
        output.append("\n📈 ATTACK GRAPH (Relationships)")
        output.append("━" * 60)
        
        if self.graph.number_of_nodes() == 0:
            output.append("  (No entities discovered yet)")
            output.append("━" * 60)
            return "\n".join(output)
        
        # Limit nodes to display
        if self.graph.number_of_nodes() > max_nodes:
            output.append(f"  (Showing {max_nodes} of {self.graph.number_of_nodes()} nodes)")
            output.append("")
        
        # Get representative nodes (prioritize IPs and high-degree nodes)
        nodes_to_show = self._select_important_nodes(max_nodes)
        
        # Display edges
        shown_edges = set()
        for source in nodes_to_show:
            if source not in self.graph:
                continue
                
            source_data = self.graph.nodes[source]
            source_type = source_data.get('type', 'UNKNOWN')
            source_icon = self.ICONS.get(source_type, '📍')
            source_color = self.COLORS.get(source_type, '')
            reset = self.COLORS['RESET']
            
            # Get outgoing edges
            neighbors = list(self.graph.neighbors(source))
            if not neighbors:
                continue
            
            # Show node
            output.append(f"{source_color}{source_icon} [{source}]{reset}")
            
            for i, target in enumerate(neighbors[:5]):  # Limit neighbors
                if target not in nodes_to_show:
                    continue
                
                edge_key = (source, target)
                if edge_key in shown_edges:
                    continue
                shown_edges.add(edge_key)
                
                # Get edge info
                edge_data = self.graph.edges[source, target]
                relationship = edge_data.get('relationship', 'connected_to')
                
                # Get target info
                target_data = self.graph.nodes[target]
                target_type = target_data.get('type', 'UNKNOWN')
                target_icon = self.ICONS.get(target_type, '📍')
                target_color = self.COLORS.get(target_type, '')
                
                # Draw edge
                is_last = (i == len(neighbors) - 1) or (i == 4)
                connector = "└──" if is_last else "├──"
                
                output.append(f"  {connector}[{relationship}]──> {target_color}{target_icon} {target}{reset}")
            
            output.append("")  # Spacing
        
        output.append("━" * 60)
        return "\n".join(output)
    
    def _select_important_nodes(self, max_nodes: int) -> List[str]:
        """
        Select the most important nodes to display.
        Prioritizes IPs and high-degree nodes.
        
        Args:
            max_nodes: Maximum number of nodes to select
            
        Returns:
            List of node IDs
        """
        # Prioritize by type
        type_priority = ['IP', 'VULNERABILITY', 'SERVICE', 'CREDENTIAL', 'PORT']
        
        selected = []
        
        # First, add nodes by priority type
        for node_type in type_priority:
            for node, data in self.graph.nodes(data=True):
                if len(selected) >= max_nodes:
                    break
                if data.get('type') == node_type and node not in selected:
                    selected.append(node)
        
        # Then add high-degree nodes
        if len(selected) < max_nodes:
            degrees = dict(self.graph.degree())
            remaining_nodes = [n for n in self.graph.nodes() if n not in selected]
            remaining_sorted = sorted(remaining_nodes, 
                                    key=lambda n: degrees.get(n, 0), 
                                    reverse=True)
            selected.extend(remaining_sorted[:max_nodes - len(selected)])
        
        return selected
    
    def render_full(self) -> str:
        """
        Render complete visualization: stats + list + graph.
        
        Returns:
            Complete visualization string
        """
        output = []
        output.append(self.render_statistics())
        output.append(self.render_node_list())
        output.append(self.render_ascii_graph())
        return "\n".join(output)
