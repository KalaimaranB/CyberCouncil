# CyberCouncil

**AI-Powered Offensive Security Assistant** with dual-AI architecture, attack graph visualization, and GPU hash cracking.

---

## Features

| Feature | Description |
|---------|-------------|
| 🤖 **Dual AI** | Strategist (planning) + Specialist (commands) |
| 🕸️ **Attack Graph** | Interactive web visualization |
| 📥 **Tool Import** | Auto-parse nmap, rustscan, gobuster, wpscan |
| 🔐 **Hash Cracking** | GPU-accelerated with auto-detection |
| 🌐 **Web Dashboard** | Full browser UI |
| 📡 **Remote API** | Access from Kali VM |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python council.py
```

On first run: `/tutorial` for guided walkthrough.

---

## Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/sitrep` | Strategic situation report |
| `/graph` | Interactive attack graph |
| `/dashboard` | Full web UI |
| `/crack HASH` | GPU hash cracking |
| `/server start` | Remote API for Kali |
| `/review` | Manage pending logs |
| `/close` | Finalize investigation |

---

## Tool Import

Just paste raw output from:
- **nmap** - Ports, services, OS
- **rustscan** - Fast port scans
- **gobuster** - Directories
- **wpscan** - WordPress vulnerabilities

---

## Kali VM Access

```bash
ssh -L 5052:localhost:5052 user@MAC_IP
python council.py
/dashboard
# Browser: http://localhost:5052
```

See [docs/KALI_VM_SETUP.md](docs/KALI_VM_SETUP.md) for details.

---

## Architecture

```
council.py          # Main entry
├── core/           # Commands, AI clients
├── ai/             # Router, vector engine
├── graph/          # Attack graph visualization
├── parsing/        # Discovery & tool parsers
├── remote/         # API server, Kali client
├── web/            # Dashboard UI
└── utils/          # Tools, config, hash cracker
```

---

## License

MIT
