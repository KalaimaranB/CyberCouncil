"""
Tutorial Command

Interactive walkthrough that guides new users through CyberCouncil features.
"""

from core.commands.base import Command
from core import config
import os
import time


# Tutorial steps
TUTORIAL_STEPS = [
    {
        'title': '👋 Welcome to CyberCouncil!',
        'content': '''
This interactive tutorial will walk you through all the key features.
You'll learn how to:
• Log discoveries automatically
• Import tool output (nmap, rustscan, etc.)
• Visualize your attack graph
• Crack hashes with GPU
• Use the web dashboard

Press Enter to continue...''',
        'action': None
    },
    {
        'title': '📝 Step 1: Auto-Discovery Logging',
        'content': '''
CyberCouncil automatically extracts and logs key information from your input.

Try typing something like:
  "Found 10.10.10.5 is a Domain Controller with ports 88, 445 open"

The system will automatically:
  ✓ Extract the IP address (10.10.10.5)
  ✓ Identify it as a Domain Controller
  ✓ Log the open ports
  ✓ Add everything to your Attack Graph''',
        'action': 'demo_discovery'
    },
    {
        'title': '📥 Step 2: Tool Import',
        'content': '''
Just paste raw output from security tools:

  • nmap      - Ports, services, OS detection
  • rustscan  - Fast port scans
  • gobuster  - Directory enumeration
  • wpscan    - WordPress vulnerabilities
  • nikto     - Web server scanning

The system auto-detects the tool and extracts data!
Raw output is saved in tool_outputs/ folder.''',
        'action': None
    },
    {
        'title': '🤖 Step 3: Asking the AI',
        'content': '''
CyberCouncil has two AI personas:

1. STRATEGIST (Vader) - For "how should I approach this?" questions
   • Planning attack paths
   • Methodology guidance
   • Kill chain progression

2. SPECIALIST (DeepHat) - For "give me the exact command" requests
   • Specific tool syntax
   • Code snippets
   • Quick technical answers

The system automatically routes your question to the right AI!''',
        'action': None
    },
    {
        'title': '🕸️ Step 4: Attack Graph (/graph)',
        'content': '''
The Attack Graph visualizes relationships between:
  • Target IPs (blue)
  • Services (green)  
  • Vulnerabilities (red)
  • Credentials (yellow)

Use /graph for interactive web visualization with:
  • Path finding between nodes
  • Filtering by type
  • Export to PNG/JSON''',
        'action': None
    },
    {
        'title': '🔐 Step 5: Hash Cracking (/crack)',
        'content': '''
GPU-accelerated hash cracking with auto-detection:

  /crack 31d6cfe0d16ae931b73c59d7e0c089c0

Supports: NTLM, MD5, SHA, bcrypt, Kerberos, and more!
Type /crack --types to see all supported formats.

No need to remember hashcat mode numbers!''',
        'action': None
    },
    {
        'title': '🌐 Step 6: Web Dashboard (/dashboard)',
        'content': '''
Full web-based interface with:

  • Interactive attack graph
  • Terminal (send commands from browser)
  • Pending logs view
  • Hash cracker UI

Type /dashboard to launch in your browser!''',
        'action': None
    },
    {
        'title': '🎉 Tutorial Complete!',
        'content': '''
You're ready to use CyberCouncil!

Quick Reference:
  /help       - Show all commands
  /sitrep     - Strategic summary
  /graph      - Attack visualization
  /dashboard  - Full web UI
  /crack      - GPU hash cracking
  /server     - Remote API (Kali VM)
  /close      - Finalize engagement

Just type naturally - discoveries are captured automatically!

Happy hunting! 🎯''',
        'action': None
    },
]



class TutorialCommand(Command):
    """
    Interactive tutorial for new users.
    """
    
    def execute(self, context) -> bool:
        """
        Run the interactive tutorial.
        """
        print("\n" + "═" * 60)
        print("    🎓 CYBER COUNCIL - Interactive Tutorial")
        print("═" * 60)
        
        for i, step in enumerate(TUTORIAL_STEPS):
            self._show_step(i + 1, len(TUTORIAL_STEPS), step)
            
            # Wait for user input
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                print("\n\n❌ Tutorial cancelled.\n")
                return False
            
            # Run demo action if specified
            if step.get('action'):
                self._run_demo_action(step['action'], context)
        
        return True
    
    def _show_step(self, current: int, total: int, step: dict):
        """Display a tutorial step."""
        print("\n" + "─" * 60)
        print(f"  [{current}/{total}] {step['title']}")
        print("─" * 60)
        print(step['content'])
    
    def _run_demo_action(self, action: str, context):
        """Execute a demo action."""
        if action == 'demo_discovery':
            self._demo_discovery(context)
        elif action == 'demo_sitrep':
            print("\n  💡 Try: Type '/sitrep' after the tutorial to see this in action!")
            time.sleep(1)
        elif action == 'demo_graph':
            print("\n  💡 Try: Type '/graph' after the tutorial to see the visualization!")
            time.sleep(1)
    
    def _demo_discovery(self, context):
        """Demonstrate auto-discovery logging."""
        print("\n  📍 Demo: Simulating discovery input...")
        time.sleep(0.5)
        
        demo_input = "Found 10.10.10.5 is a Domain Controller"
        print(f"  > \"{demo_input}\"")
        time.sleep(0.5)
        
        print("  ✓ Extracted: 🎯 IP [DOMAIN_CONTROLLER]: 10.10.10.5")
        print("  ✓ Added to Attack Graph\n")
        time.sleep(1)


def create_demo_project():
    """Create a demo project with sample data for users to explore."""
    demo_dir = f"{config.PROJECTS_DIR}/Demo_Pentest"
    
    # Check if already exists
    if os.path.exists(demo_dir):
        return demo_dir
    
    os.makedirs(demo_dir, exist_ok=True)
    
    # Create sample active record
    active_record = '''# Active Record - Demo_Pentest
*Demo project showcasing CyberCouncil features*

<!-- SECTION: ENUMERATION -->
## Enumeration

🎯 IP [TARGET]: 10.10.10.5 - Domain Controller
🎯 IP [WEB_SERVER]: 10.10.10.20 - Web Application Server
⚙️ Service: SMB on 10.10.10.5
⚙️ Service: HTTP on 10.10.10.20
⚙️ Service: Kerberos on 10.10.10.5
✅ Open Port: 445 (SMB)
✅ Open Port: 88 (Kerberos)
✅ Open Port: 80 (HTTP)
✅ Open Port: 443 (HTTPS)

<!-- SECTION: EXPLOITATION -->
## Exploitation

🚨 Vulnerability: MS17-010 (EternalBlue) on 10.10.10.5
🚨 Vulnerability: CVE-2021-44228 (Log4Shell) on 10.10.10.20
👤 Username: svc_backup (service account)
🔐 Hash: aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0

<!-- SECTION: POST-EXPLOITATION -->
## Post-Exploitation

🔑 Credential: CORP\\administrator
🏰 Domain: CORP.LOCAL
'''
    
    with open(f"{demo_dir}/active_record.md", 'w') as f:
        f.write(active_record)
    
    return demo_dir
