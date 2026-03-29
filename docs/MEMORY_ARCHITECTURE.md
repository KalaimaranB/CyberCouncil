# 🧠 Multi-Tier Memory Architecture

In long-running, agent-driven workflows, context windows quickly become a bottleneck. CyberCouncil solves this by implementing a **Multi-Tier Memory Architecture** that separates invariant knowledge from rapidly changing operational state.

## 1. Persistent Knowledge Layer (Long-Term Memory)
*Powered by ChromaDB and advanced RAG.*

The baseline layer stores immutable cybersecurity methodology, tradecraft, and historical data. 
- **The Challenge:** Standard similarity search often returns redundant results (e.g., retrieving five slightly different documents on basic SQL injection).
- **The Solution:** We implement **Maximal Marginal Relevance (MMR)** during retrieval. MMR penalizes redundancy, ensuring the agent receives a highly relevant but *diverse* set of documents. This maximizes the information density of the context window.

## 2. Episodic Working Memory (Short-Term State)
*Powered by `active_record.md`.*

As an engagement progresses, the operational reality changes minute by minute. The **Episodic Memory** is the single source of truth for the *current* state of the environment.
- It is a highly structured, chronological log of discovered IPs, compromised credentials, and open ports.
- **Shared State:** Both the Strategist and Tactical agents read from this identical state, ensuring that if one agent discovers a vulnerability, the other instantly factors it into its next decision. This creates a powerful **feedback loop**.

## 3. Relational Intelligence (Compounding Memory)
*Powered by NetworkX (`graph/attack_graph.py`).*

Raw episodic logs are linear and hard to analyze at scale. CyberCouncil continuously parses the episodic memory to build a **NetworkX Directed Graph**.
- Nodes represent Entities (IPs, Ports, Services, Vulnerabilities).
- Edges represent logical Relationships (`IP -> runs -> Service -> has_vuln -> MS17-010`).

By structuring memory relationally, the system gains compounding intelligence. While currently used for visualization, this layer lays the groundwork for future **Graph Neural Network (GNN)** traversal, allowing the system to mathematically predict the most viable path to domain compromise.
