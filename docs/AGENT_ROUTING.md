# 🤖 Multi-Agent Orchestration & Routing

CyberCouncil rejects the monolithic LLM approach in favor of a specialized **Multi-Agent System**. Different phases of security workflows require fundamentally different modes of reasoning.

## The Dual-Agent Paradigm

1. **The Strategist (Vader):** 
   - *Role:* High-level planning, operational assessment, and identifying "what" to do next.
   - *Behavior:* Analyzes the entire engagement graph, mapping current discoveries against kill-chain frameworks.

2. **The Tactical Specialist (DeepHat):**
   - *Role:* Execution, syntax generation, and tool usage.
   - *Behavior:* Generates highly precise, context-aware terminal commands (e.g., the exact `impacket` syntax needed to exploit a specific service found in the active record).

## The Hybrid Routing Heuristic (`ai/router.py`)

To provide a seamless UX, the user simply talks to the system. A lightweight, deterministic **Query Router** analyzes the input in real-time and routes it to the correct specialist using a hybrid scoring system.

The router evaluates:
- **Keyword Analysis:** Does the query contain strategic words (*"plan, approach, evaluate"*) or tactical words (*"command, syntax, script"*).
- **Interrogative Type:** "Why/How" questions lean strategic. "Give me/Show me" lean tactical.
- **Length Heuristics:** Short, punchy requests are usually tool commands. Long explanations of the environment are usually strategic loops.
- **Code Markers:** The presence of backticks or code formatting instantly biases the router toward the Tactical agent.

## End-to-End Resilience
Because we own the system end-to-end, reliability is critical. The agents interact with local and remote models via a resilient wrapper (`core/ollama_client.py`) that includes automatic model validation and exponential backoff retries, ensuring the orchestrator doesn't crash during inference spikes.
