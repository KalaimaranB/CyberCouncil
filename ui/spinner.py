"""
Spinner Module

Provides animated loading indicator for long-running operations.
Shows elapsed time during AI model inference.
"""

import sys
import time
import threading


class Spinner:
    """
    Animated loading spinner with elapsed time display.
    
    Usage:
        spinner = Spinner()
        spinner.start("Thinking")
        # ... long operation ...
        spinner.stop()
        
    Or as context manager:
        with Spinner("Processing") as s:
            # ... long operation ...
    """
    
    FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self):
        self._running = False
        self._thread = None
        self._message = ""
        self._start_time = None
    
    def start(self, message: str = "Processing"):
        """Start the spinner animation."""
        if self._running:
            return
        
        self._message = message
        self._running = True
        self._start_time = time.time()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the spinner and clear the line."""
        if not self._running:
            return
        
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)
        
        # Clear the spinner line
        sys.stdout.write('\r' + ' ' * 60 + '\r')
        sys.stdout.flush()
    
    def _spin(self):
        """Animation loop running in background thread."""
        frame_idx = 0
        
        while self._running:
            elapsed = time.time() - self._start_time
            frame = self.FRAMES[frame_idx % len(self.FRAMES)]
            
            # Format: "⠋ Thinking... (12s)"
            output = f"\r{frame} {self._message}... ({int(elapsed)}s)"
            sys.stdout.write(output)
            sys.stdout.flush()
            
            frame_idx += 1
            time.sleep(0.1)
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False


# Convenience function
def spin_while(func, message: str = "Processing"):
    """
    Execute a function while showing a spinner.
    
    Args:
        func: Callable to execute
        message: Message to display
        
    Returns:
        Result of func()
    """
    spinner = Spinner()
    spinner.start(message)
    try:
        return func()
    finally:
        spinner.stop()
