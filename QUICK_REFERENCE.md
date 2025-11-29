# 🚀 CyberCouncil Quick Reference

Fast reference for common operations and commands.

## Installation & Startup

```bash
# First time setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ai/ingest.py

# Every session
source .venv/bin/activate
ollama serve  # Separate terminal
python council.py
```

## Discovery Patterns

| What You Say | What Gets Logged |
|--------------|------------------|
| "Found DC at 10.10.10.5" | 🎯 IP [DOMAIN_CONTROLLER]: 10.10.10.5 |
| "Port 445 is open" | ✅ Open Port [OPEN]: 445 |
| "Running SMB" | ⚙️ Service: SMB |
| "Vulnerable to MS17-010" | 🚨 Vulnerability: MS17-010 |
| "Username is admin" | 👤 Username [CREDENTIAL]: admin |
| "Password is Pass123" | 🔑 Password [CREDENTIAL]: Pass123 |
| "Domain is CORP" | 🏰 Domain: CORP |

## Commands

| Command | What It Does |
|---------|--------------|
| `/graph` | Show attack graph |
| `status` | Show investigation status |
| `/review` | Review pending logs |
| `/clear-logs` | Clear pending logs |
| `/search <query>` | Search documentation |
| `/close` | Finalize project |
| `pause teach` | General mode (no logging) |
| `resume` | Return to project |
| `exit` | Quit CyberCouncil |

## AI Routing

### Ask Vader (Strategic)
- "What should I do?"
- "Analyze this vulnerability"
- "Explain how X works"
- "Why is Y important?"

### Ask DeepHat (Tactical)
- "Give me a command for X"
- "Show me syntax for Y"
- "Write a script to Z"

## Attack Graph

**View:** `/graph`

**Automatically tracks:**
- 🎯 IPs
- ⚙️ Services  
- 🔌 Ports
- 🚨 Vulnerabilities
- 🔑 Credentials
- 🏰 Domains

**Auto-infers relationships:**
- SMB → Port 445, 139
- HTTP → Port 80, 8080
- SSH → Port 22
- Kerberos → Port 88
- Service → Vulnerability (name matching)

**Saved to:** `projects/YourProject/attack_graph.json`

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific test
pytest tests/test_attack_graph.py -v
```

## File Locations

| What | Where |
|------|-------|
| Your notes | `notes/general/*.md` |
| Projects | `projects/<ProjectName>/` |
| Active record | `projects/<ProjectName>/active_record.md` |
| Attack graph | `projects/<ProjectName>/attack_graph.json` |
| Vector DB | `chroma_db/` |
| Config | `core/config.py` |
| Tests | `tests/` |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Model not found" | `ollama pull phi4` then create |
| "No context" | `python ai/ingest.py` |
| Graph not updating | Be specific in discoveries |
| Tests failing | `pip install pytest pytest-cov` |

## Configuration

Edit `core/config.py`:

```python
# Models
STRATEGIST_MODEL = "strategist"
SPECIALIST_MODEL = "specialist"

# RAG
FALLBACK_THRESHOLD = 0.15
CHUNK_SIZE = 1500
K_RESULTS = 3
MMR_LAMBDA = 0.7

# Terminal
TERMINAL_RENDERING_ENABLED = True
```

## Project Structure

```
CyberCouncil/
├── council.py          # Main launcher
├── core/              # Orchestration
│   ├── council.py     # Main logic
│   └── config.py      # Configuration
├── ai/                # AI & routing
│   ├── router.py
│   ├── vector_engine.py
│   └── ingest.py
├── parsing/           # Entity extraction
│   ├── discovery_parser.py
│   └── logger.py
├── graph/             # Attack graphs ⭐
│   ├── attack_graph.py
│   └── graph_visualizer.py
├── ui/                # Terminal rendering
├── utils/             # Helpers
└── tests/             # Test suite (75 tests)
```

## Typical Workflow

1. **Start session**
   ```bash
   source .venv/bin/activate
   python council.py
   ```

2. **Create/load project**
   - New project or select recent

3. **Make discoveries**
   ```
   [Project]> I found a DC at 10.10.10.5
   [Project]> Port 445 is open
   [Project]> Running SMB service
   ```

4. **View graph**
   ```
   [Project]> /graph
   ```

5. **Ask questions**
   ```
   [Project]> What should my next steps be?
   [Project]> Give me an SMB enumeration command
   ```

6. **Check status**
   ```
   [Project]> status
   ```

7. **Review logs**
   ```
   [Project]> /review
   ```

8. **Close when done**
   ```
   [Project]> /close
   ```

## Tips

✅ **Do:**
- Be specific in discoveries
- Check `/graph` regularly
- Review pending logs
- Use `/search` for official docs
- Ask strategic questions to Vader
- Ask technical questions to DeepHat

❌ **Avoid:**
- Vague statements ("found a server")
- Forgetting to review pending logs
- Mixing strategic and tactical in one query

## Resources

- **Full docs:** `WALKTHROUGH.md`
- **Setup:** `SETUP_GUIDE.md`  
- **Tests:** `tests/README.md`
- **Attack graph deep dive:** `.gemini/antigravity/brain/.../walkthrough.md`

---

**Version 2.0** - Attack Graph MVP
