import os

# --- DIRECTORY CONFIGURATION ---
# These can be overridden via environment variables
DB_DIR = os.getenv("CYBERCOUNCIL_DB_DIR", "./chroma_db")
PROJECTS_DIR = os.getenv("CYBERCOUNCIL_PROJECTS_DIR", "./projects")
NOTES_DIR = os.getenv("CYBERCOUNCIL_NOTES_DIR", "./notes")

# --- MODEL CONFIGURATION ---
STRATEGIST_MODEL = os.getenv("CYBERCOUNCIL_STRATEGIST_MODEL", "strategist")
SPECIALIST_MODEL = os.getenv("CYBERCOUNCIL_SPECIALIST_MODEL", "specialist")

# --- RAG CONFIGURATION ---
# Number of documents to retrieve for context
RAG_RETRIEVAL_K = int(os.getenv("CYBERCOUNCIL_RAG_K", "5"))

# RAG quality improvements
RAG_RELEVANCE_THRESHOLD = float(os.getenv("CYBERCOUNCIL_RAG_THRESHOLD", "0.65"))
RAG_CANDIDATE_K = int(os.getenv("CYBERCOUNCIL_RAG_CANDIDATES", "20"))
MMR_LAMBDA = float(os.getenv("CYBERCOUNCIL_MMR_LAMBDA", "0.5"))  # Balance relevance vs diversity

# Chunk settings for document ingestion
CHUNK_SIZE = int(os.getenv("CYBERCOUNCIL_CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CYBERCOUNCIL_CHUNK_OVERLAP", "200"))

# --- OLLAMA CONFIGURATION ---
# Maximum retry attempts for Ollama API calls
OLLAMA_MAX_RETRIES = int(os.getenv("CYBERCOUNCIL_OLLAMA_RETRIES", "3"))

# --- AUTO-LOGGING CONFIGURATION ---
# Model used for classifying log sections
LOG_CLASSIFIER_MODEL = os.getenv("CYBERCOUNCIL_LOG_CLASSIFIER", "qwen2:0.5b")

# --- PROJECT CONFIGURATION ---
# Maximum length for project names
MAX_PROJECT_NAME_LENGTH = 100

# Maximum number of backups of active record
MAX_ACTIVE_RECORD_BACKUPS = 5

# Number of recent projects to display
RECENT_PROJECTS_COUNT = 5

# --- TERMINAL RENDERING CONFIGURATION ---
# Enable/disable markdown rendering in terminal
TERMINAL_RENDERING_ENABLED = os.getenv("CYBERCOUNCIL_TERMINAL_RENDERING", "true").lower() == "true"
