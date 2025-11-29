# ⚡ Quick Reference (V0.1)

## 🖥️ System Commands

| Command | Alias | Description |
| :--- | :--- | :--- |
| `/sitrep` | `status`, `report` | Generate a Situation Report (Status, Findings, Next Steps). |
| `/graph` | `show graph` | Display the ASCII Attack Graph. |
| `/review` | `review logs` | Review and commit pending auto-logs. |
| `/close` | `close investigation` | Finalize project, generate report, and exit. |
| `/clear-logs` | `clear logs` | Discard all pending logs. |
| `/search` | - | Search official docs (if configured). |
| `exit` | `quit` | Exit the application. |

---

## 🔄 Modes

| Mode | Trigger | Description |
| :--- | :--- | :--- |
| **PROJECT** | Default | All queries use project context and are logged. |
| **GENERAL** | `pause`, `teach` | No project context. Queries are NOT logged. Good for general learning. |
| **RESUME** | `resume` | Return to PROJECT mode. |

---

## 🤖 AI Roles

| Role | Model | Function |
| :--- | :--- | :--- |
| **Strategist** | Phi-4 | Planning, methodology, analysis, reporting. |
| **Specialist** | DeepHat | Syntax, tools, payloads, technical execution. |

---

## 📂 Key Files

| File | Location | Purpose |
| :--- | :--- | :--- |
| `active_record.md` | `projects/<name>/` | The living log of the engagement. |
| `FINAL_REPORT.md` | `projects/<name>/` | Generated upon closing the project. |
| `.env` | Root | Configuration (Model names, API keys). |
