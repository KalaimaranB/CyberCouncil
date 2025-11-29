# 📖 CyberCouncil Walkthrough

Complete guide to using CyberCouncil for offensive security operations with attack graph visualization.

## Table of Contents

- [Getting Started](#getting-started)
- [Understanding the Dual-AI System](#understanding-the-dual-ai-system)
- [Attack Graph Visualization](#attack-graph-visualization) ⭐ NEW
- [Auto-Discovery Logging](#auto-discovery-logging)
- [Project Management](#project-management)
- [System Commands](#system-commands)
- [Advanced Features](#advanced-features)

---

## Getting Started

### First Launch

```bash
source .venv/bin/activate
ollama serve  # In separate terminal
python council.py
```

You'll see initialization:
```
💀 Initializing Council Systems...
✅ Models validated: strategist, specialist
⚡ [Engine] Initializing PyTorch Model...
   -> 🚀 Hardware Acceleration: ENABLED (Apple Metal)
🧠 Attack graph initialized
```

### Create or Select Project

```
[1] New Project
[2] Search Projects
--- RECENT ---
[3] Operation_Phoenix
```

Choose option and you'll see:
```
─── 📊 INVESTIGATION STATUS 📊 ───
PROJECT: Operation_Phoenix
STATUS: Active Investigation

ENUMERATION: 3 entries
EXPLOITATION: 0 entries
POST-EXPLOITATION: 0 entries
─────────────────────────────────

[Operation_Phoenix]>
```

---

## Understanding the Dual-AI System

CyberCouncil uses two specialized AI models that automatically route queries:

### Vader (Strategist) - Phi-4

**Triggered by:**
- Strategic keywords: plan, strategy, analyze, why, should, recommend
- Long analytical questions
- High-level thinking requests

**Example:**
```
[Project]> What should my approach be for this domain controller?

[Vader] Thinking...

ANALYSIS: Your target presents a Windows domain infrastructure...

STRATEGY:
1. Enumerate SMB shares for information disclosure
2. Check for null session vulnerabilities
3. Query LDAP for user enumeration
4. Assess Kerberos for roasting opportunities
```

### DeepHat (Specialist) - DeepHat-7B

**Triggered by:**
- Tactical keywords: command, syntax, show me, give me
- Short technical queries
- Code/script requests

**Example:**
```
[Project]> Give me an nmap command for SMB enumeration

[Specialist] Processing...

nmap -p 445 --script smb-enum-shares,smb-enum-users 10.10.10.5
```

**Routing is automatic** - just ask naturally!

---

## Attack Graph Visualization ⭐

The attack graph automatically builds as you make discoveries, showing relationships between entities.

### How It Works

**Entities tracked:**
- 🎯 **IPs** - Target machines
- ⚙️ **Services** - Running services (SMB, HTTP, SSH, etc.)
- 🔌 **Ports** - Open ports
- 🚨 **Vulnerabilities** - Discovered vulnerabilities
- 🔑 **Credentials** - Usernames, passwords, hashes
- 🏰 **Domains** - Domain names

**Relationships inferred:**
- `IP --runs--> SERVICE`
- `SERVICE --on_port--> PORT`
- `SERVICE --has_vuln--> VULNERABILITY`
- `IP --has_account--> USERNAME`
- `VULNERABILITY --enables--> ACCESS`

### Example Workflow

```bash
[Project]> I found a domain controller at 10.10.10.5
📍 Logged: 🎯 IP [DOMAIN_CONTROLLER]: 10.10.10.5

[Project]> Ports 445 and 88 are open
📍 Logged: ✅ Open Port [OPEN]: 445
📍 Logged: ✅ Open Port [OPEN]: 88

[Project]> Running SMB and Kerberos services
📍 Logged: ⚙️ Service: SMB
📍 Logged: ⚙️ Service: Kerberos

[Project]> Vulnerable to MS17-010
📍 Logged: 🚨 Vulnerability: MS17-010

[Project]> /graph
```

**Output:**
```
📊 ATTACK GRAPH STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Nodes: 7
Total Edges: 7

Breakdown by Type:
  🎯 IP: 1
  ⚙️ SERVICE: 2
  🔌 PORT: 2
  🚨 VULNERABILITY: 1
  ✅ ACCESS: 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗂️  DISCOVERED ENTITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 IP:
  ├─ 10.10.10.5 [DOMAIN_CONTROLLER]

⚙️ SERVICE:
  ├─ SMB
  ├─ Kerberos

🔌 PORT:
  ├─ Port_445
  ├─ Port_88

📈 ATTACK GRAPH (Relationships)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 [10.10.10.5]
  ├──[runs]──> ⚙️ SMB
  ├──[runs]──> ⚙️ Kerberos

⚙️ [SMB]
  ├──[on_port]──> 🔌 Port_445
  └──[has_vuln]──> 🚨 MS17-010

🚨 [MS17-010]
  └──[enables]──> ✅ ACCESS_from_MS17-010
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Graph Features

**Automatic updates** - Graph rebuilds every time you log a discovery

**Intelligent inference** - Automatically connects:
- SMB to ports 445, 139
- HTTP to ports 80, 8080
- SSH to port 22
- Kerberos to port 88
- Services to vulnerabilities (name matching)

**Persistence** - Saved to `projects/YourProject/attack_graph.json`

**Foundation for GNN** - Ready for PyTorch Geometric integration (Phase 2)

---

## Auto-Discovery Logging

CyberCouncil automatically extracts and logs discoveries from your statements.

### Supported Entities

| Entity Type | Example Statement | Logged As |
|-------------|-------------------|-----------|
| IP Address | "Found DC at 10.10.10.5" | 🎯 IP [DOMAIN_CONTROLLER]: 10.10.10.5 |
| Port | "Port 445 is open" | ✅ Open Port [OPEN]: 445 |
| Service | "Running SMB service" | ⚙️ Service: SMB |
| Vulnerability | "Vulnerable to MS17-010" | 🚨 Vulnerability: MS17-010 |
| Username | "Username is administrator" | 👤 Username [CREDENTIAL]: administrator |
| Password | "Password is Admin123" | 🔑 Password [CREDENTIAL]: Admin123 |
| Hash | "Found NTLM hash 5f4dcc..." | 🔐 Hash [CREDENTIAL]: 5f4dcc... |
| Domain | "Domain is CORP" | 🏰 Domain: CORP |

### Context Detection

The parser understands context:
- "Found **domain controller** at 10.10.10.5" → Tagged as DC
- "**Target** is at 192.168.1.50" → Tagged as TARGET
- "**Web server** at 10.10.10.20" → Tagged as WEB_SERVER

### Multiple Discoveries

Extract multiple entities from one statement:
```
[Project]> Found DC at 10.10.10.5 running SMB on port 445 vulnerable to MS17-010

📍 Logged: 🎯 IP [DOMAIN_CONTROLLER]: 10.10.10.5
📍 Logged: ⚙️ Service: SMB
📍 Logged: ✅ Open Port [OPEN]: 445
📍 Logged: 🚨 Vulnerability: MS17-010
```

**Graph auto-updates** after each discovery batch!

---

## Project Management

### Section-Based Logging

Projects use three investigation phases:

1. **ENUMERATION** - Discovery phase (ports, services, IPs)
2. **EXPLOITATION** - Active exploitation (vulnerabilities, credentials)
3. **POST-EXPLOITATION** - Post-compromise activities

Logs are automatically classified using AI.

### Pending Log Review System

Not all AI responses are auto-logged. Use the pending log system:

```bash
[Project]> /review

📝 PENDING LOG #1
─────────────────────────────────────────────────────
QUERY: What tools should I use?
SUGGESTED SECTION: ENUMERATION

CONTENT:
I recommend nmap for port scanning...

[A]ppend / [S]kip / [E]dit / [Q]uit: a
✅ Appended to active_record.md
```

### Project Status

Check anytime:
```bash
[Project]> status

─── 📊 INVESTIGATION STATUS 📊 ───
PROJECT: Operation_Phoenix

ENUMERATION: 12 entries
  Recent:
   - 🎯 IP [DOMAIN_CONTROLLER]: 10.10.10.5
   - ⚙️ Service: SMB
   
EXPLOITATION: 3 entries
  Recent:
   - 🚨 Vulnerability: MS17-010
   
Graph: 15 nodes, 18 edges
─────────────────────────────────
```

### Closing Projects

```bash
[Project]> /close

🔐 Finalizing Investigation: Operation_Phoenix

📋 Generating summary with Vader...
[Vader generates lessons learned]

✅ Summary saved to: projects/Operation_Phoenix/summary.md
✅ Added to knowledge base for future projects
🔒 Project marked as closed

This project cannot be reopened (preserves chain of custody).
```

---

## System Commands

| Command | Description |
|---------|-------------|
| `/graph` | Show attack graph visualization ⭐ |
| `status` / `sitrep` | Show investigation status |
| `/review` | Review pending logs for approval |
| `/clear-logs` | Clear all pending logs |
| `/search <query>` | Search DuckDuckGo for docs |
| `/close` | Finalize and close project |
| `pause teach` | Enter general mode (no project context, no logging) |
| `resume` | Return to project mode |
| `exit` / `quit` | Exit CyberCouncil |

---

## Advanced Features

### RAG Knowledge System

**What it does:**
- Retrieves relevant context from your notes
- Powers AI responses with your knowledge
- Uses MMR (Maximal Marginal Relevance) for diverse results
- Scrubs sensitive data to prevent cross-contamination

**How to use:**
1. Add markdown or PDF notes to `notes/general/`
2. Run `python ai/ingest.py`
3. Knowledge automatically retrieved during AI queries

**Best practices:**
- Organize notes by topic (Active Directory, Web, Linux, etc.)
- Use headers and bullet points for structure
- Update knowledge base periodically: `python ai/ingest.py`

### Teach Mode (General Context)

Use CyberCouncil for learning without project logging:

```bash
[Project]> pause teach
⏸️  System: Entering Teach Mode (General Context Only).

[GENERAL]> Explain Kerberos authentication
[Vader gives educational explanation - NOT logged to project]

[GENERAL]> resume
▶️  System: Restoring Project Context.
[Project]>
```

### Markdown Rendering

Responses include:
- Syntax-highlighted code blocks
- Copyable commands
- Formatted tables and lists
- Color-coded output

Configure in `core/config.py`:
```python
TERMINAL_RENDERING_ENABLED = True  # Toggle rendering
```

### Search Integration

Search official documentation:
```bash
[Project]> /search SMB enumeration techniques

🔎 [Eyes] Searching for: SMB enumeration techniques
[Results appended to context and added to pending logs]
```

Prioritizes:
1. Official docs (GitHub, ReadTheDocs, .org sites)
2. Trusted writeups (HackTheBox, TryHackMe)
3. General results

---

## Tips & Best Practices

### Effective Discovery Logging

✅ **Good:**
- "Found DC at 10.10.10.5"
- "Port 445 is open"
- "Running SMB service"
- "Vulnerable to MS17-010"

❌ **Avoided:**
- "Found a server" (too vague)
- "Some ports are open" (no specifics)

### Using the Attack Graph

- Check `/graph` periodically to visualize progress
- Use it to identify missing links (e.g., service without port)
- Great for reports and documentation
- Foundation for GNN attack path prediction (coming in Phase 2)

### Strategic vs Tactical Queries

**Ask Vader (Strategic):**
- "What should I focus on?"
- "Why is this vulnerability important?"
- "Analyze the attack surface"
- "Recommend next steps"

**Ask DeepHat (Tactical):**
- "Give me the nmap command"
- "Show me smbclient syntax"
- "Write a script for enumeration"

### Log Management

- Review pending logs regularly: `/review`
- Clear irrelevant logs: `/clear-logs`
- Auto-discoveries go straight to active_record
- AI responses go to pending for your review

---

## Troubleshooting

### Issue: "Model not found"
**Solution:** Pull and create models:
```bash
ollama pull phi4
ollama create strategist -f Modelfile_Phi4
```

### Issue: "Hardware acceleration disabled"
**Normal on:** Intel CPUs, Linux without CUDA
**Not a problem:** Will run on CPU (slower but functional)

### Issue: "No context retrieved"
**Solution:** Ingest your notes:
```bash
python ai/ingest.py
```

### Issue: Graph not updating
**Solution:** Discoveries must match patterns. Be specific:
- Use IP addresses (not "server")
- Mention port numbers
- Name services explicitly

### Issue: Tests failing
**Solution:**
```bash
source .venv/bin/activate
pip install pytest pytest-cov
pytest tests/ -v
```

---

## What's Next?

### Current Capabilities (MVP)
- ✅ Attack graph visualization
- ✅ Entity extraction and auto-logging
- ✅ Relationship inference
- ✅ ASCII terminal rendering
- ✅ 75 passing tests

### Phase 2: GNN Integration (Planned)
- 🔮 PyTorch Geometric for graph neural networks
- 🔮 Exploitability scoring using GNN
- 🔮 Attack path prediction (shortest path to domain admin)
- 🔮 Interactive HTML visualization (D3.js)
- 🔮 Export graphs as PNG/SVG for reports

---

## Additional Documentation

- **[README.md](README.md)** - Project overview and installation
- **[tests/README.md](tests/README.md)** - Test suite documentation
- **[Attack Graph Walkthrough](/.gemini/antigravity/brain/8c42f206-f3f5-498b-a8a3-5b433611be5a/walkthrough.md)** - Deep dive into graph features

---

**Happy Hacking!** 🛡️

*Remember: Always get proper authorization before security testing.*
