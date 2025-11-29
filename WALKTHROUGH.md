# 📖 Walkthrough (V0.1)

This guide walks you through a typical engagement using CyberCouncil.

---

## 1. Starting a Session

Run the main script:
```bash
python main.py
```

You will be presented with a menu:
*   **[1] New Project**: Start a fresh engagement.
*   **[2] Search Projects**: Find an existing project.
*   **Recent Projects**: Quickly resume recent work.

Select **[1]** and enter a project name (e.g., `Target-Alpha`).

---

## 2. The Loop

Once inside a project, you are in the **Intelligence Loop**.

### 🗣️ Interaction
Simply type your thoughts, findings, or questions.

*   **Strategic Questions**: "How should I approach this target?" -> Routes to **Strategist (Phi-4)**.
*   **Tactical Requests**: "Give me an nmap command for fast scanning." -> Routes to **Specialist (DeepHat)**.

### 📝 Auto-Logging
The system automatically detects key information in your input (e.g., "Found open port 80 on 10.10.10.5") and queues it for the **Active Record**.

*   **Review Logs**: Type `/review` to see pending logs and commit them to the permanent record.

---

## 3. Visualization & Status

### 📊 Situation Report (SitRep)
Type `/sitrep` at any time.
The Strategist will analyze your Active Record and provide:
1.  Current status in the kill chain.
2.  Key findings so far.
3.  Recommended next steps.

### 🕸️ Attack Graph
Type `/graph` to see a visual representation of the attack surface.
*   **Nodes**: IPs, Ports, Services, Vulnerabilities.
*   **Edges**: Relationships (e.g., `10.10.10.5 -> HAS_PORT -> 80`).

---

## 4. Closing the Engagement

When you are finished, type `/close`.

The system will:
1.  Ask you to commit any pending logs.
2.  Generate a **Final Report** (`FINAL_REPORT.md`) summarizing the entire engagement.
3.  Export the **Attack Graph** to JSON.
4.  Mark the project as closed (read-only).

---

## 💡 Pro Tips

*   **Teach Mode**: Type `pause` or `teach` to switch to **General Mode**. This allows you to ask general questions without polluting the project log. Type `resume` to go back.
*   **RAG**: The system automatically retrieves relevant notes from your knowledge base based on your query. Look for `[NOTE: Title]` in the context.
