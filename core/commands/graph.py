"""
Graph Command
"""

from core.commands.base import Command
from graph.graph_visualizer import GraphVisualizer

class GraphCommand(Command):
    """
    Handles attack graph visualization and updates.
    """
    
    def execute(self, context) -> bool:
        """
        Shows the current attack graph.
        """
        if not context.attack_graph:
            print("⚠️  Attack graph not initialized")
            return False
            
        print("\n🕸️  Attack Graph Visualization")
        GraphVisualizer.render_graph(context.attack_graph)
        return True

    def update(self, context) -> bool:
        """
        Updates the attack graph from the active record.
        """
        if context.attack_graph:
            context.attack_graph.build_from_active_record()
            return True
        return False
