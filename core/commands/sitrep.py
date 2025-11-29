"""
SitRep Command
"""

from core.commands.base import Command
from core import config
from utils import tools

class SitrepCommand(Command):
    """
    Generates a Situation Report (SitRep) for the current project.
    """
    
    def execute(self, context) -> bool:
        """
        Parses the Active Record to give a 'Where are we' summary.
        """
        if not context.current_project:
            print("❌ No active project.")
            return False

        print("\n📊 Generating Situation Report (SitRep)...")
        
        # 1. Get Active Record
        try:
            with open(f"{config.PROJECTS_DIR}/{context.current_project}/active_record.md", "r") as f:
                active_record = f.read()
        except FileNotFoundError:
            print("⚠️  Active Record not found.")
            return False

        # 2. Get Attack Graph Stats
        graph_stats = "Graph not initialized"
        if context.attack_graph:
            stats = context.attack_graph.get_statistics()
            graph_stats = f"Nodes: {stats['nodes']}, Edges: {stats['edges']}"

        # 3. Ask Strategist for Summary
        prompt = f"""
        You are the Cyber Council Strategist.
        Review this engagement log and provide a concise Situation Report (SitRep).
        
        Format:
        ## 🚩 Current Status
        (Where are we in the kill chain?)
        
        ## 🎯 Key Findings
        (Top 3 most critical discoveries)
        
        ## 🔮 Recommended Next Steps
        (What should we do next?)
        
        Active Record:
        {active_record}
        
        Graph Stats: {graph_stats}
        """

        try:
            # Use Ollama client for strategist calls
            response = context.ollama_client.call_strategist(prompt)
            
            print("\n[Vader] Analysis Complete. Archiving wisdom...")
            result_msg = tools.save_lessons_learned(context.current_project, response)
            print(result_msg)
            
            # Render output
            formatted_response = context.renderer.render(response)
            print(f"\n{formatted_response}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating SitRep: {e}")
            return False
