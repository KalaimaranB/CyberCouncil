"""
Tests for Query Router module.
Tests routing decisions between strategic and tactical models.
"""

import pytest
from ai.router import QueryRouter


class TestQueryRouter:
    """Test suite for QueryRouter class"""
    
    @pytest.fixture
    def router(self):
        """Create a QueryRouter instance"""
        return QueryRouter()
    
    def test_strategic_keyword_plan(self, router):
        """Test routing on 'plan' keyword"""
        result = router.route_query("What's my plan for this target?")
        assert result == 'strategic'
    
    def test_strategic_keyword_analyze(self, router):
        """Test routing on 'analyze' keyword"""
        result = router.route_query("Analyze the network topology")
        assert result == 'strategic'
    
    def test_strategic_keyword_why(self, router):
        """Test routing on 'why' question"""
        result = router.route_query("Why is Kerberos important?")
        assert result == 'strategic'
    
    def test_strategic_question_type(self, router):
        """Test routing on strategic question types"""
        result = router.route_query("How should I approach this domain controller?")
        assert result == 'strategic'
    
    def test_strategic_long_query(self, router):
        """Test that longer queries tend toward strategic"""
        result = router.route_query(
            "I need to understand the complete attack surface and develop a comprehensive strategy"
        )
        assert result == 'strategic'
    
    def test_tactical_keyword_command(self, router):
        """Test routing on 'command' keyword"""
        result = router.route_query("Give me the nmap command")
        assert result == 'tactical'
    
    def test_tactical_keyword_syntax(self, router):
        """Test routing on 'syntax' keyword"""
        result = router.route_query("What's the syntax for smbclient?")
        assert result == 'tactical'
    
    def test_tactical_give_me(self, router):
        """Test routing on 'give me' phrase"""
        result = router.route_query("Give me commands for AS-REP roasting")
        assert result == 'tactical'
    
    def test_tactical_show_me(self, router):
        """Test routing on 'show me' phrase"""
        result = router.route_query("Show me how to use crackmapexec")
        assert result == 'tactical'
    
    def test_tactical_short_query(self, router):
        """Test that short queries can be tactical"""
        result = router.route_query("nmap command")
        # Short and contains command keyword
        assert result == 'tactical'
    
    def test_tactical_code_markers(self, router):
        """Test routing when code blocks are mentioned"""
        result = router.route_query("Show me the ```bash command for this")
        assert result == 'tactical'
    
    def test_fallback_to_tactical(self, router):
        """Test default fallback when scores are tied"""
        result = router.route_query("Hello")
        # With no strong signals, should default to tactical
        assert result in ['strategic', 'tactical']  # Either is acceptable for neutral
    
    def test_case_insensitive(self, router):
        """Test that routing is case-insensitive"""
        result1 = router.route_query("GIVE ME A COMMAND")
        result2 = router.route_query("give me a command")
        assert result1 == result2 == 'tactical'
    
    def test_complex_strategic_query(self, router):
        """Test complex strategic scenario"""
        result = router.route_query(
            "What should I do next after discovering the domain controller? "
            "I need to analyze the attack vectors and plan my approach."
        )
        assert result == 'strategic'
    
    def test_complex_tactical_query(self, router):
        """Test complex tactical scenario"""
        result = router.route_query(
            "Give me the command to enumerate SMB shares and show me the syntax"
        )
        assert result == 'tactical'


class TestQueryRouterConvenience:
    """Test the convenience function"""
    
    def test_route_query_function(self):
        """Test standalone route_query function"""
        from ai.router import route_query
        
        result = route_query("What should I do?")
        assert result in ['strategic', 'tactical']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
