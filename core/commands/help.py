"""
Help Command

Provides comprehensive help for CyberCouncil commands and usage.
"""

from core.commands.base import Command


# Command registry with descriptions and examples
COMMANDS = {
    '/help': {
        'short': 'Show this help message',
        'usage': '/help [command]',
        'examples': ['/help', '/help graph'],
        'description': 'Display all available commands or detailed help for a specific command.'
    },
    '/sitrep': {
        'short': 'Generate situation report',
        'usage': '/sitrep',
        'aliases': ['status', 'report', 'where are we', 'summary'],
        'description': 'Analyzes your Active Record and provides a strategic summary of your current position in the engagement, key findings, and recommended next steps.'
    },
    '/graph': {
        'short': 'Open interactive attack graph',
        'usage': '/graph',
        'aliases': ['graph', 'show graph'],
        'description': 'Opens an interactive web-based visualization of your attack graph. Shows IPs, services, vulnerabilities, and their relationships. Includes path finding and filtering.'
    },
    '/review': {
        'short': 'Review pending logs',
        'usage': '/review',
        'aliases': ['review logs'],
        'description': 'Review and commit pending log entries to the Active Record. Allows selective commit or viewing details before saving.'
    },
    '/clear-logs': {
        'short': 'Clear pending logs',
        'usage': '/clear-logs',
        'aliases': ['clear logs'],
        'description': 'Discard all pending log entries without committing them.'
    },
    '/search': {
        'short': 'Search security docs',
        'usage': '/search <query>',
        'examples': ['/search kerberoasting', '/search privilege escalation'],
        'description': 'Search official security documentation and add results to your context for the AI to reference.'
    },
    '/close': {
        'short': 'Close investigation',
        'usage': '/close',
        'aliases': ['close investigation'],
        'description': 'Finalize the engagement: generates a final report, exports the attack graph, and archives the project. Project becomes read-only.'
    },
    '/tutorial': {
        'short': 'Start interactive tutorial',
        'usage': '/tutorial',
        'description': 'Launch a guided walkthrough that demonstrates all features using a demo project.'
    },
    '/crack': {
        'short': 'Crack hashes with GPU',
        'usage': '/crack HASH',
        'examples': ['/crack 31d6cfe0...', '/crack --types', '/crack -w /path/wordlist HASH'],
        'description': 'Crack hashes using hashcat with GPU acceleration. Auto-detects hash type (NTLM, MD5, SHA, bcrypt, Kerberos, etc.).'
    },
    '/server': {
        'short': 'Remote API server',
        'usage': '/server start|stop|status',
        'examples': ['/server start', '/server status'],
        'description': 'Control the remote API server for Kali VM access. Start the server, then use council-client.py from Kali.'
    },
    '/dashboard': {
        'short': 'Open web dashboard',
        'usage': '/dashboard',
        'aliases': ['/web', '/ui'],
        'description': 'Opens a full web-based dashboard with interactive graph, terminal, pending logs view, and hash cracker.'
    },
}

# Tool output support info
TOOL_SUPPORT = """
📥 TOOL OUTPUT IMPORT:
  Just paste raw output from these tools:
  • nmap      - Ports, services, OS detection
  • rustscan  - Fast port scans
  • gobuster  - Directory enumeration
  • wpscan    - WordPress vulnerabilities
  • nikto     - Web server scanning

  The system will auto-detect the tool and extract data!
"""

# Quick tips for new users
QUICK_TIPS = [
    "💡 Just type naturally! The AI understands questions and discoveries.",
    "💡 Discoveries are auto-logged: 'Found port 80 on 10.10.10.5' → automatically captured",
    "💡 Use '/sitrep' anytime to get a strategic summary of your progress",
    "💡 The attack '/graph' shows all relationships between your targets",
]


class HelpCommand(Command):
    """
    Displays help information for CyberCouncil commands.
    """
    
    def execute(self, context, args: str = "") -> bool:
        """
        Execute help command.
        
        Args:
            context: CyberCouncil instance
            args: Optional command name for detailed help
        """
        args = args.strip().lower()
        
        if args:
            # Detailed help for specific command
            self._show_command_help(args)
        else:
            # Show all commands
            self._show_all_help()
        
        return True
    
    def _show_all_help(self):
        """Display overview of all commands."""
        print("\n" + "═" * 60)
        print("🧠 CYBER COUNCIL - Command Reference")
        print("═" * 60)
        
        print("\n📋 COMMANDS:\n")
        
        for cmd, info in COMMANDS.items():
            print(f"  {cmd:15} - {info['short']}")
        
        print("\n" + "─" * 60)
        print("📝 NATURAL INPUT:")
        print("─" * 60)
        print("  Just type naturally! The system understands:")
        print("  • Questions: 'How do I enumerate SMB shares?'")
        print("  • Discoveries: 'Found 10.10.10.5 is a Domain Controller'")
        print("  • Findings: 'Ports 80, 443, 445 are open'")
        print("  • Credentials: 'Username: admin, Password: P@ssw0rd'")
        
        print("\n" + "─" * 60)
        print("💡 QUICK TIP:")
        print("─" * 60)
        import random
        print(f"  {random.choice(QUICK_TIPS)}")
        
        # Tool support info
        print(TOOL_SUPPORT)
        
        print("  Type '/help <command>' for detailed usage.")
        print("═" * 60 + "\n")
    
    def _show_command_help(self, cmd_name: str):
        """Display detailed help for a specific command."""
        # Normalize command name
        if not cmd_name.startswith('/'):
            cmd_name = '/' + cmd_name
        
        if cmd_name not in COMMANDS:
            print(f"\n❌ Unknown command: {cmd_name}")
            print("   Type '/help' to see all available commands.\n")
            return
        
        info = COMMANDS[cmd_name]
        
        print("\n" + "─" * 60)
        print(f"📖 {cmd_name} - {info['short']}")
        print("─" * 60)
        
        print(f"\n  Usage: {info['usage']}")
        
        if 'aliases' in info:
            print(f"  Aliases: {', '.join(info['aliases'])}")
        
        print(f"\n  {info['description']}")
        
        if 'examples' in info:
            print("\n  Examples:")
            for ex in info['examples']:
                print(f"    {ex}")
        
        print("─" * 60 + "\n")
