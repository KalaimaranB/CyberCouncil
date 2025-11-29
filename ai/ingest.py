"""
Knowledge base ingestion pipeline for CyberCouncil.

This module loads markdown and PDF notes, scrubs sensitive data (IPs, credentials,
hashes), extracts metadata, chunks the content, and stores embeddings in ChromaDB
for RAG retrieval.

Key Features:
- Scrubs target-specific data while preserving concepts
- Supports .md and .pdf files
- Context-aware scrubbing (doesn't destroy legitimate content)
- Domain whitelisting for important technical sites
- Metadata extraction from markdown headers

Usage:
    from ai.ingest import ingest_notes
    ingest_notes()
"""

import os
import glob
import re
from typing import Dict, List
from langchain_community.document_loaders import TextLoader, PyPDFLoader # Loaders
from langchain_text_splitters import RecursiveCharacterTextSplitter       # Text Splitter
from langchain_chroma import Chroma                                      # Vector Store
from langchain_core.documents import Document
from ai.vector_engine import PyTorchEmbedder
from core import config

# Constants
DEFAULT_TITLE = "General"
SOURCE_TYPE_PDF = "pdf"

# Whitelist of important technical domains to preserve
WHITELISTED_DOMAINS = [
    'github.com', 'microsoft.com', 'exploit-db.com', 'kali.org',
    'metasploit.com', 'rapid7.com', 'offensive-security.com',
    'nmap.org', 'wireshark.org', 'python.org', 'stackoverflow.com'
]


def scrub_sensitive_data(text: str) -> str:
    """
    Sanitizes notes before ingestion so the AI learns concepts, not specific targets.
    Enhanced to prevent context contamination between projects while preserving
    important technical content.
    
    Args:
        text: Raw text content to scrub
        
    Returns:
        Scrubbed text with sensitive data replaced by placeholders
    """
    # 1. Replace IPv4 Addresses (e.g., 10.10.10.5) with <TARGET_IP>
    # We ignore 127.0.0.1 and 0.0.0.0
    ip_pattern = r'\b(?!(?:127\.0\.0\.1|0\.0\.0\.0)\b)(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    text = re.sub(ip_pattern, "<TARGET_IP>", text)
    
    # 2. Replace common CTF domains
    text = re.sub(r'tryhackme\.loc', "<TARGET_DOMAIN>", text, flags=re.IGNORECASE)
    text = re.sub(r'htb\.local', "<TARGET_DOMAIN>", text, flags=re.IGNORECASE)
    
    # 3. Scrub usernames (CONTEXT-AWARE - only in credential contexts)
    # Matches: "username: admin", "user: root", "login: administrator"
    text = re.sub(r'\b(username|user|login):\s*(admin|administrator|root|user\d+)\b', 
                  r'\1: <USERNAME>', text, flags=re.IGNORECASE)
    
    # Generic pattern for "username: <value>"
    text = re.sub(r'\b(username|user|login):\s*\S+', r'\1: <USERNAME>', text, flags=re.IGNORECASE)
    
    # 4. Scrub passwords (CONTEXT-AWARE - only in credential contexts)
    # Matches: "password: xyz", "pass: abc", "pwd: 123"
    text = re.sub(r'\b(password|pass|pwd):\s*\S+', r'\1: <PASSWORD>', text, flags=re.IGNORECASE)
    
    # Also match "password=<value>" format
    text = re.sub(r'\b(password|pass|pwd)\s*=\s*["\']([^"\']+)["\']', r'\1=<PASSWORD>', text, flags=re.IGNORECASE)
    
    # 5. Scrub hashes
    # MD5 hashes (32 hex characters)
    text = re.sub(r'\b[a-fA-F0-9]{32}\b', '<MD5_HASH>', text)
    
    # SHA1 hashes (40 hex characters)
    text = re.sub(r'\b[a-fA-F0-9]{40}\b', '<SHA1_HASH>', text)
    
    # SHA256 hashes (64 hex characters)
    text = re.sub(r'\b[a-fA-F0-9]{64}\b', '<SHA256_HASH>', text)
    
    # 6. Scrub domain names with whitelist protection
    # Build pattern that excludes whitelisted domains
    whitelisted_pattern = '|'.join([re.escape(domain) for domain in WHITELISTED_DOMAINS])
    
    # Scrub all domains EXCEPT whitelisted ones
    text = re.sub(
        rf'\b(?!(?:{whitelisted_pattern})\b)[a-zA-Z0-9-]+\.(com|net|org|local|htb|thm)\b',
        '<DOMAIN>',
        text,
        flags=re.IGNORECASE
    )
    
    # 7. Scrub specific hostnames
    # Matches: DC-01, SRV-WEB01, DB-PROD, MAIL-SRV, etc.
    text = re.sub(r'\b(DC|SRV|WEB|DB|MAIL|AD|SQL|EXCH)-[A-Z0-9]+\b', '<HOSTNAME>', text, flags=re.IGNORECASE)
    
    return text


