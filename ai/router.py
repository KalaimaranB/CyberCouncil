"""
Query Router Module

Routes user queries to either strategic (Vader) or tactical (DeepHat) AI models
using a hybrid scoring system that combines multiple signals:
- Keyword matching (strategic vs tactical vocabulary)
- Question type analysis (how/why vs show/give)
- Query length heuristics
- Code marker detection

This ensures queries are sent to the most appropriate AI specialist.

Usage:
    router = QueryRouter()
    decision = router.route_query("What should I do next?")  # Returns: 'strategic'
    decision = router.route_query("Give me an nmap command")  # Returns: 'tactical'
"""


class QueryRouter:
    """
    Routes user queries to either strategic (Vader) or tactical (DeepHat) models
    using a hybrid scoring system.
    """
    
    def __init__(self):
        # Strategic keywords - indicate need for high-level analysis
        self.strategy_keywords = [
            "plan", "strategy", "analyze", "review", "think", "vader", "approach", 
            "vector", "what should i do", "what is", "target", "current", "how do i",
            "explain", "why", "assess", "evaluate", "consider", "recommend", "advise",
            "how should"
        ]
        
        # Tactical keywords - indicate need for specific commands/code
        self.tactical_keywords = [
            "command", "syntax", "code", "script", "give me", "show me",
            "what's the", "tool for"
        ]
    
    def route_query(self, user_input: str) -> str:
        """
        Route query using hybrid scoring system.
        Returns: 'strategic' or 'tactical'
        """
        score = {
            'strategic': 0,
            'tactical': 0
        }
        
        user_lower = user_input.lower()
        
        # Signal 1: Strategy keywords (+2 each)
        for keyword in self.strategy_keywords:
            if keyword in user_lower:
                score['strategic'] += 2
                break  # Only count once
        
        # Signal 2: Tactical keywords (+2 each)
        for keyword in self.tactical_keywords:
            if keyword in user_lower:
                score['tactical'] += 2
                break
        
        # Signal 3: Question type (+1)
        if user_input.startswith(("How should", "Why", "What is", "When", "Explain")):
            score['strategic'] += 1
        elif user_input.startswith(("Give me", "Show me", "What's the", "Which tool")):
            score['tactical'] += 1
        
        # Signal 4: Length (+1)
        word_count = len(user_input.split())
        if word_count > 10:
            score['strategic'] += 1
        elif word_count < 6:
            score['tactical'] += 1
        
        # Signal 5: Code markers (+2 for tactical)
        if '```' in user_input or 'command for' in user_lower:
            score['tactical'] += 2
        
        # Decision: highest score wins
        return 'strategic' if score['strategic'] > score['tactical'] else 'tactical'


# Convenience function
def route_query(user_input: str) -> str:
    """Quick routing function"""
    router = QueryRouter()
    return router.route_query(user_input)
