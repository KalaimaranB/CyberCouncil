# ⚙️ Automated Parsing & Tool Engine

Raw security data is notoriously noisy, unstructured, and fragmented. Translating this ambiguous output into scalable, executable data structures is a core capability of CyberCouncil.

## The Discovery Parser (`parsing/discovery_parser.py`)

Security tool outputs (`nmap`, `gobuster`, `rustscan`) are pasted directly into the Council. Instead of relying on slow, token-heavy LLMs to read entire scan logs, we utilize a highly optimized, regex-driven pipeline.

- **Entity Extraction:** The system automatically identifies IPv4 addresses, hostnames, ports, credentials, and CVE identifiers.
- **Contextualization:** The parser doesn't just pull an IP; it reads the surrounding string locally to determine if that IP is a `domain_controller`, a `gateway`, or a standard `target`.
- **Normalization:** Extracted entities are instantly formatted and injected into the Episodic Memory (`active_record.md`), making them instantly available to the AI agents and the visualization graph without human intervention.

## AI Log Classification

While deterministic regex handles entity extraction, we use lightweight AI to apply stateful context.

Every action taken by the user or the system is passed through a fast classifier model which categorizes the action into one of three operational states:
1. **ENUMERATION:** Information gathering and scanning.
2. **EXPLOITATION:** Active attempts to gain access.
3. **POST-EXPLOITATION:** Privilege escalation, lateral movement, or persistence.

By automatically applying structured metadata to unstructured actions, the system maintains a clean, scalable timeline of the engagement that holds up under real operational use.
