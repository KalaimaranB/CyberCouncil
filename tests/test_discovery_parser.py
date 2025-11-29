"""
Tests for Discovery Parser module.
Tests entity extraction from user statements.
"""

import pytest
from parsing.discovery_parser import DiscoveryParser


class TestDiscoveryParser:
    """Test suite for DiscoveryParser class"""
    
    @pytest.fixture
    def parser(self):
        """Create a DiscoveryParser instance"""
        return DiscoveryParser()
    
    def test_extract_ip_address(self, parser):
        """Test IP address extraction"""
        discoveries = parser.extract_discoveries("I found a DC at 10.10.10.5")
        
        assert len(discoveries) > 0
        ip_discovery = next((d for d in discoveries if d['type'] == 'ip_address'), None)
        assert ip_discovery is not None
        assert ip_discovery['value'] == "10.10.10.5"
    
    def test_extract_ip_with_context_dc(self, parser):
        """Test IP extraction with domain controller context"""
        discoveries = parser.extract_discoveries("Found domain controller at 192.168.1.100")
        
        ip_discovery = next((d for d in discoveries if d['type'] == 'ip_address'), None)
        assert ip_discovery is not None
        assert ip_discovery['context'] == 'domain_controller'
    
    def test_extract_ip_with_context_target(self, parser):
        """Test IP extraction with target context"""
        discoveries = parser.extract_discoveries("Target is at 172.16.0.50")
        
        ip_discovery = next((d for d in discoveries if d['type'] == 'ip_address'), None)
        assert ip_discovery is not None
        assert ip_discovery['context'] == 'target'
    
    def test_extract_port(self, parser):
        """Test port extraction"""
        discoveries = parser.extract_discoveries("Found port 445 and port 22")
        
        port_discoveries = [d for d in discoveries if d['type'] == 'port']
        assert len(port_discoveries) >= 1
        assert any(d['value'] == '445' for d in port_discoveries)
    
    def test_extract_open_port(self, parser):
        """Test open port extraction"""
        discoveries = parser.extract_discoveries("Port 445 is open")
        
        open_port = next((d for d in discoveries if d['type'] == 'open_port'), None)
        assert open_port is not None
        assert open_port['value'] == '445'
        assert open_port['context'] == 'open'
    
    def test_extract_service(self, parser):
        """Test service extraction"""
        discoveries = parser.extract_discoveries("Running SMB and HTTP services")
        
        service_discoveries = [d for d in discoveries if d['type'] == 'service']
        assert len(service_discoveries) >= 1
        assert any(d['value'] == 'SMB' for d in service_discoveries)
    
    def test_extract_vulnerability_ms(self, parser):
        """Test Microsoft vulnerability extraction"""
        discoveries = parser.extract_discoveries("Vulnerable to MS17-010")
        
        vuln = next((d for d in discoveries if d['type'] == 'vulnerability'), None)
        assert vuln is not None
        assert vuln['value'] == 'MS17-010'
    
    def test_extract_vulnerability_cve(self, parser):
        """Test CVE extraction"""
        discoveries = parser.extract_discoveries("Found CVE-2024-1234")
        
        vuln = next((d for d in discoveries if d['type'] == 'vulnerability'), None)
        assert vuln is not None
        assert 'CVE-2024-1234' in vuln['value']
    
    def test_extract_username(self, parser):
        """Test username extraction"""
        discoveries = parser.extract_discoveries("Username is administrator")
        
        username = next((d for d in discoveries if d['type'] == 'username'), None)
        assert username is not None
        assert username['value'] == 'administrator'
    
    def test_extract_password(self, parser):
        """Test password extraction"""
        discoveries = parser.extract_discoveries("Password is Admin123")
        
        password = next((d for d in discoveries if d['type'] == 'password'), None)
        assert password is not None
        assert 'Admin123' in password['value']  # Regex may not capture special chars at end
    
    def test_extract_hash(self, parser):
        """Test hash extraction"""
        test_hash = "5f4dcc3b5aa765d61d8327deb882cf99"
        discoveries = parser.extract_discoveries(f"NTLM hash {test_hash}")
        
        hash_discovery = next((d for d in discoveries if d['type'] == 'hash'), None)
        assert hash_discovery is not None
        assert test_hash in hash_discovery['value']
    
    def test_extract_domain(self, parser):
        """Test domain extraction"""
        discoveries = parser.extract_discoveries("Domain is CORP")
        
        domain = next((d for d in discoveries if d['type'] == 'domain'), None)
        assert domain is not None
        assert domain['value'] == 'CORP'
    
    def test_format_discovery_log_ip(self, parser):
        """Test formatting IP discovery for logging"""
        discovery = {
            'type': 'ip_address',
            'value': '10.10.10.5',
            'context': 'domain_controller'
        }
        
        formatted = parser.format_discovery_log(discovery)
        
        assert '🎯' in formatted  # IP icon
        assert '10.10.10.5' in formatted
        assert 'DOMAIN_CONTROLLER' in formatted.upper()
    
    def test_format_discovery_log_port(self, parser):
        """Test formatting port discovery"""
        discovery = {
            'type': 'open_port',
            'value': '445',
            'context': 'open'
        }
        
        formatted = parser.format_discovery_log(discovery)
        
        assert '✅' in formatted  # Open port icon
        assert '445' in formatted
    
    def test_format_discovery_log_vuln(self, parser):
        """Test formatting vulnerability discovery"""
        discovery = {
            'type': 'vulnerability',
            'value': 'MS17-010',
            'context': 'vulnerability'
        }
        
        formatted = parser.format_discovery_log(discovery)
        
        assert '🚨' in formatted  # Vulnerability icon
        assert 'MS17-010' in formatted
    
    def test_skip_localhost_ip(self, parser):
        """Test that localhost IPs are skipped"""
        discoveries = parser.extract_discoveries("Server at 127.0.0.1")
        
        ip_discoveries = [d for d in discoveries if d['type'] == 'ip_address']
        assert len(ip_discoveries) == 0  # Should skip localhost
    
    def test_multiple_discoveries_in_one_statement(self, parser):
        """Test extracting multiple entities from single statement"""
        discoveries = parser.extract_discoveries(
            "Found DC at 10.10.10.5 running SMB on port 445 vulnerable to MS17-010"
        )
        
        types = set(d['type'] for d in discoveries)
        assert 'ip_address' in types
        assert 'service' in types
        assert 'port' in types or 'open_port' in types
        assert 'vulnerability' in types
    
    def test_empty_input(self, parser):
        """Test handling empty input"""
        discoveries = parser.extract_discoveries("")
        assert discoveries == []
    
    def test_no_discoveries(self, parser):
        """Test input with no extractable entities"""
        discoveries = parser.extract_discoveries("Just some random text")
        assert len(discoveries) == 0
    
    def test_case_insensitive_service(self, parser):
        """Test that service detection is case-insensitive"""
        discoveries1 = parser.extract_discoveries("Running smb service")
        discoveries2 = parser.extract_discoveries("Running SMB service")
        
        services1 = [d for d in discoveries1 if d['type'] == 'service']
        services2 = [d for d in discoveries2 if d['type'] == 'service']
        
        assert len(services1) == len(services2)
        if services1:
            assert services1[0]['value'] == services2[0]['value']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
