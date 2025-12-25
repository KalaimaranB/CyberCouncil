from langchain_chroma import Chroma 
from langchain_core.documents import Document 
from ai.vector_engine import PyTorchEmbedder
from ui.terminal_renderer import TerminalRenderer
from parsing.discovery_parser import DiscoveryParser
from parsing.tool_parser import ToolOutputParser, is_likely_tool_output
from ai.router import QueryRouter
from parsing.logger import Logger
from graph.attack_graph import AttackGraph
from graph.graph_visualizer import GraphVisualizer
from core.ollama_client import OllamaClient
from core.context_builder import ContextBuilder
from core.session_manager import SessionManager
from core.commands.sitrep import SitrepCommand
from core.commands.graph import GraphCommand
from core.commands.finalize import FinalizeCommand
from core.commands.help import HelpCommand
from core.commands.tutorial import TutorialCommand
from core.commands.crack import CrackCommand
from remote import api_server
from web import dashboard as web_dashboard
from utils import project_status
from utils import tools
import sys
import os
import glob
import atexit
from core import config

class CyberCouncil:
    def __init__(self):
        print("💀 Initializing Council Systems...")
        
        # Initialize Ollama client with model validation
        try:
            self.ollama_client = OllamaClient()
        except RuntimeError as e:
            print(f"❌ {e}")
            sys.exit(1)
        
        # Initialize embedding and database
        try:
            self.embedding_fn = PyTorchEmbedder()
            self.db = Chroma(persist_directory=config.DB_DIR, embedding_function=self.embedding_fn)
        except Exception as e:
            print(f"❌ CRITICAL ERROR: Could not load Database or PyTorch Engine.\nDetails: {e}")
            sys.exit(1)
        
        # Issue #2 Fix: Database Health Check
        self.check_database_health()
        
        # Issue #8 Fix: Resource Cleanup
        atexit.register(self.cleanup)
            
        self.current_project = None
        self.context_mode = "GENERAL"
        
        # Terminal renderer for markdown formatting
        self.renderer = TerminalRenderer(enabled=config.TERMINAL_RENDERING_ENABLED)
        
        # Discovery parser for extracting user findings
        self.discovery_parser = DiscoveryParser()
        
        # Query router for strategic vs tactical
        self.router = QueryRouter()
        
        # Logger for auto-logging and pending logs
        self.logger = Logger(ollama_caller=self.ollama_client.call_with_retry)
        
        # Context builder for RAG retrieval
        self.context_builder = ContextBuilder(db=self.db)
        
        # Session manager for project state
        self.session_manager = SessionManager()

    

    
    def check_database_health(self):
        """Issue #2 Fix: Verifies the vector database has content"""
        try:
            test_results = self.db.similarity_search("test", k=1)
            if not test_results:
                print("⚠️  WARNING: Knowledge base is empty!")
                print("   Run 'python ingest.py' to populate the database with notes.")
            else:
                # Try to estimate total documents
                print(f"✅ Knowledge base loaded (found indexed content)")
        except Exception as e:
            print(f"⚠️  Database health check warning: {e}")
    
    def cleanup(self):
        """Issue #8 Fix: Cleanup resources on exit"""
        try:
            if hasattr(self, 'db') and self.db:
                # ChromaDB handles persistence automatically, just ensure clean shutdown
                del self.db
        except Exception as e:
            print(f"Cleanup warning: {e}")
    

    # --- PROJECT MANAGEMENT ---



    def generate_sitrep(self):
        """Parses the Active Record to give a 'Where are we' summary"""
        if not self.current_project:
            return

        path = f"{config.PROJECTS_DIR}/{self.current_project}/active_record.md"
        if not os.path.exists(path):
            print("⚠️ No Active Record found.")
            return

        with open(path, 'r') as f:
            content = f.read()

        print(f"\n📊 SITUATION REPORT: {self.current_project}")
        print("-" * 50)
        
        sections = ["ENUMERATION", "EXPLOITATION", "POST-EXPLOITATION"]
        
        for section in sections:
            print(f"[{section}]:")
            # Using concatenation to avoid f-string parser conflicts with HTML tags
            start_tag = "<!-- SECTION: " + section + " -->"
            
            if start_tag in content:
                try:
                    # 1. Grab everything AFTER the start tag
                    part = content.split(start_tag)[1]
                    
                    # 2. Grab everything BEFORE the next tag (if it exists)
                    if "<!--" in part:
                        part = part.split("<!--")[0]
                    
                    # 3. Clean and Split lines
                    lines = [l.strip() for l in part.split('\n') if l.strip()]
                    
                    if lines:
                        # Show last 3 non-empty lines
                        for l in lines[-3:]: 
                            print(f"   {l}")
                    else:
                        print("   (No actions recorded)")
                except Exception as e:
                    print(f"   (Parsing Error: {e})")
            else:
                print("   (Section tag missing - Recreate Project to fix)")
        print("-" * 50 + "\n")
    
    def show_attack_graph(self):
        """Display the attack graph visualization"""
        if not self.attack_graph:
            print("⚠️  Attack graph not initialized. Load a project first.")
            return
         
        # Update graph from current active record
        self.update_attack_graph()
        
        # Visualize
        viz = GraphVisualizer(self.attack_graph.graph)
        print(viz.render_full())
    
    def update_attack_graph(self):
        """Update attack graph from current active_record.md"""
        if not self.current_project or not self.attack_graph:
            return
        
        active_record_path = f"{config.PROJECTS_DIR}/{self.current_project}/active_record.md"
        if os.path.exists(active_record_path):
            self.attack_graph.parse_active_record(active_record_path)

    def finalize_project(self):
        """
        The Closing Ceremony:
        1. Reads the full logs.
        2. Uses Strategist to summarize success.
        3. Saves to 'Learned' folder for future RAG ingestion.
        4. Marks project as closed to prevent reopening.
        """
        if not self.current_project:
            print("No active project to close.")
            return False

        print(f"\n🛑 CLOSING CEREMONY INITIATED FOR: [{self.current_project}]")
        confirm = input(f"This will parse the active record, generate 'Lessons Learned', and archive the project.\nProceed? (y/n): ")
        if confirm.lower() != 'y':
            return False
            
        # Execute finalize command
        return FinalizeCommand().execute(self)

    def run(self):
        # Welcome banner
        print("\n" + "═" * 55)
        print("║" + " " * 53 + "║")
        print("║     🧠 CYBER COUNCIL - Intelligence System         ║")
        print("║" + " " * 53 + "║")
        print("╠═══════════════════════════════════════════════════════╣")
        print("║  Type /help for commands  │  /tutorial to learn     ║")
        print("═" * 55)
        
        # --- 1. STARTUP MENU ---
        while True:
            print("[1] New Project")
            print("[2] Search Projects")
            print("--- RECENT ---")
            recents = self.session_manager.list_recent_projects()
            for i, p in enumerate(recents):
                print(f"[{i+3}] {p}")
            
            # Issue #5 Fix: Input validation
            choice = input("\nSelect Option: ").strip()
            
            if choice == '1':
                name = input("Project Name: ")
                # Project name sanitization happens in tools.init_project
                self.session_manager.create_new_project(name)
                # Get the sanitized name back
                self.current_project = tools.sanitize_project_name(name)
                break
            elif choice == '2':
                query = input("🔎 Enter search term: ").lower()
                matches = self.session_manager.search_projects(query)
                if not matches:
                    print("No matches found.")
                    continue
                for i, m in enumerate(matches):
                    print(f"[{i}] {m}")
                try:
                    sel_input = input("Select Index: ").strip()
                    sel = int(sel_input)
                    if 0 <= sel < len(matches):
                        self.current_project = matches[sel]
                        break
                    else:
                        print(f"Invalid selection. Please enter 0-{len(matches)-1}")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            elif choice.isdigit():
                idx = int(choice) - 3
                if 0 <= idx < len(recents):
                    self.current_project = recents[idx]
                    break
                else:
                    print("Invalid choice. Try again.")
            # Handle /help at startup menu
            elif choice.lower().startswith("/help"):
                args = choice[5:].strip()
                HelpCommand().execute(self, args)
            # Handle /tutorial at startup menu  
            elif choice.lower() in ["/tutorial", "/demo", "tutorial"]:
                TutorialCommand().execute(self)
            else:
                print("Invalid choice. Try again.")

        self.context_mode = "PROJECT"
        self.session_manager.set_mode("PROJECT")
        
        # Check if project is closed
        is_closed, status_data = self.session_manager.is_project_closed()
        if is_closed:
            print(f"\n🔒 This project was closed on {status_data.get('closed_at', 'unknown')}")
            print("Closed projects cannot be reopened to preserve investigation integrity.")
            print("\nSystem exiting. Run script again to start a different project.")
            return
        
        # Initialize attack graph for this project
        self.session_manager.initialize_project(self.current_project)
        self.attack_graph = self.session_manager.attack_graph
        self.current_project = self.session_manager.current_project
        
        # Print SitRep immediately upon loading
        SitrepCommand().execute(self)

        # --- 2. MAIN INTELLIGENCE LOOP ---
        while True:
            try:
                user_input = input(f"\n[{self.current_project}]> ")
            except EOFError:
                break

            if user_input.lower() in ["exit", "quit"]: break
            if not user_input.strip(): continue
            
            # --- TOOL OUTPUT PARSING ---
            # Check if input looks like tool output (multi-line, technical)
            if is_likely_tool_output(user_input) and self.context_mode == "PROJECT":
                tool_parser = ToolOutputParser(self.current_project)
                result = tool_parser.parse(user_input)
                if result:
                    print(f"\n🔧 Detected {result['tool'].upper()} output!")
                    print(f"📁 Raw saved to: {result['raw_file']}")
                    print(result['summary'])
                    
                    # Log all discoveries
                    for discovery in result['discoveries']:
                        log_msg = self.logger.auto_log_discovery(self.current_project, discovery)
                        print(log_msg)
                    
                    # Update attack graph
                    if self.attack_graph and result['discoveries']:
                        GraphCommand().update(self)
                    
                    print(f"\n✅ Imported {len(result['discoveries'])} discoveries from {result['tool']}")
                    continue
            
            # --- DISCOVERY AUTO-LOGGING ---
            # Extract and log discoveries immediately
            discoveries = self.discovery_parser.extract_discoveries(user_input)
            if discoveries and self.context_mode == "PROJECT":
                for discovery in discoveries:
                    log_msg = self.logger.auto_log_discovery(self.current_project, discovery)
                    print(log_msg)
                # Update attack graph with new discoveries
                if self.attack_graph:
                    GraphCommand().update(self)

            # --- SYSTEM COMMANDS ---
            if "/close" in user_input.lower() or "close investigation" in user_input.lower():
                if FinalizeCommand().execute(self):
                    print("System shutting down. Run script again to start new project.")
                    break

            if "pause" in user_input.lower() and "teach" in user_input.lower():
                print("⏸️  System: Entering Teach Mode (General Context Only).")
                self.context_mode = "GENERAL"
                self.session_manager.set_mode("GENERAL")
                continue
            if "resume" in user_input.lower():
                print("▶️  System: Restoring Project Context.")
                self.context_mode = "PROJECT"
                self.session_manager.set_mode("PROJECT")
                continue
            if any(phrase in user_input.lower() for phrase in ["status", "report", "sitrep", "where are we", "summary"]):
                SitrepCommand().execute(self)
                continue
            
            # Help command
            if user_input.lower().startswith("/help"):
                args = user_input[5:].strip()  # Get anything after /help
                HelpCommand().execute(self, args)
                continue
            
            # Tutorial command
            if user_input.lower() in ["/tutorial", "/demo", "tutorial"]:
                TutorialCommand().execute(self)
                continue
            
            # Review pending logs
            if user_input.lower() in ["/review", "review logs"]:
                self.logger.review_pending_logs(self.current_project)
                continue
            
            # Show attack graph
            if user_input.lower() in ["/graph", "graph", "show graph"]:
                GraphCommand().execute(self)
                continue
            
            # Hash cracking
            if user_input.lower().startswith("/crack"):
                args = user_input[6:].strip()
                CrackCommand().execute(self, args)
                continue
            
            # Remote server control
            if user_input.lower().startswith("/server"):
                args = user_input[7:].strip().lower()
                if args == 'start':
                    if api_server.start_server(self):
                        ip = api_server.get_local_ip()
                        print(f"\n🌐 Remote API server started!")
                        print(f"   URL: http://{ip}:5051")
                        print(f"   From Kali: ./council-client.py --host {ip} \"message\"")
                    else:
                        print("⚠️  Server already running")
                elif args == 'stop':
                    api_server.stop_server()
                    print("🚫 Server stopped")
                elif args == 'status':
                    if api_server.is_running():
                        ip = api_server.get_local_ip()
                        print(f"✅ Server running at http://{ip}:5051")
                    else:
                        print("❌ Server not running")
                else:
                    print("Usage: /server start | stop | status")
                continue
            
            # Web Dashboard
            if user_input.lower() in ["/dashboard", "/web", "/ui"]:
                import webbrowser
                import threading
                
                app, socketio = web_dashboard.create_dashboard_app(self)
                port = 5052
                ip = api_server.get_local_ip()
                
                def run_dashboard():
                    socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False)
                
                thread = threading.Thread(target=run_dashboard, daemon=True)
                thread.start()
                
                import time
                time.sleep(0.5)
                
                url = f"http://{ip}:{port}"
                print(f"\n🌐 Web Dashboard started at {url}")
                webbrowser.open(url)
                continue
            
            # Clear pending logs
            if user_input.lower() in ["/clear-logs", "clear logs"]:
                count = len(self.logger.pending_logs)
                if count > 0:
                    confirm = input(f"Clear {count} pending log(s)? (y/n): ")
                    if confirm.lower() == 'y':
                        self.logger.clear_pending_logs()
                        print("✅ Pending logs cleared")
                else:
                    print("📋 No pending logs to clear")
                continue
            
            if "/search" in user_input:
                query = user_input.replace("/search", "").strip()
                search_res = tools.search_official_docs(query)
                user_input += f"\n\n[SYSTEM SEARCH RESULT]: {search_res}"
                # Add to pending logs instead of auto-logging
                if self.context_mode == "PROJECT":
                    self.logger.add_pending_log(
                        f"Searched: {query}",
                        search_res,
                        'ENUMERATION'
                    )
                    print("📝 Search logged to pending (ENUMERATION)")

            # 1. Retrieve Context using ContextBuilder
            context = self.context_builder.build_context(
                user_input,
                project=self.current_project,
                mode=self.context_mode
            )

            # 2. Router (Hybrid Scoring System)
            routing_decision = self.router.route_query(user_input)
            is_strategic = (routing_decision == 'strategic')

            if is_strategic:
                # --- STRATEGIST (Phi-4) ---
                print("\n[Vader] Thinking...")
                strat_input = f"CONTEXT:\n{context}\n\nUSER REQUEST:\n{user_input}"
                try:
                    # Use Ollama client for strategist calls
                    plan = self.ollama_client.call_strategist(strat_input)
                    # Format output with terminal renderer
                    formatted_plan = self.renderer.render(plan)
                    print(f"\n{formatted_plan}")
                    
                    # Batch logging with AI classification
                    if self.context_mode == "PROJECT":
                        section = self.ollama_client.classify_log_section(user_input, plan)
                        self.logger.add_pending_log(user_input, plan, section)
                        print(f"\n📝 Logged to pending ({section})")
                        
                except Exception as e:
                    print(f"❌ Error communicating with Ollama (Strategist): {e}")
                    print("Please verify Ollama is running and the model is available.")
                
            else:
                # --- SPECIALIST (DeepHat) ---
                print("\n[Specialist] Processing...")
                spec_input = f"CONTEXT:\n{context}\n\nUSER REQUEST: {user_input}\n\nProvide the specific command, code, or brief technical answer."
                try:
                    # Use Ollama client for specialist calls
                    response = self.ollama_client.call_specialist(spec_input)
                    # Format output with terminal renderer
                    formatted_response = self.renderer.render(response)
                    print(f"\n{formatted_response}")

                    # Batch logging with AI classification
                    if self.context_mode == "PROJECT":
                        section = self.ollama_client.classify_log_section(user_input, response)
                        self.logger.add_pending_log(user_input, response, section)
                        print(f"\n📝 Logged to pending ({section})")
                        
                except Exception as e:
                    print(f"❌ Error communicating with Ollama (Specialist): {e}")
                    print("Please verify Ollama is running and the model is available.")

if __name__ == "__main__":
    try:
        Council = CyberCouncil()
        Council.run()
    except KeyboardInterrupt:
        print("\n\n💀 Council Disconnected.")