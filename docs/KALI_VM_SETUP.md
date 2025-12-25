# Kali VM Remote Access Guide

Connect to CyberCouncil running on your Mac from a Kali Linux VM.

---

## Prerequisites

1. **Enable SSH on Mac**
   - System Preferences → Sharing → ✓ Remote Login
   - Note your Mac's IP: `ifconfig | grep inet`

2. **VMware Network**: Set to **Bridged** (not NAT)

---

## Method 1: SSH with Port Forwarding (Recommended)

From **Kali terminal**:

```bash
# Connect with port forwarding for dashboard
ssh -L 5052:localhost:5052 YOUR_USER@MAC_IP

# Example:
ssh -L 5052:localhost:5052 john@192.168.1.100
```

Then:
```bash
cd ~/Projects/CyberCouncil
python council.py
```

In Council:
```
/dashboard
```

In **Kali browser**: `http://localhost:5052`

---

## Method 2: Direct IP Access

If bridged networking is configured:

1. Run dashboard on Mac
2. In Kali browser: `http://MAC_IP:5052`

---

## Method 3: Remote API Client

From **Kali**:

```bash
# Copy client to Kali
scp user@MAC_IP:~/CyberCouncil/remote/council_client.py ./

# Send commands
./council_client.py --host MAC_IP "Found DC at 10.10.10.5"

# Import tool output
./council_client.py --host MAC_IP --file nmap.txt
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| SSH with dashboard | `ssh -L 5052:localhost:5052 user@MAC_IP` |
| Start dashboard | `/dashboard` (in Council) |
| Access in Kali | `http://localhost:5052` |
| Remote API | `./council_client.py --host MAC_IP "msg"` |
