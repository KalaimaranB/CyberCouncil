# Quick Reference

## Commands

| Command | Description | Aliases |
|---------|-------------|---------|
| `/help` | Show all commands | `/help <cmd>` |
| `/sitrep` | Situation report | `status`, `summary` |
| `/graph` | Attack graph (terminal + web) | `show graph` |
| `/dashboard` | Full web UI | `/web`, `/ui` |
| `/crack HASH` | GPU hash cracking | `/crack --types` |
| `/server start` | Start remote API | `/server stop` |
| `/review` | Review pending logs | `review logs` |
| `/clear-logs` | Clear pending logs | `clear logs` |
| `/search QUERY` | Search security docs | - |
| `/tutorial` | Interactive walkthrough | `/demo` |
| `/close` | Finalize investigation | `close investigation` |

---

## Hash Cracking

```bash
/crack HASH                    # Auto-detect type
/crack --types                 # List supported types
/crack -w /path/wordlist HASH  # Custom wordlist
/crack -m 1000 HASH            # Force mode
```

**Supported**: NTLM, MD5, SHA-1/256/512, bcrypt, Kerberos, NetNTLMv2

---

## Tool Import

Paste raw output from:
- `nmap` - Ports, services, OS
- `rustscan` - Open ports
- `gobuster` - Directories
- `wpscan` - WordPress vulns
- `nikto` - Web vulns

---

## Remote Access (Kali VM)

```bash
# On Mac: Enable SSH in System Preferences

# From Kali:
ssh -L 5052:localhost:5052 user@MAC_IP
cd /path/to/CyberCouncil
python council.py
/dashboard
# Open http://localhost:5052 in Kali browser
```

---

## Natural Input

Just type naturally:
- "Found DC at 10.10.10.5" → Auto-logged
- "Port 445 is open" → Captured
- "Username: admin" → Stored
- "CVE-2021-44228 found" → Tracked
