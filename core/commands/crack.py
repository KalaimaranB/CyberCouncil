"""
Crack Command

Hash cracking with automatic type detection.
Uses hashcat with GPU acceleration.
"""

from core.commands.base import Command
from utils.hash_cracker import HashCracker


class CrackCommand(Command):
    """
    Crack hashes using hashcat with auto-detection.
    
    Usage:
        /crack HASH
        /crack --wordlist /path/to/wordlist.txt HASH
        /crack --mode 1000 HASH
        /crack --types  (list supported hash types)
    """
    
    def execute(self, context, args: str = "") -> bool:
        """
        Execute crack command.
        
        Args:
            context: CyberCouncil instance
            args: Hash and optional flags
        """
        if not args.strip():
            self._show_usage()
            return False
        
        args = args.strip()
        
        # Handle --types flag
        if args == '--types' or args == '-t':
            cracker = HashCracker()
            print(cracker.list_supported_types())
            return True
        
        # Parse arguments
        wordlist = None
        mode = None
        hash_string = None
        
        parts = args.split()
        i = 0
        while i < len(parts):
            if parts[i] in ['--wordlist', '-w'] and i + 1 < len(parts):
                wordlist = parts[i + 1]
                i += 2
            elif parts[i] in ['--mode', '-m'] and i + 1 < len(parts):
                try:
                    mode = int(parts[i + 1])
                    i += 2
                except ValueError:
                    print(f"❌ Invalid mode: {parts[i + 1]}")
                    return False
            else:
                hash_string = parts[i]
                i += 1
        
        if not hash_string:
            self._show_usage()
            return False
        
        # Initialize cracker
        project = context.current_project if hasattr(context, 'current_project') else None
        cracker = HashCracker(project_name=project)
        
        print(f"\n🔐 Cracking: {hash_string[:32]}...")
        
        # Crack the hash
        result = cracker.crack(
            hash_string=hash_string,
            wordlist=wordlist,
            mode=mode
        )
        
        # Display result
        if result['status'] == 'cracked':
            print("\n" + "═" * 50)
            print("🎉 CRACKED!")
            print("═" * 50)
            print(f"  Hash:     {result['hash'][:40]}...")
            print(f"  Password: {result['password']}")
            print("═" * 50 + "\n")
            
            # Auto-log the credential
            if hasattr(context, 'logger') and project:
                context.logger.auto_log_discovery(project, {
                    'type': 'password',
                    'value': result['password'],
                    'context': 'cracked',
                    'raw': f"Cracked hash: {result['hash']}"
                })
                print("📍 Credential logged to project!")
            
            return True
        
        elif result['status'] == 'not_cracked':
            print(f"\n❌ {result['message']}")
            print("   Try: /crack --wordlist /path/to/bigger.txt HASH")
            return False
        
        else:
            print(f"\n❌ {result.get('message', 'Unknown error')}")
            return False
    
    def _show_usage(self):
        """Display usage help."""
        print("""
🔐 HASH CRACKING

Usage:
  /crack HASH                         Auto-detect and crack
  /crack --wordlist /path HASH        Use custom wordlist
  /crack --mode 1000 HASH             Force hashcat mode
  /crack --types                      List supported hash types

Examples:
  /crack 31d6cfe0d16ae931b73c59d7e0c089c0
  /crack -w /usr/share/wordlists/rockyou.txt $krb5tgs$23$*...
  /crack -m 0 5f4dcc3b5aa765d61d8327deb882cf99
""")
