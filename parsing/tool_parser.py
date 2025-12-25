"""
Tool Output Parser

Parses raw output from security tools like nmap, rustscan, gobuster, wpscan.
Extracts structured data and stores raw output for reference.

Supported Tools:
- nmap: Port scans, service detection, OS fingerprinting
- rustscan: Fast port scans
- gobuster/dirbuster: Directory enumeration
- wpscan: WordPress scanning
- nikto: Web vulnerability scanning

Usage:
    parser = ToolOutputParser(project_name)
    result = parser.parse(raw_output)
    # result = {
    #     'tool': 'nmap',
    #     'discoveries': [...],
    #     'raw_file': 'tool_outputs/nmap_20231225_120000.txt'
    # }
"""

import re
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from core import config


class ToolOutputParser:
    """
    Parses raw output from security tools and extracts structured data.
    """
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.tool_outputs_dir = f"{config.PROJECTS_DIR}/{project_name}/tool_outputs"
        os.makedirs(self.tool_outputs_dir, exist_ok=True)
    
    def parse(self, raw_output: str) -> Optional[Dict]:
        """
        Parse raw tool output.
        
        Returns:
            Dict with 'tool', 'discoveries', 'raw_file', 'summary'
            or None if not recognized as tool output
        """
        # Detect which tool
        tool = self._detect_tool(raw_output)
        if not tool:
            return None
        
        # Save raw output
        raw_file = self._save_raw_output(tool, raw_output)
        
        # Parse based on tool
        discoveries = []
        if tool == 'nmap':
            discoveries = self._parse_nmap(raw_output)
        elif tool == 'rustscan':
            discoveries = self._parse_rustscan(raw_output)
        elif tool in ['gobuster', 'dirbuster', 'feroxbuster']:
            discoveries = self._parse_gobuster(raw_output)
        elif tool == 'wpscan':
            discoveries = self._parse_wpscan(raw_output)
        elif tool == 'nikto':
            discoveries = self._parse_nikto(raw_output)
        
        return {
            'tool': tool,
            'discoveries': discoveries,
            'raw_file': raw_file,
            'summary': self._generate_summary(tool, discoveries)
        }
    
    def _detect_tool(self, output: str) -> Optional[str]:
        """Detect which tool generated the output."""
        output_lower = output.lower()
        
        # Nmap detection
        if 'nmap scan report' in output_lower or 'starting nmap' in output_lower:
            return 'nmap'
        
        # Rustscan detection
        if 'rustscan' in output_lower or ('open' in output_lower and '->' in output):
            return 'rustscan'
        
        # Gobuster/dirbuster detection
        if 'gobuster' in output_lower or 'dirbuster' in output_lower:
            return 'gobuster'
        if 'feroxbuster' in output_lower:
            return 'feroxbuster'
        if re.search(r'status:\s*\d{3}', output_lower):
            return 'gobuster'
        
        # WPScan detection
        if 'wpscan' in output_lower or 'wordpress' in output_lower:
            return 'wpscan'
        
        # Nikto detection
        if 'nikto' in output_lower:
            return 'nikto'
        
        return None
    
    def _save_raw_output(self, tool: str, output: str) -> str:
        """Save raw output to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{tool}_{timestamp}.txt"
        filepath = f"{self.tool_outputs_dir}/{filename}"
        
        with open(filepath, 'w') as f:
            f.write(output)
        
        return filepath
    
    def _parse_nmap(self, output: str) -> List[Dict]:
        """Parse nmap output for ports, services, versions."""
        discoveries = []
        
        # Extract target IP
        ip_match = re.search(r'Nmap scan report for (?:[\w.-]+\s+\()?(\d+\.\d+\.\d+\.\d+)', output)
        target_ip = ip_match.group(1) if ip_match else None
        
        if target_ip:
            discoveries.append({
                'type': 'ip_address',
                'value': target_ip,
                'context': 'scanned',
                'source': 'nmap'
            })
        
        # Extract open ports with services
        # Matches: 80/tcp   open  http    Apache httpd 2.4.41
        port_pattern = r'(\d+)/(tcp|udp)\s+open\s+(\S+)(?:\s+(.+?))?(?:\n|$)'
        for match in re.finditer(port_pattern, output, re.IGNORECASE):
            port = match.group(1)
            protocol = match.group(2)
            service = match.group(3)
            version = match.group(4).strip() if match.group(4) else None
            
            discoveries.append({
                'type': 'open_port',
                'value': port,
                'context': 'open',
                'protocol': protocol,
                'source': 'nmap'
            })
            
            discoveries.append({
                'type': 'service',
                'value': service.upper(),
                'context': 'service',
                'port': port,
                'version': version,
                'source': 'nmap'
            })
        
        # Extract OS detection
        os_match = re.search(r'OS details?:\s*(.+?)(?:\n|$)', output)
        if os_match:
            discoveries.append({
                'type': 'os',
                'value': os_match.group(1).strip(),
                'context': 'detected',
                'source': 'nmap'
            })
        
        return discoveries
    
    def _parse_rustscan(self, output: str) -> List[Dict]:
        """Parse rustscan output for open ports."""
        discoveries = []
        
        # Extract IP
        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', output)
        if ip_match:
            discoveries.append({
                'type': 'ip_address',
                'value': ip_match.group(1),
                'context': 'scanned',
                'source': 'rustscan'
            })
        
        # Rustscan format: Open 10.10.10.5:445
        # Or: 10.10.10.5 -> [22,80,443,445]
        port_pattern = r'(?:Open\s+[\d.]+:(\d+)|\[[\d,\s]*(\d+)[\d,\s]*\])'
        for match in re.finditer(port_pattern, output):
            port = match.group(1) or match.group(2)
            if port:
                discoveries.append({
                    'type': 'open_port',
                    'value': port,
                    'context': 'open',
                    'source': 'rustscan'
                })
        
        # Also match list format: [22, 80, 443]
        list_match = re.search(r'\[([\d,\s]+)\]', output)
        if list_match:
            ports = re.findall(r'\d+', list_match.group(1))
            for port in ports:
                if not any(d['value'] == port and d['type'] == 'open_port' for d in discoveries):
                    discoveries.append({
                        'type': 'open_port',
                        'value': port,
                        'context': 'open',
                        'source': 'rustscan'
                    })
        
        return discoveries
    
    def _parse_gobuster(self, output: str) -> List[Dict]:
        """Parse gobuster/dirbuster output for directories."""
        discoveries = []
        
        # Gobuster format: /admin (Status: 200) [Size: 1234]
        dir_pattern = r'(/[\w./-]+)\s+\(Status:\s*(\d+)\)'
        for match in re.finditer(dir_pattern, output):
            path = match.group(1)
            status = match.group(2)
            
            discoveries.append({
                'type': 'directory',
                'value': path,
                'context': f'status_{status}',
                'status_code': status,
                'source': 'gobuster'
            })
        
        # Also match feroxbuster format: 200      GET    12l      45w    1234c http://10.10.10.5/admin
        ferox_pattern = r'(\d{3})\s+\w+\s+\d+\w?\s+\d+\w?\s+\d+\w?\s+(https?://[^\s]+)'
        for match in re.finditer(ferox_pattern, output):
            status = match.group(1)
            url = match.group(2)
            
            discoveries.append({
                'type': 'url',
                'value': url,
                'context': f'status_{status}',
                'status_code': status,
                'source': 'feroxbuster'
            })
        
        return discoveries
    
    def _parse_wpscan(self, output: str) -> List[Dict]:
        """Parse wpscan output for WordPress info."""
        discoveries = []
        
        # WordPress version
        wp_version = re.search(r'WordPress version (\d+\.\d+(?:\.\d+)?)', output)
        if wp_version:
            discoveries.append({
                'type': 'service',
                'value': f'WordPress {wp_version.group(1)}',
                'context': 'version',
                'source': 'wpscan'
            })
        
        # Plugins
        plugin_pattern = r'\[!\] Title: ([^\n]+)'
        for match in re.finditer(plugin_pattern, output):
            discoveries.append({
                'type': 'vulnerability',
                'value': match.group(1).strip(),
                'context': 'wordpress_plugin',
                'source': 'wpscan'
            })
        
        # Usernames
        user_pattern = r'(?:User\(s\)|Username).*?:\s*(\w+)'
        for match in re.finditer(user_pattern, output, re.IGNORECASE):
            discoveries.append({
                'type': 'username',
                'value': match.group(1),
                'context': 'wordpress_user',
                'source': 'wpscan'
            })
        
        return discoveries
    
    def _parse_nikto(self, output: str) -> List[Dict]:
        """Parse nikto output for web vulnerabilities."""
        discoveries = []
        
        # Target
        target_match = re.search(r'Target IP:\s*(\d+\.\d+\.\d+\.\d+)', output)
        if target_match:
            discoveries.append({
                'type': 'ip_address',
                'value': target_match.group(1),
                'context': 'scanned',
                'source': 'nikto'
            })
        
        # Server
        server_match = re.search(r'Server:\s*(.+?)(?:\n|$)', output)
        if server_match:
            discoveries.append({
                'type': 'service',
                'value': server_match.group(1).strip(),
                'context': 'web_server',
                'source': 'nikto'
            })
        
        # Vulnerabilities (lines starting with +)
        vuln_pattern = r'\+\s*(.+?):\s*(.+?)(?:\n|$)'
        for match in re.finditer(vuln_pattern, output):
            if 'OSVDB' in match.group(1) or 'CVE' in match.group(1):
                discoveries.append({
                    'type': 'vulnerability',
                    'value': f"{match.group(1)}: {match.group(2)[:100]}",
                    'context': 'web_vuln',
                    'source': 'nikto'
                })
        
        return discoveries
    
    def _generate_summary(self, tool: str, discoveries: List[Dict]) -> str:
        """Generate a human-readable summary."""
        if not discoveries:
            return f"No significant findings from {tool}"
        
        # Count by type
        type_counts = {}
        for d in discoveries:
            t = d['type']
            type_counts[t] = type_counts.get(t, 0) + 1
        
        parts = [f"📊 {tool.upper()} Results:"]
        for dtype, count in type_counts.items():
            icon = {
                'ip_address': '🎯',
                'open_port': '🔌',
                'service': '⚙️',
                'directory': '📁',
                'url': '🌐',
                'vulnerability': '🚨',
                'username': '👤',
                'os': '💻'
            }.get(dtype, '📍')
            parts.append(f"  {icon} {dtype}: {count}")
        
        return '\n'.join(parts)


def is_likely_tool_output(text: str) -> bool:
    """
    Quick check if text looks like tool output (multi-line, technical content).
    Used to decide whether to attempt parsing.
    """
    lines = text.strip().split('\n')
    
    # Tool output is usually multi-line
    if len(lines) < 3:
        return False
    
    # Check for common tool patterns
    indicators = [
        'nmap', 'rustscan', 'gobuster', 'wpscan', 'nikto',
        'scan report', 'open', '/tcp', '/udp', 'status:',
        'starting', 'discovered', 'port', 'host'
    ]
    
    text_lower = text.lower()
    matches = sum(1 for i in indicators if i in text_lower)
    
    return matches >= 2
