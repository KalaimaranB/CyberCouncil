"""
Discovery Parser Module

Extracts key reconnaissance discoveries from user statements using regex patterns.
Automatically identifies and classifies:
- IP addresses with contextual classification (DC, target, server)
- Credentials (usernames, passwords, hashes)
- Infrastructure (domains, hostnames, ports)
- Services (SMB, RDP, SSH, HTTP, etc.)
- Vulnerabilities (CVEs, named exploits like MS17-010)

Used by the auto-logging system to capture critical information without manual input.

Usage:
    parser = DiscoveryParser()
    discoveries = parser.extract_discoveries("I found DC at 10.10.10.5")
    # Returns: [{'type': 'ip_address', 'value': '10.10.10.5', 'context': 'domain_controller', ...}]

Author: CyberCouncil Project
"""

import re
from typing import List, Dict, Optional

class DiscoveryParser:
    """
    Parses user statements to extract key reconnaissance discoveries.
    Automatically identifies IPs, credentials, hostnames, ports, and vulnerabilities.
    """
    
    def __init__(self):
        # Regex patterns for common discoveries
        self.patterns = {
            'ip_address': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
            'hostname': r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b',
            'port': r'\bport[s]?\s+(\d{1,5})\b',
            'open_port': r'\b(\d{1,5})\s+(?:is\s+)?open\b',
            'username': r'\b(?:user(?:name)?|login|account)\s*(?:is|:|=)\s*([a-zA-Z0-9_-]+)\b',
            'password': r'\b(?:pass(?:word)?|pwd|cred(?:ential)?)\s*(?:is|:|=|found)\s*[:\s]*([^\s,;]+)\b',
            'hash': r'\b(?:hash|NTLM|MD5|SHA)\s*[:\s]*([a-fA-F0-9]{32,64})\b',
            'domain': r'\b(?:domain|DC)\s+(?:is\s+)?([a-zA-Z0-9][a-zA-Z0-9-]*)\b',
            'service': r'\b((?:SMB|RDP|SSH|HTTP|FTP|LDAP|Kerberos|DNS))\b',
            'vulnerability': r'\b(MS\d{2}-\d{3}|CVE-\d{4}-\d{4,}|EternalBlue|BlueKeep)\b',
        }
    
    def extract_discoveries(self, user_input: str) -> List[Dict[str, str]]:
        """
        Extract all discoveries from user input.
        Returns list of discovery dictionaries with type, value, and context.
        """
        discoveries = []
        user_lower = user_input.lower()
        
        # IP Address detection
        ip_matches = re.finditer(self.patterns['ip_address'], user_input)
        for match in ip_matches:
            ip = match.group()
            # Skip localhost and special IPs
            if not ip.startswith(('127.', '0.0.', '255.255')):
                # Determine context (found, target, DC, etc.)
                context = self._determine_ip_context(user_input, ip)
                discoveries.append({
                    'type': 'ip_address',
                    'value': ip,
                    'context': context,
                    'raw': user_input
                })
        
        # Hostname detection
        hostname_matches = re.finditer(self.patterns['hostname'], user_input)
        for match in hostname_matches:
            hostname = match.group()
            # Skip common false positives
            if not hostname.endswith(('.com', '.net', '.org')) or 'local' in hostname:
                discoveries.append({
                    'type': 'hostname',
                    'value': hostname,
                    'context': 'discovered',
                    'raw': user_input
                })
        
        # Port detection
        port_matches = re.finditer(self.patterns['port'], user_lower, re.IGNORECASE)
        for match in port_matches:
            port = match.group(1)
            discoveries.append({
                'type': 'port',
                'value': port,
                'context': 'mentioned',
                'raw': user_input
            })
        
        # Open port detection
        open_port_matches = re.finditer(self.patterns['open_port'], user_lower, re.IGNORECASE)
        for match in open_port_matches:
            port = match.group(1)
            discoveries.append({
                'type': 'open_port',
                'value': port,
                'context': 'open',
                'raw': user_input
            })
        
        # Username detection
        username_matches = re.finditer(self.patterns['username'], user_lower, re.IGNORECASE)
        for match in username_matches:
            username = match.group(1)
            discoveries.append({
                'type': 'username',
                'value': username,
                'context': 'credential',
                'raw': user_input
            })
        
        # Password detection
        password_matches = re.finditer(self.patterns['password'], user_input, re.IGNORECASE)
        for match in password_matches:
            password = match.group(1)
            discoveries.append({
                'type': 'password',
                'value': password,
                'context': 'credential',
                'raw': user_input
            })
        
        # Hash detection
        hash_matches = re.finditer(self.patterns['hash'], user_input, re.IGNORECASE)
        for match in hash_matches:
            hash_val = match.group(1)
            discoveries.append({
                'type': 'hash',
                'value': hash_val,
                'context': 'credential',
                'raw': user_input
            })
        
        # Domain detection
        domain_matches = re.finditer(self.patterns['domain'], user_input, re.IGNORECASE)
        for match in domain_matches:
            domain = match.group(1)
            discoveries.append({
                'type': 'domain',
                'value': domain,
                'context': 'infrastructure',
                'raw': user_input
            })
        
        # Service detection
        service_matches = re.finditer(self.patterns['service'], user_input, re.IGNORECASE)
        for match in service_matches:
            service = match.group(1)
            discoveries.append({
                'type': 'service',
                'value': service.upper(),
                'context': 'service',
                'raw': user_input
            })
        
        # Vulnerability detection
        vuln_matches = re.finditer(self.patterns['vulnerability'], user_input, re.IGNORECASE)
        for match in vuln_matches:
            vuln = match.group(1)
            discoveries.append({
                'type': 'vulnerability',
                'value': vuln.upper(),
                'context': 'vulnerability',
                'raw': user_input
            })
        
        return discoveries
    
    def _determine_ip_context(self, text: str, ip: str) -> str:
        """Determine the context/role of an IP address from surrounding text"""
        text_lower = text.lower()
        
        # Check for keywords around the IP
        if 'dc' in text_lower or 'domain controller' in text_lower:
            return 'domain_controller'
        elif 'found' in text_lower or 'discovered' in text_lower:
            return 'discovered'
        elif 'target' in text_lower:
            return 'target'
        elif 'gateway' in text_lower or 'router' in text_lower:
            return 'gateway'
        elif 'server' in text_lower:
            return 'server'
        else:
            return 'mentioned'
    
    def format_discovery_log(self, discovery: Dict[str, str]) -> str:
        """Format a discovery for logging to active record"""
        type_map = {
            'ip_address': '🎯 IP',
            'hostname': '🖥️ Hostname',
            'port': '🔌 Port',
            'open_port': '✅ Open Port',
            'username': '👤 Username',
            'password': '🔑 Password',
            'hash': '🔐 Hash',
            'domain': '🏰 Domain',
            'service': '⚙️ Service',
            'vulnerability': '🚨 Vulnerability',
        }
        
        icon = type_map.get(discovery['type'], '📍')
        value = discovery['value']
        context = discovery.get('context', '')
        
        if context and context != 'mentioned':
            return f"{icon} [{context.upper()}]: {value}"
        else:
            return f"{icon}: {value}"


# Convenience function
def extract_discoveries(user_input: str) -> List[Dict[str, str]]:
    """Quick function to extract discoveries"""
    parser = DiscoveryParser()
    return parser.extract_discoveries(user_input)
