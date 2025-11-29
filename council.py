#!/usr/bin/env python3
"""
CyberCouncil - AI-Powered Offensive Security Assistant
Main entry point for the application
"""

if __name__ == "__main__":
    try:
        from core.council import CyberCouncil
        Council = CyberCouncil()
        Council.run()
    except KeyboardInterrupt:
        print("\n\n💀 Council Disconnected.")
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you're in the project root directory and have activated the virtual environment.")
