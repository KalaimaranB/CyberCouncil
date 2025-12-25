"""
Configuration Manager

Handles user configuration from ~/.council/config.yaml
Provides defaults and validation.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any


# Default configuration
DEFAULTS = {
    'default_wordlist': '/usr/share/wordlists/rockyou.txt',
    'default_project': None,  # None = show menu
    'api_token': None,  # None = no auth
    'api_port': 5051,
    'theme': 'dark',
    'auto_save': True,
    'max_pending_logs': 50,
    'hashcat_timeout': 300,  # 5 minutes
}

CONFIG_DIR = Path.home() / '.council'
CONFIG_FILE = CONFIG_DIR / 'config.yaml'


class ConfigManager:
    """
    Manages user configuration with sensible defaults.
    """
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._config = None
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load config from file or create defaults."""
        config = DEFAULTS.copy()
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    user_config = yaml.safe_load(f) or {}
                    config.update(user_config)
            except Exception as e:
                print(f"⚠️  Error loading config: {e}")
        
        return config
    
    def save(self):
        """Save current config to file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set config value and save."""
        self._config[key] = value
        self.save()
    
    def get_wordlist(self) -> Optional[str]:
        """Get default wordlist path if it exists."""
        path = self._config.get('default_wordlist')
        if path and os.path.exists(os.path.expanduser(path)):
            return os.path.expanduser(path)
        return None
    
    def get_api_token(self) -> Optional[str]:
        """Get API token for authentication."""
        return self._config.get('api_token')
    
    def generate_token(self) -> str:
        """Generate a new API token."""
        import secrets
        token = secrets.token_urlsafe(32)
        self.set('api_token', token)
        return token
    
    @property
    def all(self) -> Dict[str, Any]:
        """Get all config values."""
        return self._config.copy()


# Global config instance
config = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global config instance."""
    return ConfigManager()


def create_default_config():
    """Create default config file if it doesn't exist."""
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        default_content = """# CyberCouncil Configuration
# https://github.com/your-repo/cybercouncil

# Default wordlist for hash cracking
default_wordlist: /usr/share/wordlists/rockyou.txt

# Default project to open (null = show menu)
default_project: null

# API authentication token (null = no auth, generate with /server token)
api_token: null

# API server port
api_port: 5051

# Theme (dark/light)
theme: dark

# Auto-save discoveries
auto_save: true

# Maximum pending logs before warning
max_pending_logs: 50

# Hashcat timeout in seconds
hashcat_timeout: 300
"""
        with open(CONFIG_FILE, 'w') as f:
            f.write(default_content)
        
        print(f"📝 Created config at: {CONFIG_FILE}")
