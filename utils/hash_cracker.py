"""
Hash Cracker Module

Wrapper for hashcat with automatic hash type detection.
Handles common hash formats: NTLM, MD5, SHA, bcrypt, etc.

Usage:
    cracker = HashCracker()
    result = cracker.crack("aad3b435...", wordlist="/path/to/rockyou.txt")
"""

import re
import subprocess
import os
import shutil
from typing import Optional, Dict, Tuple
from datetime import datetime
from core import config


# Hash type patterns and hashcat modes
HASH_PATTERNS = {
    # Windows
    'ntlm': {
        'pattern': r'^[a-fA-F0-9]{32}$',
        'mode': 1000,
        'name': 'NTLM',
        'example': '31d6cfe0d16ae931b73c59d7e0c089c0'
    },
    'ntlm_with_user': {
        'pattern': r'^[^:]+:[0-9]+:[a-fA-F0-9]{32}:[a-fA-F0-9]{32}',
        'mode': 1000,
        'name': 'NTLM (with user)',
        'example': 'user:1001:aad3b...:31d6c...'
    },
    'lm': {
        'pattern': r'^[a-fA-F0-9]{32}$',  # Same as NTLM, but older
        'mode': 3000,
        'name': 'LM',
        'example': 'aad3b435b51404ee'
    },
    
    # Standard hashes
    'md5': {
        'pattern': r'^[a-fA-F0-9]{32}$',
        'mode': 0,
        'name': 'MD5',
        'example': '5f4dcc3b5aa765d61d8327deb882cf99'
    },
    'sha1': {
        'pattern': r'^[a-fA-F0-9]{40}$',
        'mode': 100,
        'name': 'SHA-1',
        'example': '5baa61e4c9b93f3f...'
    },
    'sha256': {
        'pattern': r'^[a-fA-F0-9]{64}$',
        'mode': 1400,
        'name': 'SHA-256',
        'example': '5e884898da28047d...'
    },
    'sha512': {
        'pattern': r'^[a-fA-F0-9]{128}$',
        'mode': 1700,
        'name': 'SHA-512',
        'example': 'b109f3bbbc244eb8...'
    },
    
    # Unix crypt formats
    'md5crypt': {
        'pattern': r'^\$1\$[./a-zA-Z0-9]{8}\$[./a-zA-Z0-9]{22}$',
        'mode': 500,
        'name': 'MD5crypt (Unix)',
        'example': '$1$salt$hash...'
    },
    'sha256crypt': {
        'pattern': r'^\$5\$[./a-zA-Z0-9]+\$[./a-zA-Z0-9]{43}$',
        'mode': 7400,
        'name': 'SHA256crypt (Unix)',
        'example': '$5$salt$hash...'
    },
    'sha512crypt': {
        'pattern': r'^\$6\$[./a-zA-Z0-9]+\$[./a-zA-Z0-9]{86}$',
        'mode': 1800,
        'name': 'SHA512crypt (Unix)',
        'example': '$6$salt$hash...'
    },
    
    # bcrypt
    'bcrypt': {
        'pattern': r'^\$2[aby]?\$\d+\$[./a-zA-Z0-9]{53}$',
        'mode': 3200,
        'name': 'bcrypt',
        'example': '$2a$10$...'
    },
    
    # Kerberos
    'kerberos_tgs': {
        'pattern': r'^\$krb5tgs\$',
        'mode': 13100,
        'name': 'Kerberos 5 TGS-REP (etype 23)',
        'example': '$krb5tgs$23$*user...'
    },
    'kerberos_asrep': {
        'pattern': r'^\$krb5asrep\$',
        'mode': 18200,
        'name': 'Kerberos 5 AS-REP (etype 23)',
        'example': '$krb5asrep$23$user...'
    },
    
    # Web
    'django_sha256': {
        'pattern': r'^pbkdf2_sha256\$',
        'mode': 10000,
        'name': 'Django (PBKDF2-SHA256)',
        'example': 'pbkdf2_sha256$...'
    },
    
    # Network
    'netntlmv2': {
        'pattern': r'^[^:]+::[^:]+:[a-fA-F0-9]+:[a-fA-F0-9]+:[a-fA-F0-9]+$',
        'mode': 5600,
        'name': 'NetNTLMv2',
        'example': 'user::domain:challenge:response:blob'
    },
}

# Common wordlist paths
DEFAULT_WORDLISTS = [
    '/usr/share/wordlists/rockyou.txt',
    '/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt',
    '~/wordlists/rockyou.txt',
    './wordlists/rockyou.txt',
]


