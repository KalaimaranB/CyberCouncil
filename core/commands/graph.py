"""
Graph Command

Handles attack graph visualization. Supports both ASCII terminal view
and interactive web visualization with Cytoscape.js.
"""

from core.commands.base import Command
from graph.graph_visualizer import GraphVisualizer


class GraphCommand(Command):
    """
    Handles attack graph visualization and updates.
    Now supports interactive web visualization.
    """
    
    def __init__(self):
        self._server_port = None
    
    def execute(self, context) -> bool:
        """
        Shows the attack graph - launches interactive web view and shows terminal fallback.
        
        Args:
            context: CyberCouncil instance
            
        Returns:
            True if successful
        """
        if not context.attack_graph:
            print("⚠️  Attack graph not initialized. Load a project first.")
            return False
        
        # Update graph from current active record first
        self.update(context)
        
        # Try to launch web visualization
        try:
            from graph import graph_server
            
            if graph_server.is_running():
                # Server already running - just update the graph data
                graph_server.update_graph(context.attack_graph)
                print(f"\n🕸️  Graph server already running at http://localhost:{self._server_port}")
                print("    Refresh the browser to see updated data.\n")
            else:
                # Start new server
                port = graph_server.start_server(context.attack_graph, open_browser=True)
                if port:
                    self._server_port = port
                    print(f"\n🌐 Interactive Attack Graph opened at http://localhost:{port}")
                    print("    Leave terminal open to keep the visualization available.\n")
        except ImportError as e:
            print(f"⚠️  Web visualization unavailable: {e}")
            print("    Install flask: pip install flask")
        except Exception as e:
            print(f"⚠️  Could not start web visualization: {e}")
        
        # Always show ASCII fallback in terminal
        print("📊 Terminal View:")
        viz = GraphVisualizer(context.attack_graph.graph)
        print(viz.render_statistics())
        print(viz.render_ascii_graph(max_nodes=15))
        
        return True

    def update(self, context) -> bool:
        """
        Updates the attack graph from the active record.
        
        Args:
            context: CyberCouncil instance
            
        Returns:
            True if successful
        """
        if not context.attack_graph or not context.current_project:
            return False
        
        from core import config
        import os
        
        active_record_path = f"{config.PROJECTS_DIR}/{context.current_project}/active_record.md"
        if os.path.exists(active_record_path):
            context.attack_graph.parse_active_record(active_record_path)
            return True
        
        return False
