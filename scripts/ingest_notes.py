#!/usr/bin/env python3
"""
Script to ingest notes into the CyberCouncil knowledge base.

This script loads all markdown and PDF files from the notes directory,
scrubs sensitive data, and stores embeddings in ChromaDB for RAG retrieval.

Usage:
    python scripts/ingest_notes.py
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    from ai.ingest import ingest_notes
    
    try:
        ingest_notes()
    except KeyboardInterrupt:
        print("\n\n⚠️  Ingestion cancelled by user")
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