def extract_metadata_from_headers(text: str) -> Dict[str, str]:
    """
    Extracts the Title (#) and Subtitles (##) to use as metadata.
    Works with markdown format: '# Title' and '## Subtitle'
    
    Args:
        text: Markdown text content
        
    Returns:
        Dictionary with 'title' and 'topics' keys
    """
    metadata = {"title": DEFAULT_TITLE, "topics": ""}
    
    # Find the main title (First line starting with # )
    title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if title_match:
        metadata["title"] = title_match.group(1).strip()
        
    # Find sub-topics (Lines starting with ## )
    topics = re.findall(r'^##\s+(.+)$', text, re.MULTILINE)
    if topics:
        metadata["topics"] = ", ".join(topics)
        
    return metadata

def ingest_notes() -> None:
    """
    Main ingestion pipeline that loads, scrubs, chunks, and embeds notes.
    
    Raises:
        FileNotFoundError: If notes directory doesn't exist
        NotADirectoryError: If notes path is not a directory
    """
    print("📚 [Librarian] Scanning and Sanitizing notes...")
    
    # Validation: ensure notes directory exists
    if not os.path.exists(config.NOTES_DIR):
        raise FileNotFoundError(f"Notes directory not found: {config.NOTES_DIR}")
    
    if not os.path.isdir(config.NOTES_DIR):
        raise NotADirectoryError(f"Path is not a directory: {config.NOTES_DIR}")
    
    documents = []
    failed_files: List[tuple[str, str]] = []
    
    # 1. Load Markdown Files
    md_files = list(glob.glob(f"{config.NOTES_DIR}/**/*.md", recursive=True))
    print(f"   Found {len(md_files)} markdown file(s)")
    
    for filepath in md_files:
        print(f"   -> Processing: {os.path.basename(filepath)}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            
            # A. SCRUB DATA (Generalization Step)
            clean_text = scrub_sensitive_data(raw_text)
            
            # B. EXTRACT METADATA (Header Step)
            meta = extract_metadata_from_headers(clean_text)
            meta['source'] = os.path.basename(filepath)
            
            # Create a Document object manually since we modified the text
            doc = Document(page_content=clean_text, metadata=meta)
            documents.append(doc)
            
        except Exception as e:
            error_msg = f"{filepath}: {str(e)}"
            print(f"   ⚠️  ERROR: {error_msg}")
            failed_files.append((filepath, str(e)))

    # 2. Load PDF Files (Text Based)
    pdf_files = list(glob.glob(f"{config.NOTES_DIR}/**/*.pdf", recursive=True))
    if pdf_files:
        print(f"   Found {len(pdf_files)} PDF file(s)")
        
    for filepath in pdf_files:
        print(f"   -> Processing PDF: {os.path.basename(filepath)}")
        try:
            loader = PyPDFLoader(filepath)
            docs = loader.load()
            for doc in docs:
                # We also scrub PDFs
                doc.page_content = scrub_sensitive_data(doc.page_content)
                doc.metadata['source_type'] = SOURCE_TYPE_PDF
            documents.extend(docs)
        except Exception as e:
            error_msg = f"{filepath}: {str(e)}"
            print(f"   ⚠️  ERROR: {error_msg}")
            failed_files.append((filepath, str(e)))

    # Report any failures
    if failed_files:
        print(f"\n❌ {len(failed_files)} file(s) failed to ingest:")
        for filepath, error in failed_files:
            print(f"   - {os.path.basename(filepath)}: {error}")

    if not documents:
        print("\n⚠️  No notes found. Add .md or .pdf files to 'notes/' directory")
        print(f"   Notes directory: {config.NOTES_DIR}")
        return

    # 3. Split Text
    print(f"\n📝 [Librarian] Chunking {len(documents)} document(s)...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE, 
        chunk_overlap=config.CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)
    print(f"   Created {len(chunks)} chunks")

    # 4. Embed & Store
    print("\n🧠 [Librarian] Vectorizing with PyTorch...")
    embedding_function = PyTorchEmbedder()
    
    # Initialize Chroma
    db = Chroma(
        persist_directory=config.DB_DIR, 
        embedding_function=embedding_function
    )
    
    # Add documents (This automatically upserts/saves)
    print("   Storing embeddings in ChromaDB...")
    db.add_documents(documents=chunks)
    
    print(f"\n✅ Successfully ingested and stored {len(chunks)} knowledge chunks")
    print(f"   📊 Stats: {len(documents)} documents → {len(chunks)} chunks")
    if failed_files:
        print(f"   ⚠️  {len(failed_files)} file(s) skipped due to errors")