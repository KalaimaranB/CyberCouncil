"""
Finalize Command
"""

from core.commands.base import Command
from core import config
from utils import project_status

class FinalizeCommand(Command):
    """
    Finalizes a project, generating reports and closing the session.
    """
    
    def execute(self, context) -> bool:
        """
        Generates final report and closes the project.
        """
        if not context.current_project:
            print("❌ No active project to finalize.")
            return False
            
        print(f"\n🏁 Finalizing Project: {context.current_project}")
        
        # 1. Ensure all logs are committed
        if context.logger.pending_logs:
            print(f"⚠️  You have {len(context.logger.pending_logs)} pending logs.")
            choice = input("Commit them before closing? (y/n): ").lower()
            if choice == 'y':
                context.review_pending_logs()
        
        # 2. Generate Final Report using Strategist
        print("📝 Generating Final Report...")
        try:
            with open(f"{config.PROJECTS_DIR}/{context.current_project}/active_record.md", "r") as f:
                full_log = f.read()
            
            prompt = f"""
            Generate a comprehensive Final Engagement Report for project '{context.current_project}'.
            
            Include:
            1. Executive Summary
            2. Attack Path Narrative
            3. Critical Vulnerabilities Found
            4. Remediation Recommendations
            
            Based on this log:
            {full_log}
            """
            
            report = context.ollama_client.call_strategist(prompt)
            
            # Save report
            report_path = f"{config.PROJECTS_DIR}/{context.current_project}/FINAL_REPORT.md"
            with open(report_path, "w") as f:
                f.write(report)
            
            print(f"✅ Final Report saved to: {report_path}")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            # Continue closing anyway?
        
        # 3. Export Attack Graph
        if context.attack_graph:
            try:
                export_path = f"{config.PROJECTS_DIR}/{context.current_project}/attack_graph.json"
                context.attack_graph.save_graph(export_path)
                print(f"✅ Attack graph exported to: {export_path}")
            except Exception as e:
                print(f"⚠️  Could not export graph: {e}")

        # 4. Mark Project as Closed
        try:
            project_status.mark_project_closed(context.current_project)
            print("🔒 Project marked as CLOSED.")
            return True
        except Exception as e:
            print(f"❌ Error during finalization: {e}")
            return False
