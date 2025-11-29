import ollama
from langchain_chroma import Chroma 
from langchain_core.documents import Document 
from ai.vector_engine import PyTorchEmbedder
from ui.terminal_renderer import TerminalRenderer
from parsing.discovery_parser import DiscoveryParser
from ai.router import QueryRouter
from parsing.logger import Logger
from graph.attack_graph import AttackGraph
from graph.graph_visualizer import GraphVisualizer
from utils import project_status
from utils import tools
import sys
import os
import glob
import time
import atexit
from core import config

class CyberCouncil:
    def __init__(self):
        print("💀 Initializing Council Systems...")
        
        # Issue #1 Fix: Model Validation
        self.strategist_model = config.STRATEGIST_MODEL
        self.specialist_model = config.SPECIALIST_MODEL
        if not self.validate_ollama_models():
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
        self.logger = Logger(ollama_caller=self.call_ollama_with_retry)
        
        # Attack graph for relationship tracking
        self.attack_graph = None  # Initialized when project is loaded
    
    def validate_ollama_models(self):
        """Issue #1 Fix: Validates that required Ollama models are available"""
        try:
            available = ollama.list()
            
            # Handle different response formats
            if isinstance(available, dict):
                models = available.get('models', [])
            else:
                models = available
            
            # Extract model names - handle both 'name' and 'model' keys
            model_names = []
            for m in models:
                if isinstance(m, dict):
                    name = m.get('name') or m.get('model', '')
                    if name:
                        model_names.append(name)
                elif isinstance(m, str):
                    model_names.append(m)
            
            if not model_names:
                print("⚠️  WARNING: Could not retrieve model list from Ollama.")
                print("Attempting to proceed anyway...")
                return True  # Allow to proceed if we can't get the list
            
            missing = []
            if self.strategist_model not in model_names:
                missing.append(self.strategist_model)
            if self.specialist_model not in model_names:
                missing.append(self.specialist_model)
            
            if missing:
                print(f"❌ CRITICAL ERROR: Missing Ollama models: {', '.join(missing)}")
                print(f"\nAvailable models: {', '.join(model_names)}")
                print(f"\nPlease ensure the following models are installed:")
                print(f"  - {self.strategist_model}")
                print(f"  - {self.specialist_model}")
                return False
            
            print(f"✅ Models validated: {self.strategist_model}, {self.specialist_model}")
            return True
        except Exception as e:
            print(f"❌ Cannot connect to Ollama service: {e}")
            print("Please ensure Ollama is running.")
            return False
    
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
    
    def call_ollama_with_retry(self, model, messages, max_retries=None):
        """Issue #7 Fix: Retry logic for Ollama API calls with exponential backoff"""
        if max_retries is None:
            max_retries = config.OLLAMA_MAX_RETRIES
        
        for attempt in range(max_retries):
            try:
                response = ollama.chat(model=model, messages=messages)
                return response['message']['content']
            except Exception as e:
                if attempt == max_retries - 1:
                    # Final attempt failed
                    raise
                
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"⚠️  Retry {attempt + 1}/{max_retries} (waiting {wait_time}s): {e}")
                time.sleep(wait_time) 
    
    def route_query_hybrid(self, user_input):
        """
        Improved router using hybrid scoring system.
        Combines multiple signals for better routing accuracy.
        """
        score = {
            'strategic': 0,
            'tactical': 0
        }
        
        user_lower = user_input.lower()
        
        # Signal 1: Strategy keywords (+2 each)
        strategy_keywords = [
            "plan", "strategy", "analyze", "review", "think", "vader", "approach", 
            "vector", "what should i do", "what is", "target", "current", "how do i",
            "explain", "why", "assess", "evaluate", "consider", "recommend", "advise",
            "how should"
        ]
        
        for keyword in strategy_keywords:
            if keyword in user_lower:
                score['strategic'] += 2
                break  # Only count once
        
        # Signal 2: Tactical keywords (+2 each)
        tactical_keywords = [
            "command", "syntax", "code", "script", "give me", "show me",
            "what's the", "tool for"
        ]
        
        for keyword in tactical_keywords:
            if keyword in user_lower:
                score['tactical'] += 2
                break
        
        # Signal 3: Question type (+1)
        if user_input.startswith(("How should", "Why", "What is", "When", "Explain")):
            score['strategic'] += 1
        elif user_input.startswith(("Give me", "Show me", "What's the", "Which tool")):
            score['tactical'] += 1
        
        # Signal 4: Length (+1)
        word_count = len(user_input.split())
        if word_count > 10:
            score['strategic'] += 1
        elif word_count < 6:
            score['tactical'] += 1
        
        # Signal 5: Code markers (+2 for tactical)
        if '```' in user_input or 'command for' in user_lower:
            score['tactical'] += 2
        
        # Decision: highest score wins
        return 'strategic' if score['strategic'] > score['tactical'] else 'tactical'
    
    def retrieve_with_mmr(self, query, k=5):
        """
        Retrieves documents using Maximal Marginal Relevance for diversity.
        Balances relevance with diversity to avoid redundant results.
        """
        try:
            # Get more candidates than needed
            candidates = self.db.similarity_search_with_score(query, k=config.RAG_CANDIDATE_K)
            
            # Filter by relevance threshold
            relevant = [(doc, score) for doc, score in candidates if score >= config.RAG_RELEVANCE_THRESHOLD]
            
            if not relevant:
                return []
            
            # MMR selection
            selected = []
            remaining = relevant.copy()
            
            # Always select most relevant first
            if remaining:
                best_doc, best_score = max(remaining, key=lambda x: x[1])
                selected.append(best_doc)
                remaining.remove((best_doc, best_score))
            
            # Select remaining docs balancing relevance and diversity
            while len(selected) < k and remaining:
                best_score_val = -999
                best_item = None
                
                for doc, relevance in remaining:
                    # Calculate similarity to already selected docs
                    if selected:
                        # Simple diversity check: avoid docs with too similar content
                        max_similarity = max(
                            len(set(doc.page_content.split()) & set(s.page_content.split())) / 
                            max(len(doc.page_content.split()), len(s.page_content.split()))
                            for s in selected
                        )
                    else:
                        max_similarity = 0
                    
                    # MMR score: balance relevance vs diversity
                    mmr_score = (config.MMR_LAMBDA * relevance) - ((1 - config.MMR_LAMBDA) * max_similarity)
                    
                    if mmr_score > best_score_val:
                        best_score_val = mmr_score
                        best_item = (doc, relevance)
                
                if best_item:
                    selected.append(best_item[0])
                    remaining.remove(best_item)
                else:
                    break
            
            return selected
            
        except AttributeError:
            # Fallback if similarity_search_with_score not available
            print("⚠️  Using fallback retrieval (MMR not available)")
            return self.db.similarity_search(query, k=k)
    
    def classify_log_section(self, user_query, ai_response):
        """
        Uses AI to classify which pentesting section an action belongs to.
        Returns: ENUMERATION, EXPLOITATION, or POST-EXPLOITATION
        """
        try:
            prompt = f"""Classify this pentesting action into ONE category:

ENUMERATION: Scanning, discovery, reconnaissance, information gathering
EXPLOITATION: Exploiting vulnerabilities, gaining initial access
POST-EXPLOITATION: Privilege escalation, lateral movement, persistence

User: "{user_query[:200]}"
AI: "{ai_response[:200]}"

Answer with ONE WORD:"""
            
            # Use fast model for classification
            result = self.call_ollama_with_retry(
                config.LOG_CLASSIFIER_MODEL,
                [{'role': 'user', 'content': prompt}],
                max_retries=1
            )
            
            result_upper = result.upper()
            if "ENUMERATION" in result_upper:
                return "ENUMERATION"
            elif "EXPLOITATION" in result_upper:
                return "EXPLOITATION"
            elif "POST" in result_upper:
                return "POST-EXPLOITATION"
            else:
                # Default fallback
                return "ENUMERATION"
        except Exception as e:
            print(f"⚠️  Log classification failed: {e}")
            return "ENUMERATION"  # Safe default
    
    def review_pending_logs(self):
        """Allows user to review and commit pending logs"""
        if not self.pending_logs:
            print("📋 No pending logs to review.")
            return
        
        print(f"\n📋 Pending Logs ({len(self.pending_logs)} items):")
        print("-" * 60)
        for i, log in enumerate(self.pending_logs):
            print(f"[{i}] {log['section']:20s} | {log['query'][:50]}")
        print("-" * 60)
        
        choice = input("\nCommit (a)ll, (s)elective, (c)ancel, or (v)iew details? ").lower()
        
        if choice == 'a':
            for log in self.pending_logs:
                tools.update_active_record(
                    self.current_project,
                    log['section'],
                    log['query']
                )
            print(f"✅ Committed all {len(self.pending_logs)} logs")
            self.pending_logs = []
        
        elif choice == 's':
            indices_str = input("Enter numbers to commit (e.g., 0,2,5 or 0-3): ").strip()
            try:
                # Parse ranges and individual numbers
                indices = set()
                for part in indices_str.split(','):
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        indices.update(range(start, end + 1))
                    else:
                        indices.add(int(part))
                
                committed = 0
                for i in sorted(indices, reverse=True):
                    if 0 <= i < len(self.pending_logs):
                        log = self.pending_logs[i]
                        tools.update_active_record(
                            self.current_project,
                            log['section'],
                            log['query']
                        )
                        self.pending_logs.pop(i)
                        committed += 1
                
                print(f"✅ Committed {committed} log(s)")
            except (ValueError, IndexError) as e:
                print(f"❌ Invalid selection: {e}")
        
        elif choice == 'v':
            idx_str = input("Enter log number to view: ").strip()
            try:
                idx = int(idx_str)
                if 0 <= idx < len(self.pending_logs):
                    log = self.pending_logs[idx]
                    print(f"\n--- Log #{idx} ---")
                    print(f"Section: {log['section']}")
                    print(f"Query: {log['query']}")
                    print(f"Response preview:\n{log['response_preview']}")
                    print("-" * 60)
                else:
                    print("❌ Invalid index")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == 'c':
            print("❌ Review cancelled. Logs still pending.")
        else:
            print("❌ Invalid choice.")

    # --- PROJECT MANAGEMENT ---
    def list_recent_projects(self):
        """Returns the top 5 most recently modified project folders"""
        if not os.path.exists(config.PROJECTS_DIR):
            os.makedirs(config.PROJECTS_DIR)
            return []
        
        try:
            # Get all subdirectories in projects/
            projects = [f.path for f in os.scandir(config.PROJECTS_DIR) if f.is_dir()]
            
            # Issue #9 Fix: Prevent race conditions during modification time check
            valid_projects = []
            for p in projects:
                try:
                    mtime = os.path.getmtime(p)
                    valid_projects.append((p, mtime))
                except (FileNotFoundError, OSError) as e:
                    # Project was deleted or modified during scan
                    print(f"⚠️  Skipping {os.path.basename(p)}: {e}")
                    continue
            
            # Sort by modification time (newest first)
            valid_projects.sort(key=lambda x: x[1], reverse=True)
            
            # Return just the folder names (top 5)
            return [os.path.basename(p[0]) for p in valid_projects[:config.RECENT_PROJECTS_COUNT]]
        except Exception as e:
            print(f"Error scanning projects: {e}")
            return []

    def search_projects(self):
        """Allows user to search for a project string"""
        query = input("🔎 Enter search term: ").lower()
        if not os.path.exists(config.PROJECTS_DIR):
            return []
        projects = [f.name for f in os.scandir(config.PROJECTS_DIR) if f.is_dir()]
        matches = [p for p in projects if query in p.lower()]
        return matches

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

        print("\n[System] Retrieving full mission logs...")
        record_content = tools.get_active_record(self.current_project)
        
        # Issue #12 Fix: Backup before finalization
        backup_msg = tools.backup_active_record(self.current_project)
        print(backup_msg)

        print("[Vader] Analyzing mission success and failure patterns...")
        
        # The Post-Mortem Prompt
        prompt = (
            f"You are conducting a Post-Mortem Analysis for the operation: {self.current_project}.\n\n"
            f"RAW LOGS:\n{record_content}\n\n"
            "TASK:\n"
            "1. Ignore failed attempts, typos, or dead ends.\n"
            "2. Extract the successful attack vectors, discovered credentials, and key enumeration findings.\n"
            "3. Summarize the specific syntax or methodology that worked.\n"
            "4. Format the output as a clean Markdown technical guide titled 'Lessons Learned'.\n"
            "5. Do not include conversational filler. Focus on the technical takeaway.\n"
        )

        try:
            # Issue #7 Fix: Use retry logic for Ollama calls
            response = self.call_ollama_with_retry(self.strategist_model, [{'role': 'user', 'content': prompt}])
            
            print("\n[Vader] Analysis Complete. Archiving wisdom...")
            result_msg = tools.save_lessons_learned(self.current_project, response)
            print(result_msg)
            
            # Mark project as closed
            status_msg = project_status.mark_project_closed(self.current_project)
            print(status_msg)
            
            print(f"🏁 Operation {self.current_project} Closed. Context unloaded.")
            self.current_project = None
            self.context_mode = "GENERAL"
            return True

        except Exception as e:
            print(f"❌ Error during finalization: {e}")
            return False

    # --- CONTEXT & EXECUTION ---
    def retrieve_context(self, query):
        # 1. Get RAG results with MMR for quality and diversity
        docs = self.retrieve_with_mmr(query, k=config.RAG_RETRIEVAL_K)
        
        if docs:
            rag_text = "\n".join([f"[NOTE: {d.metadata.get('title', 'General')}]: {d.page_content}" for d in docs])
        else:
            rag_text = "[No relevant knowledge found in database]"
        
        # 2. Get Project Context (Active Record)
        project_text = ""
        if self.current_project and self.context_mode == "PROJECT":
            # Issue #3 Fix: Proper exception handling instead of bare except
            try:
                path = f"{config.PROJECTS_DIR}/{self.current_project}/active_record.md"
                with open(path, 'r') as f:
                    # We load the whole log so the model knows what has happened
                    project_text = f"\n[CURRENT ENGAGEMENT LOG]:\n{f.read()}"
            except FileNotFoundError:
                print(f"⚠️  Active record not found. Attempting to recreate...")
                try:
                    tools.init_project(self.current_project)
                    print("✅ Active record recreated.")
                except Exception as e:
                    print(f"⚠️  Could not recreate active record: {e}")
            except Exception as e:
                print(f"⚠️  Warning: Could not load project context: {e}")
                
        return f"{rag_text}\n{project_text}"

    def run(self):
        print("\n--- 🧠 CYBER COUNCIL ONLINE 🧠 ---")
        
        # --- 1. STARTUP MENU ---
        while True:
            print("\n[1] New Project")
            print("[2] Search Projects")
            print("--- RECENT ---")
            recents = self.list_recent_projects()
            for i, p in enumerate(recents):
                print(f"[{i+3}] {p}")
            
            # Issue #5 Fix: Input validation
            choice = input("\nSelect Option: ").strip()
            
            if choice == '1':
                name = input("Project Name: ")
                # Project name sanitization happens in tools.init_project
                result = tools.init_project(name)
                print(result)
                # Get the sanitized name back
                self.current_project = tools.sanitize_project_name(name)
                break
            elif choice == '2':
                matches = self.search_projects()
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
            else:
                print("Invalid choice. Try again.")

        self.context_mode = "PROJECT"
        # Check if project is closed
        is_closed, status_data = project_status.is_project_closed(self.current_project)
        if is_closed:
            print(f"\n🔒 This project was closed on {status_data.get('closed_at', 'unknown')}")
            print("Closed projects cannot be reopened to preserve investigation integrity.")
            print("\nSystem exiting. Run script again to start a different project.")
            return
        
        # Initialize attack graph for this project
        self.attack_graph = AttackGraph(self.current_project)
        print("🧠 Attack graph initialized")
        
        # Print SitRep immediately upon loading
        self.generate_sitrep()

        # --- 2. MAIN INTELLIGENCE LOOP ---
        while True:
            try:
                user_input = input(f"\n[{self.current_project}]> ")
            except EOFError:
                break

            if user_input.lower() in ["exit", "quit"]: break
            if not user_input.strip(): continue
            
            # --- DISCOVERY AUTO-LOGGING ---
            # Extract and log discoveries immediately
            discoveries = self.discovery_parser.extract_discoveries(user_input)
            if discoveries and self.context_mode == "PROJECT":
                for discovery in discoveries:
                    log_msg = self.logger.auto_log_discovery(self.current_project, discovery)
                    print(log_msg)
                # Update attack graph with new discoveries
                if self.attack_graph:
                    self.update_attack_graph()

            # --- SYSTEM COMMANDS ---
            if "/close" in user_input.lower() or "close investigation" in user_input.lower():
                self.finalize_project()
                # Loop back to menu if user wants to start another, or just exit?
                # For now, let's break to exit or we could loop back to menu.
                # Let's simple break to restart or exit.
                print("System shutting down. Run script again to start new project.")
                break

            if "pause" in user_input.lower() and "teach" in user_input.lower():
                print("⏸️  System: Entering Teach Mode (General Context Only).")
                self.context_mode = "GENERAL"
                continue
            if "resume" in user_input.lower():
                print("▶️  System: Restoring Project Context.")
                self.context_mode = "PROJECT"
                continue
            if any(phrase in user_input.lower() for phrase in ["status", "report", "sitrep", "where are we", "summary"]):
                self.generate_sitrep()
                continue
            
            # Review pending logs
            if user_input.lower() in ["/review", "review logs"]:
                self.logger.review_pending_logs(self.current_project)
                continue
            
            # Show attack graph
            if user_input.lower() in ["/graph", "graph", "show graph"]:
                self.show_attack_graph()
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

            # 1. Retrieve Context
            context = self.retrieve_context(user_input)

            # 2. Router (Hybrid Scoring System)
            routing_decision = self.router.route_query(user_input)
            is_strategic = (routing_decision == 'strategic')

            if is_strategic:
                # --- STRATEGIST (Phi-4) ---
                print("\n[Vader] Thinking...")
                strat_input = f"CONTEXT:\n{context}\n\nUSER REQUEST:\n{user_input}"
                try:
                    # Issue #7 Fix: Use retry logic
                    plan = self.call_ollama_with_retry(self.strategist_model, [{'role': 'user', 'content': strat_input}])
                    # Format output with terminal renderer
                    formatted_plan = self.renderer.render(plan)
                    print(f"\n{formatted_plan}")
                    
                    # Batch logging with AI classification
                    if self.context_mode == "PROJECT":
                        section = self.logger.classify_log_section(user_input, plan)
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
                    # Issue #7 Fix: Use retry logic
                    response = self.call_ollama_with_retry(self.specialist_model, [{'role': 'user', 'content': spec_input}])
                    # Format output with terminal renderer
                    formatted_response = self.renderer.render(response)
                    print(f"\n{formatted_response}")

                    # Batch logging with AI classification
                    if self.context_mode == "PROJECT":
                        section = self.logger.classify_log_section(user_input, response)
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