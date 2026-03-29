# 🛡️ CyberCouncil: Autonomous Offensive Security Orchestration

**CyberCouncil** is an agent-driven offensive security assistant designed to streamline, accelerate, and automate fragmented workflows during penetration testing engagements. By orchestrating a multi-agent system, CyberCouncil translates ambiguous reconnaissance data into scalable, executable intelligence, empowering security operators with high-impact leverage.

---

## 🌟 Executive Summary & Impact

**What it does:** CyberCouncil acts as an autonomous intelligence layer over traditional security tools. It manages the lifecycle of an engagement by ingesting raw, unstructured scan data, autonomously building an interactive attack graph, and providing strategic and tactical guidance.
**How it was built:** Developed in Python with a focus on systems thinking, utilizing the Ollama API, LangChain, and ChromaDB. The architecture is highly modular and built with iteration in mind, ensuring components like the AI router, vector engine, and graph visualization can be rapidly tested, deployed, and improved.
**The Impact:** By automating fragmented operational work (like parsing Nmap or Rustscan logs) and orchestrating AI-driven insights, it dramatically reduces cognitive load and allows operators to focus on high-value exploitation. It holds up under real use, bridging the gap between raw data collection and strategic execution, proving resilient and reliable.

---

## 🤖 Multi-Agent Orchestration & Shared State

*[📖 Read the Deep Dive: Agent Orchestration & Hybrid Routing](docs/AGENT_ROUTING.md)*

CyberCouncil utilizes a **hybrid routing system** to orchestrate multiple AI specialists:
- **The Strategist (Vader):** Analyzes the broader engagement state, identifies high-impact opportunities, and maps out long-term strategic plans.
- **The Tactical Specialist (DeepHat):** Provides precise, actionable commands, scripts, and syntax for immediate execution (e.g., hash cracking logic, specific exploitation commands).

**Shared State & Feedback Loops:**
These agents do not operate in silos. They communicate through a shared state—the engagement's `active_record.md`. As one agent or automated tool discovers new information (e.g., an open SMB port), the shared state is updated, creating a compounding feedback loop where subsequent AI reasoning becomes progressively more accurate and context-aware.

---

## 🧠 Multi-Tier Memory Architecture

*[📖 Read the Deep Dive: Multi-Tier Memory Systems](docs/MEMORY_ARCHITECTURE.md)*

To ensure the AI agents possess compounding intelligence over time, CyberCouncil implements a sophisticated multi-tier memory architecture designed to surface the right context at the right time:

1. **Persistent Knowledge Layer (RAG with ChromaDB):** Operates as the long-term memory. It stores fundamental cybersecurity knowledge and methodology. Context retrieval is optimized using Maximal Marginal Relevance (MMR) to balance high relevance with content diversity, preventing redundancy.
2. **Episodic Memory (Active Record):** Acts as the short-term working memory for the current engagement. It maintains the exact timeline of discoveries, credentials, and compromised hosts.
3. **Learned Knowledge Graph:** The `attack_graph.py` engine continuously ingests the Episodic memory to construct a multidimensional NetworkX graph, mapping the relationships between IPs, Services, Vulnerabilities, and Access levels.

---

## ⚙️ Automated Workflows & Tool Engine

*[📖 Read the Deep Dive: Automated Parsing Engine](docs/PARSING_ENGINE.md)*

CyberCouncil translates unstructured, ambiguous inputs into structured system outputs without needing everything perfectly defined by the operator:
- **Intelligent Discovery Parsing:** Using an automated regex-based engine (`discovery_parser.py`), the system seamlessly processes pasted terminal outputs from tools like `nmap`, `rustscan`, `gobuster`, and `wpscan`. It natively identifies infrastructure, credentials, and CVEs.
- **AI Log Classification:** The internal wrapper (`ollama_client.py`) uses a lightweight classification model to categorize user actions into ENUMERATION, EXPLOITATION, or POST-EXPLOITATION natively, applying structure to unstructured human input.
- **GPU-Accelerated Integration:** Integrates directly with hardware, auto-detecting hash types and routing them to specialized cracking utilities (e.g., hashcat) when requested.

---

## 💻 Technical Implementation & End-to-End Ownership

CyberCouncil was designed with a focus on understanding inputs, outputs, where things break, and ensuring overall trustworthiness:
- **Resilience:** Integrates exponential backoff retry logic and fallback mechanisms within the Ollama client wrapper to handle inference failures or API downtime gracefully.
- **Observability in the Loop:** Includes a "Pending Logs" queue (`logger.py`) that acts as a human-in-the-loop checkpoint, allowing engineers to review AI-detected findings to ensure accuracy, trust, and reliability before committing them to the permanent record.

### System Architecture
```text
council.py          # Main orchestrator
├── core/           # Commands, AI clients, Context/Memory builders
├── ai/             # Multi-agent router, Vector engine
├── graph/          # Attack graph visualization and NetworkX engine
├── parsing/        # Discovery and automated tool parsers
├── remote/         # Remote API server for distributed operations
├── web/            # Interactive dashboard UI
└── utils/          # Config, utilities, GPU integrations
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.9+
- Ollama running locally or remotely (configured in `utils/config.py`)

```bash
# Clone the repository
git clone https://github.com/kalaimaranbalasothy/CyberCouncil.git
cd CyberCouncil

# Install dependencies
pip install -r requirements.txt

# Start the Council
python council.py
```
*Note: Run `/tutorial` on your first launch for an interactive, hands-on walkthrough of the system.*

---

## 🚧 Limitations & Future Roadmap

As a system built for rapid iteration ("ship, observe, improve, repeat"), there are known limitations and areas for future expansion:
- **Graph Neural Network (GNN) Prediction:** Currently, the attack graph provides visualization and basic relational mapping. Future iterations aim to integrate GNN-based link prediction to proactively suggest the most statistically viable attack paths.
- **Parser Robustness:** The current tool parsing logic relies on regex pattern matching. Complex or heavily malformed tool outputs may drop edge-case intelligence. Hardening the parsing layer is an ongoing operational priority.
- **Autonomous Exploitation Constraints:** To maintain human-in-the-loop safety, fully autonomous exploitation is disabled by design. The system currently recommends, but does not autonomously execute, high-risk commands.
- **Context Window Ceilings:** Managing extremely large engagements can strain the episodic memory token limits of local models. Improved chunking and summarization layers are needed for massive horizontal deployments.
