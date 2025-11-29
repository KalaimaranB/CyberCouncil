"""
Base Command Interface
"""

from abc import ABC, abstractmethod

class Command(ABC):
    """
    Abstract base class for all system commands.
    """
    
    @abstractmethod
    def execute(self, context) -> bool:
        """
        Execute the command.
        
        Args:
            context: The CyberCouncil instance or context object
            
        Returns:
            True if execution was successful, False otherwise
        """
        pass
