# 🛡️ CyberCouncil

AI-powered offensive security assistant with dual-AI architecture, RAG knowledge system, and **attack graph visualization** for intelligent penetration testing guidance.

## 🎯 Key Features

### 🧠 Dual-AI Architecture
- **Vader (Strategist)** - Strategic planning and analysis using Phi-4
- **DeepHat (Specialist)** - Technical commands and code generation using DeepHat-7B
- **Intelligent Routing** - Automatically routes queries to the appropriate AI

### 📊 Attack Graph Visualization ⭐ NEW
- **Automatic graph building** from discovered entities
- **Visual relationships** between IPs, services, vulnerabilities, and credentials
- **ASCII rendering** in terminal with colored output
- **Foundation for GNN** attack path prediction (Phase 2)

### 🔍 Auto-Discovery Logging
- Automatically extracts IPs, credentials, ports, services, and vulnerabilities
- No manual logging required
- Real-time graph updates as you discover entities

### 🗄️ RAG Knowledge System
- Learns from your cybersecurity notes
- PyTorch embeddings with Apple Silicon acceleration
- MMR algorithm for diverse, high-quality retrieval
- Scrubs sensitive data to prevent cross-contamination

### 📁 Project Management
- Organized investigation tracking with section-based logging
- Automatic lesson extraction from finalized projects
- Closed project protection
- Pending log review system

### 🧪 Comprehensive Test Suite
- **75 tests** covering all core functionality
- pytest with fixtures and mocking
- 90%+ coverage on core modules
- Security and edge case testing

## 🏗️ Project Structure

```
CyberCouncil/
├── core/              # Main orchestration (council.py, config.py)
├── ai/                # AI models and routing
├── parsing/           # Entity extraction and logging
├── graph/             # Attack graph visualization ⭐
├── ui/                # Terminal rendering
├── utils/             # Helper functions
├── tests/             # Comprehensive test suite
├── projects/          # Your investigations
├── notes/             # Your knowledge base
└── chroma_db/         # Vector database
```

## 📦 Installation

### Prerequisites

- **Python 3.10+**
- **Ollama** - For running local LLMs
  ```bash
  # macOS
  brew install ollama
  
  # Linux
  curl -fsSL https://ollama.com/install.sh | sh
  ```

### Setup

1. **Clone and setup environment**
   ```bash
   git clone <repository-url>
   cd CyberCouncil
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set up Ollama models**
   ```bash
   ollama pull phi4
   ollama create strategist -f Modelfile_Phi4
   
   # Download DeepHat-V1-7B.Q4_K_M.gguf (provided separately)
   ollama create specialist -f Modelfile_DeepHat
   ```

3. **Create directories and ingest knowledge**
   ```bash
   mkdir -p notes/general notes/learned projects
   # Add your notes to notes/general/
   python ai/ingest.py
   ```

## 🚀 Quick Start

```bash
source .venv/bin/activate
ollama serve  # In separate terminal
python council.py
```

Then:
- Create/select a project
- Make discoveries: "I found a DC at 10.10.10.5"
- Ask strategic questions: "What should my approach be?"
- Get tactical commands: "Give me an nmap command"
- **View attack graph**: `/graph` ⭐

## 📊 Attack Graph Features

The attack graph automatically visualizes your investigation:

```bash
[YourProject]> I found a DC at 10.10.10.5
📍 Logged: 🎯 IP [DOMAIN_CONTROLLER]: 10.10.10.5

[YourProject]> Port 445 is open
📍 Logged: ✅ Open Port [OPEN]: 445

[YourProject]> Running SMB service
📍 Logged: ⚙️ Service: SMB

[YourProject]> /graph
📊 ATTACK GRAPH STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Nodes: 3
Total Edges: 2

🎯 [10.10.10.5]
  ├──[runs]──> ⚙️ SMB
  └──[on_port]──> 🔌 Port_445
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Graph automatically infers relationships:
- Service-to-port mappings (SMB → 445, HTTP → 80, etc.)
- IP-to-service connections
- Vulnerability-to-access paths

## 🧪 Testing

```bash
source .venv/bin/activate
pytest tests/ -v                    # Run all 75 tests
pytest tests/ --cov=. --cov-report=html  # With coverage
```

## 📚 Documentation

- **[WALKTHROUGH.md](WALKTHROUGH.md)** - Complete usage guide with attack graph examples
- **[tests/README.md](tests/README.md)** - Test suite documentation
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup instructions

## 🎓 Learning Objectives

This project demonstrates:

**Core Skills:**
- Graph Neural Network foundations (NetworkX, entity relationships)
- Deep Learning (PyTorch embeddings, vector search)
- RAG Systems (retrieval-augmented generation)
- LLM Integration (multi-model orchestration)
- Software Engineering (modular architecture, testing)

**Advanced Concepts:**
- Graph algorithms (relationship inference, pathfinding)
- Visualization (ASCII rendering, colored output)
- Data processing (entity extraction, auto-logging)
- Security (sanitization, path traversal prevention)

**Transferable to Computational Biology:**
- Protein interaction networks (graphs)
- Entity extraction (protein sequences, domains)
- Relationship inference (protein-protein interactions)
- GNN applications (function prediction)

## 🔮 Roadmap

### Phase 1: MVP ✅ (Complete)
- Attack graph visualization
- Entity extraction and relationship inference
- ASCII terminal rendering

### Phase 2: GNN Integration (Planned)
- PyTorch Geometric for graph neural networks
- Exploitability scoring using GNN
- Attack path prediction
- Interactive HTML visualization (D3.js)

## ⚙️ Configuration

Edit `core/config.py` to customize:
- Model names and parameters
- RAG settings (chunk size, retrieval count, MMR lambda)
- Terminal rendering options
- Project directories

## 🎯 Command Reference

| Command | Description |
|---------|-------------|
| `/graph` | Show attack graph visualization ⭐ |
| `status` / `sitrep` | Show situation report |
| `/review` | Review pending logs |
| `/clear-logs` | Clear pending logs |
| `/search <query>` | DuckDuckGo search |
| `/close` | Finalize project |
| `pause teach` | Enter general mode (no logging) |
| `resume` | Return to project mode |

## ⚖️ License & Disclaimer

**Educational use only.** This tool is designed for **authorized security testing only**. Users are responsible for ensuring they have explicit permission before testing any systems. Unauthorized access is illegal.

---

**Note**: Your notes and project data are protected by `.gitignore` and will not be committed to the repository.

**Version**: 2.0 - Attack Graph MVP