class HashCracker:
    """
    Hashcat wrapper with auto-detection and friendly interface.
    """
    
    def __init__(self, project_name: str = None):
        self.project_name = project_name
        self.hashcat_path = self._find_hashcat()
        self.output_dir = None
        
        if project_name:
            self.output_dir = f"{config.PROJECTS_DIR}/{project_name}/cracked"
            os.makedirs(self.output_dir, exist_ok=True)
    
    def _find_hashcat(self) -> Optional[str]:
        """Find hashcat binary."""
        return shutil.which('hashcat')
    
    def detect_hash_type(self, hash_string: str) -> Optional[Dict]:
        """
        Auto-detect hash type from the hash string.
        
        Returns:
            Dict with 'mode', 'name', 'pattern' or None if unknown
        """
        hash_string = hash_string.strip()
        
        # Try each pattern
        for hash_type, info in HASH_PATTERNS.items():
            if re.match(info['pattern'], hash_string):
                return {
                    'type': hash_type,
                    'mode': info['mode'],
                    'name': info['name']
                }
        
        # Special case: 32 hex chars could be MD5 or NTLM
        if re.match(r'^[a-fA-F0-9]{32}$', hash_string):
            return {
                'type': 'md5_or_ntlm',
                'mode': 1000,  # Default to NTLM (more common in pentesting)
                'name': 'NTLM (or MD5)',
                'note': 'Try mode 0 if NTLM fails'
            }
        
        return None
    
    def find_wordlist(self, custom_path: str = None) -> Optional[str]:
        """Find a valid wordlist path."""
        if custom_path:
            expanded = os.path.expanduser(custom_path)
            if os.path.exists(expanded):
                return expanded
        
        # Try default paths
        for path in DEFAULT_WORDLISTS:
            expanded = os.path.expanduser(path)
            if os.path.exists(expanded):
                return expanded
        
        return None
    
    def crack(self, hash_string: str, wordlist: str = None, 
              mode: int = None, rules: bool = True) -> Dict:
        """
        Crack a hash using hashcat.
        
        Args:
            hash_string: The hash to crack
            wordlist: Path to wordlist (auto-finds if not specified)
            mode: Hashcat mode (auto-detects if not specified)
            rules: Apply rules (slower but more effective)
            
        Returns:
            Dict with 'status', 'cracked', 'password', 'time'
        """
        if not self.hashcat_path:
            return {
                'status': 'error',
                'message': '❌ hashcat not found. Install with: brew install hashcat'
            }
        
        # Auto-detect hash type if mode not specified
        if mode is None:
            detected = self.detect_hash_type(hash_string)
            if detected:
                mode = detected['mode']
                print(f"🔍 Detected: {detected['name']} (mode {mode})")
            else:
                return {
                    'status': 'error',
                    'message': '❌ Could not detect hash type. Use /crack --mode NUM HASH'
                }
        
        # Find wordlist
        wordlist_path = self.find_wordlist(wordlist)
        if not wordlist_path:
            return {
                'status': 'error',
                'message': '❌ No wordlist found. Use /crack --wordlist /path HASH'
            }
        
        print(f"📚 Using wordlist: {wordlist_path}")
        
        # Create temp file for hash
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        hash_file = f"/tmp/council_hash_{timestamp}.txt"
        potfile = f"/tmp/council_pot_{timestamp}.txt"
        
        with open(hash_file, 'w') as f:
            f.write(hash_string + '\n')
        
        # Build hashcat command
        cmd = [
            self.hashcat_path,
            '-m', str(mode),
            '-a', '0',  # Dictionary attack
            hash_file,
            wordlist_path,
            '--potfile-path', potfile,
            '-O',  # Optimized kernels
            '--quiet'
        ]
        
        if rules:
            # Add best64 rules if available
            rules_path = '/usr/share/hashcat/rules/best64.rule'
            if os.path.exists(rules_path):
                cmd.extend(['-r', rules_path])
        
        print(f"⚡ Starting hashcat (GPU accelerated)...")
        
        try:
            # Run hashcat
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Check potfile for result
            if os.path.exists(potfile):
                with open(potfile, 'r') as f:
                    content = f.read().strip()
                    if content:
                        # Format: hash:password
                        parts = content.split(':')
                        if len(parts) >= 2:
                            password = ':'.join(parts[1:])
                            
                            # Save to project if available
                            if self.output_dir:
                                with open(f"{self.output_dir}/cracked_{timestamp}.txt", 'w') as out:
                                    out.write(f"Hash: {hash_string}\n")
                                    out.write(f"Password: {password}\n")
                            
                            return {
                                'status': 'cracked',
                                'hash': hash_string,
                                'password': password
                            }
            
            return {
                'status': 'not_cracked',
                'message': 'Hash not cracked with current wordlist'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'message': 'Cracking timed out (5 min limit). Try a smaller wordlist.'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error: {str(e)}'
            }
        finally:
            # Cleanup
            if os.path.exists(hash_file):
                os.remove(hash_file)
            if os.path.exists(potfile):
                os.remove(potfile)
    
    def list_supported_types(self) -> str:
        """Return formatted list of supported hash types."""
        output = ["📋 Supported Hash Types:\n"]
        output.append(f"{'Type':<20} {'Mode':<8} {'Example'}")
        output.append("-" * 60)
        
        for hash_type, info in HASH_PATTERNS.items():
            output.append(f"{info['name']:<20} {info['mode']:<8} {info['example'][:30]}...")
        
        return '\n'.join(output)
