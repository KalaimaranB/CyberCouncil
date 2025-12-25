# Walkthrough

## Getting Started

```bash
python council.py
```

First time? Run `/tutorial` for interactive guide.

---

## 1. Start a Project

Select from menu or create new. Each project gets:
- `active_record.md` - Your notes
- `tool_outputs/` - Raw scan data
- `cracked/` - Cracked passwords

---

## 2. Log Discoveries

Just type naturally:
```
Found DC at 10.10.10.5 with ports 88, 445 open
Username: svc_backup, hash: aad3b435...
```

Auto-captured and added to attack graph.

---

## 3. Import Tool Output

Paste nmap/rustscan output directly:
```
Nmap scan report for 10.10.10.5
PORT    STATE SERVICE  VERSION
445/tcp open  smb      Windows Server 2019
```

System detects tool and extracts data.

---

## 4. Ask the AI

**Strategic questions** → Strategist (Vader)
```
How should I approach this DC?
What's my next move in the kill chain?
```

**Technical questions** → Specialist (DeepHat)
```
Give me the command to dump NTDS.dit
How to run Kerberoasting with impacket?
```

Router decides automatically.

---

## 5. Visualize

Terminal view:
```
/graph
```

Web dashboard:
```
/dashboard
```

---

## 6. Crack Hashes

```
/crack 31d6cfe0d16ae931b73c59d7e0c089c0
```

Auto-detects NTLM, runs hashcat with GPU.

---

## 7. Status Report

```
/sitrep
```

Get strategic summary of your progress.

---

## 8. Close Investigation

```
/close
```

Generates report, exports graph, archives project.
