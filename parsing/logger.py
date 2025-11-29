"""
Logger Module

Handles automatic logging of user discoveries and AI responses with intelligent
section classification. Provides a pending log review system for user approval.

Key Features:
- Auto-logging for immediate discoveries (IPs, credentials, etc.)
- AI-powered section classification (ENUMERATION/EXPLOITATION/POST-EXPLOITATION)
- Batch logging with user review capability
- Smart section mapping based on discovery type

Usage:
    logger = Logger(ollama_caller=some_function)
    logger.auto_log_discovery(project_name, discovery_dict)
    logger.add_pending_log(query, response, section)
    logger.review_pending_logs(project_name)
"""

from utils import tools
from parsing.discovery_parser import DiscoveryParser
from core import config

class Logger:
    """
    Manages automatic logging of user discoveries and AI responses.
    Provides batch logging system with user review capability.
    """
    
    def __init__(self, ollama_caller=None):
        """
        Initialize logger with optional Ollama caller for AI classification.
        
        Args:
            ollama_caller: Function to call Ollama (e.g., self.call_ollama_with_retry)
        """
        self.pending_logs = []
        self.discovery_parser = DiscoveryParser()
        self.ollama_caller = ollama_caller
    
    def classify_log_section(self, user_query, ai_response):
        """
        Uses AI to classify which pentesting section an action belongs to.
        Returns: ENUMERATION, EXPLOITATION, or POST-EXPLOITATION
        """
        if not self.ollama_caller:
            return "ENUMERATION"  # Default fallback
        
        try:
            prompt = f"""Classify this pentesting action into ONE category:

ENUMERATION: Scanning, discovery, reconnaissance, information gathering
EXPLOITATION: Exploiting vulnerabilities, gaining initial access
POST-EXPLOITATION: Privilege escalation, lateral movement, persistence

User: "{user_query[:200]}"
AI: "{ai_response[:200]}"

Answer with ONE WORD:"""
            
            # Use fast model for classification
            result = self.ollama_caller(
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
                return "ENUMERATION"  # Default fallback
        except Exception as e:
            print(f"⚠️  Log classification failed: {e}")
            return "ENUMERATION"  # Safe default
    
    def auto_log_discovery(self, project_name, discovery):
        """
        Immediately log a user discovery to the active record.
        Used for critical information like IPs, credentials, etc.
        """
        # Determine section based on discovery type
        section_map = {
            'ip_address': 'ENUMERATION',
            'hostname': 'ENUMERATION',
            'port': 'ENUMERATION',
            'open_port': 'ENUMERATION',
            'service': 'ENUMERATION',
            'domain': 'ENUMERATION',
            'username': 'EXPLOITATION',
            'password': 'EXPLOITATION',
            'hash': 'EXPLOITATION',
            'vulnerability': 'EXPLOITATION',
        }
        
        section = section_map.get(discovery['type'], 'ENUMERATION')
        log_entry = self.discovery_parser.format_discovery_log(discovery)
        
        # Log immediately
        tools.update_active_record(project_name, section, log_entry)
        
        return f"📍 Logged: {log_entry}"
    
    def add_pending_log(self, query, response, section):
        """Add a log entry to pending queue for user review"""
        self.pending_logs.append({
            'query': query,
            'response_preview': response[:150],
            'section': section
        })
    
    def review_pending_logs(self, current_project):
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
                    current_project,
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
                            current_project,
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
    
    def clear_pending_logs(self):
        """Clear all pending logs"""
        count = len(self.pending_logs)
        self.pending_logs = []
        return count
