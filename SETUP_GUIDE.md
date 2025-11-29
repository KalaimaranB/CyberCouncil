# CyberCouncil - Fresh Start Setup Guide

Complete setup instructions for getting CyberCouncil running from scratch.

---

## Prerequisites

### 1. **Ollama Service**
Ollama must be installed and running with the required models.

**Check if Ollama is running:**
```bash
ollama list
```

If you get an error, start Ollama:
```bash
# On macOS, Ollama usually runs as an app
# Or start it via command line:
ollama serve
```

### 2. **Required Models**
You need two models installed in Ollama:
- `strategist` (for strategic planning)
- `specialist` (for tactical commands)

**Check what models you have:**
```bash
ollama list
```

**If you need to create/pull the models:**

Based on your `Modelfile_Phi4` and `Modelfile_DeepHat`, create them:

```bash
# Create the strategist model (Phi-4)
ollama create strategist -f Modelfile_Phi4

# Create the specialist model (DeepHat)
ollama create specialist -f Modelfile_DeepHat
```

---

## Step-by-Step Setup

### Step 1: Activate Virtual Environment

```bash
cd "/DIRECTORY/CyberCouncil"
source .venv/bin/activate
```

### Step 2: Install/Update Dependencies

```bash
pip install -r requirements.txt
```

**If requirements.txt is missing packages, install manually:**
```bash
pip install ollama langchain-chroma langchain-core langchain-community \
    langchain-text-splitters transformers torch duckduckgo-search
```

### Step 3: Prepare Knowledge Base (Optional but Recommended)

If you have notes/documentation to ingest:

```bash
# Make sure notes directory exists
mkdir -p notes

# Add your markdown or PDF files to ./notes/
# Then run the ingestion script:
python ingest.py
```

**Expected output:**
```
📚 [Librarian] Scanning and Sanitizing notes...
   -> Processing: your_note.md
🧠 [Librarian] Vectorizing with PyTorch...
⚡ [Engine] Initializing PyTorch Model: sentence-transformers/all-MiniLM-L6-v2
   -> 🚀 Hardware Acceleration: ENABLED (Apple Metal)
✅ Generalized and Stored X knowledge chunks.
```

If you don't have notes yet, you can skip this - the system will warn you but still work.

### Step 4: Run CyberCouncil

```bash
python council.py
```

**Expected startup output:**
```
💀 Initializing Council Systems...
⚡ [Engine] Initializing PyTorch Model: sentence-transformers/all-MiniLM-L6-v2
   -> 🚀 Hardware Acceleration: ENABLED (Apple Metal)
✅ Models validated: strategist, specialist
✅ Knowledge base loaded (found indexed content)

--- 🧠 CYBER COUNCIL ONLINE 🧠 ---

[1] New Project
[2] Search Projects
--- RECENT ---

Select Option:
```

---

## Troubleshooting

### Issue: "Cannot connect to Ollama service"

**Solution:**
1. Check if Ollama is running:
   ```bash
   ollama list
   ```
2. If not running, start it:
   ```bash
   ollama serve
   ```
3. Verify models exist:
   ```bash
   ollama list
   ```

### Issue: "Missing Ollama models: strategist, specialist"

**Solution:**
Create the models from your Modelfiles:
```bash
ollama create strategist -f Modelfile_Phi4
ollama create specialist -f Modelfile_DeepHat
```

### Issue: "Knowledge base is empty"

**Solution:**
This is just a warning. Either:
1. Run `python ingest.py` after adding notes to `./notes/`
2. Or continue - the system will work but without RAG context

### Issue: "Could not load Database or PyTorch Engine"

**Solution:**
1. Check if PyTorch is installed:
   ```bash
   pip install torch transformers
   ```
2. Check if ChromaDB is installed:
   ```bash
   pip install langchain-chroma
   ```

### Issue: Module import errors

**Solution:**
Reinstall dependencies:
```bash
pip install --upgrade -r requirements.txt
```

---

## Configuration (Optional)

You can customize paths and settings via environment variables:

```bash
# Custom database location
export CYBERCOUNCIL_DB_DIR="/path/to/custom/db"

# Custom projects directory
export CYBERCOUNCIL_PROJECTS_DIR="/path/to/projects"

# Different model names
export CYBERCOUNCIL_STRATEGIST_MODEL="phi4:latest"
export CYBERCOUNCIL_SPECIALIST_MODEL="deephat:v2"

# Adjust RAG settings
export CYBERCOUNCIL_RAG_K=10  # Retrieve more context documents

# Run with custom config
python council.py
```

---

## Quick Start Commands

**Complete fresh start (assuming Ollama is running with models):**

```bash
# 1. Navigate to project
cd "/DIRECTORY/CyberCouncil"

# 2. Activate virtual environment
source .venv/bin/activate

# 3. (Optional) Ingest knowledge base
python ingest.py

# 4. Run CyberCouncil
python council.py
```

---

## Verifying Everything Works

Once running, try these commands:

1. **Create a test project:**
   - Select option `[1] New Project`
   - Enter name: `test`
   - You should see: `Project test initialized.`

2. **Ask a strategic question:**
   - Type: `what is the best approach to enumerate a target?`
   - Should route to `[Vader] Thinking...`

3. **Ask for a command:**
   - Type: `give me an nmap command for port scanning`
   - Should route to `[Specialist] Processing...`

4. **Check status:**
   - Type: `status`
   - Should show situation report

5. **Close project:**
   - Type: `/close`
   - Should create backup and generate lessons learned

---

## What Changed from Original

The fixes added:
- ✅ Model validation at startup
- ✅ Database health checks
- ✅ Automatic backups before finalization
- ✅ Path sanitization for security
- ✅ Retry logic for API calls
- ✅ Better error messages
- ✅ Configurable paths via environment variables

Everything should work the same way, just more robustly!
