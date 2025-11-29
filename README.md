# 🧠 CyberCouncil (V0.1)

**AI-Powered Offensive Security Orchestrator**

CyberCouncil is a terminal-based tool that assists security researchers by orchestrating two specialized AI models to plan, execute, and document security engagements. It combines RAG (Retrieval-Augmented Generation), an active knowledge graph, and automated logging to maintain context throughout an investigation.

---

## 🚀 Core Objectives

1.  **Orchestration**: Manage the workflow between strategic planning and tactical execution.
2.  **Context Retention**: Automatically log findings and maintain a "memory" of the engagement using RAG and an Active Record.
3.  **Relationship Mapping**: Visualize connections between discovered entities (IPs, ports, vulnerabilities) using a dynamic Attack Graph.

---

## 🛠️ Prerequisites

1.  **Python 3.10+**
2.  **Ollama**:
    *   Install the [Ollama App](https://ollama.com/) (Mac/Linux/Windows).
    *   Ensure the app is running in the background (tray icon visible).
    *   *Note: You do NOT need to run `ollama serve` manually if the app is running.*
3.  **Models**:
    *   **Strategist**: `ollama pull phi4`
    *   **Specialist**: [DeepHat-V1-7B-GGUF](https://huggingface.co/mradermacher/DeepHat-V1-7B-GGUF/blob/main/DeepHat-V1-7B.Q4_K_M.gguf) (See `SETUP_GUIDE.md` for import instructions).

---

## 📦 Installation

```bash
# 1. Clone the repository
git clone https://github.com/YourUsername/CyberCouncil.git
cd CyberCouncil

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env
# Edit .env if you need to change model names
```

---

## 🚦 Usage

Start the council:

```bash
python main.py
```

### Common Commands

| Command | Description |
| :--- | :--- |
| `/sitrep` | Generate a Situation Report summarizing current status. |
| `/graph` | Display the current Attack Graph. |
| `/review` | Review and commit pending logs to the Active Record. |
| `/close` | Finalize the project and generate a report. |

See [WALKTHROUGH.md](WALKTHROUGH.md) for a detailed usage guide.
See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed configuration.
