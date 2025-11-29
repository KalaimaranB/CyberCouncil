# 📋 CyberCouncil Code Review Checklist

**Purpose:** Systematic review of all code before first git push  
**Estimated Time:** 4-5 hours (thorough) | 1.5-2 hours (priority files only)  
**Date Started:** _____________  
**Date Completed:** _____________

---

## 🎯 Review Strategy

This checklist follows a **bottom-up dependency flow**:
1. Configuration & utilities (foundation)
2. AI, parsing, and graph layers (building blocks)
3. Core orchestration (integration)
4. Tests & documentation (validation)

---

## 📚 Phase 1: Configuration & Foundation

### ☐ 1. `core/config.py` (5-10 min)
**Why First:** Defines all constants, model names, paths, and system parameters

**Review Items:**
- [ ] Model names match Ollama setup (`STRATEGIST_MODEL`, `SPECIALIST_MODEL`)
- [ ] Directory paths are correct (`NOTES_DIR`, `PROJECTS_DIR`, `CHROMA_DIR`)
- [ ] RAG parameters are sensible (K=5, threshold=0.65, lambda=0.5)
- [ ] Chunk settings appropriate (size=1200, overlap=200)
- [ ] Terminal rendering settings configured
- [ ] No hardcoded secrets or API keys
- [ ] Environment variable fallbacks present

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 🔧 Phase 2: Utility Layer (Pure Functions)

### ☐ 2. `utils/tools.py` (10 min)
**Why:** Core utility functions (DuckDuckGo search, sanitization)

**Review Items:**
- [ ] DuckDuckGo search functionality implemented correctly
- [ ] Input sanitization logic prevents injection attacks
- [ ] Path traversal prevention in place
- [ ] No hardcoded secrets or credentials
- [ ] Error handling for network failures
- [ ] Function docstrings clear and accurate

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 3. `utils/project_status.py` (5 min)
**Why:** Project state management (closed project detection)

**Review Items:**
- [ ] File path handling is safe (no path traversal)
- [ ] Status file format is documented
- [ ] Edge cases handled (missing files, corrupted status)
- [ ] Proper error handling for I/O operations
- [ ] Function logic is clear and simple

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 🎨 Phase 3: UI Layer (Presentation)

### ☐ 4. `ui/terminal_renderer.py` (10 min)
**Why:** Markdown rendering with syntax highlighting

**Review Items:**
- [ ] Code blocks render correctly (copy-pasteable)
- [ ] Syntax highlighting works for common languages
- [ ] Color scheme is consistent and readable
- [ ] Edge cases handled (malformed markdown, empty input)
- [ ] No ANSI escape sequence injection vulnerabilities
- [ ] Performance acceptable for large outputs

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 5. `ui/test_renderer.py` (2 min) *(Optional)*
**Why:** Manual testing script for terminal rendering

**Review Items:**
- [ ] Quick sanity check - does it demonstrate renderer features?
- [ ] No critical issues visible

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 🧠 Phase 4: AI Layer (Intelligence)

### ☐ 6. `ai/vector_engine.py` (15 min)
**Why:** PyTorch embeddings engine (foundation for RAG)

**Review Items:**
- [ ] Apple Silicon MPS acceleration configured correctly
- [ ] Fallback to CPU if MPS unavailable
- [ ] Embedding dimension consistent (384 for all-MiniLM-L6-v2)
- [ ] Memory management appropriate (no leaks)
- [ ] Model loading error handling
- [ ] Batch processing implemented efficiently
- [ ] Thread safety if needed

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 7. `ai/ingest.py` (10 min)
**Why:** Knowledge base ingestion script

**Review Items:**
- [ ] File discovery logic finds all relevant files
- [ ] Chunking strategy matches config (1200 chars, 200 overlap)
- [ ] ChromaDB integration correct (collection creation, upserts)
- [ ] Error handling for corrupted/unreadable files
- [ ] Progress indicators for user feedback
- [ ] Duplicate handling strategy clear
- [ ] Can be run multiple times safely (idempotent)

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 8. `ai/router.py` (15 min)
**Why:** Hybrid routing logic (Vader vs DeepHat)

**Review Items:**
- [ ] Keyword patterns for routing are comprehensive
- [ ] Scoring algorithm is logical and well-documented
- [ ] Fallback behavior is sensible (default to Strategist?)
- [ ] No obvious routing edge cases missed
- [ ] Performance acceptable (routing should be fast)
- [ ] Easy to add new routing rules

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 🔍 Phase 5: Parsing Layer (Data Extraction)

### ☐ 9. `parsing/discovery_parser.py` (20 min)
**Why:** Entity extraction (IPs, ports, credentials, vulns)

**Review Items:**
- [ ] Regex patterns for entity detection are accurate
- [ ] IP address validation (IPv4/IPv6)
- [ ] Port number validation (1-65535)
- [ ] Credential extraction doesn't create false positives
- [ ] Vulnerability detection patterns comprehensive
- [ ] Entity classification logic is clear
- [ ] False positive handling/filtering present
- [ ] No regex DoS vulnerabilities (catastrophic backtracking)

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 10. `parsing/logger.py` (15 min)
**Why:** Automatic logging to active_record.md

**Review Items:**
- [ ] File I/O operations are safe (proper file handling)
- [ ] Section classification works correctly
- [ ] Duplicate detection prevents redundant logs
- [ ] Pending log queue management is thread-safe if needed
- [ ] Log format is consistent and readable
- [ ] Timestamps included where appropriate
- [ ] Error handling for write failures

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 📊 Phase 6: Graph Layer (Visualization) ⭐ NEW

### ☐ 11. `graph/attack_graph.py` (20 min)
**Why:** NetworkX graph construction and relationship inference

**Review Items:**
- [ ] Node creation logic handles all entity types
- [ ] Edge inference rules are comprehensive (SMB→445, HTTP→80, etc.)
- [ ] Graph update mechanisms don't create duplicates
- [ ] Data structure integrity maintained
- [ ] Node attributes stored correctly
- [ ] Graph can be serialized/deserialized if needed
- [ ] Performance acceptable for large graphs (100+ nodes)
- [ ] Cycle detection/handling if relevant

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 12. `graph/graph_visualizer.py` (15 min)
**Why:** ASCII rendering of attack graphs

**Review Items:**
- [ ] Tree traversal algorithm is correct
- [ ] Color coding consistent with entity types
- [ ] Edge case handling (empty graphs, single node, cycles)
- [ ] Statistics calculation accurate
- [ ] Output formatting is clean and readable
- [ ] Performance acceptable for large graphs
- [ ] Unicode characters render correctly

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 🏛️ Phase 7: Core Orchestration (The Heart)

### ☐ 13. `core/council.py` ⭐ MOST IMPORTANT (45-60 min)
**Why:** Main orchestration class (774 lines!)

**Review Items:**

#### Initialization & Setup
- [ ] Initialization sequence is logical
- [ ] Model validation logic works correctly
- [ ] Database health checks are thorough
- [ ] Cleanup handlers registered properly (atexit)
- [ ] All dependencies initialized in correct order

#### AI Integration
- [ ] Retry logic for Ollama calls (exponential backoff)
- [ ] Hybrid routing implementation matches `ai/router.py`
- [ ] MMR retrieval logic correct (relevance + diversity)
- [ ] Context scrubbing prevents data leakage
- [ ] Error handling for model failures

#### Logging & Classification
- [ ] Log classification uses AI appropriately
- [ ] Pending log review workflow is clear
- [ ] Auto-discovery integration works
- [ ] Graph updates triggered correctly

#### Project Management
- [ ] Project creation is safe (no path traversal)
- [ ] Project switching works correctly
- [ ] Project finalization extracts lessons
- [ ] Closed projects cannot be reopened
- [ ] Project listing/search works

#### Command Handling
- [ ] `/graph` command shows visualization
- [ ] `/review` command shows pending logs
- [ ] `/search` command integrates DuckDuckGo
- [ ] `/close` command finalizes project
- [ ] `status`/`sitrep` command generates report
- [ ] All commands have error handling

#### Main Event Loop
- [ ] Input handling is robust
- [ ] Exit conditions are clear
- [ ] State management is consistent
- [ ] User feedback is appropriate

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 14. `council.py` (Entry Point) (2 min)
**Why:** Simple entry point wrapper

**Review Items:**
- [ ] Import paths are correct
- [ ] Error handling for ImportError
- [ ] KeyboardInterrupt handled gracefully
- [ ] User-friendly error messages

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 🧪 Phase 8: Test Suite (Quality Assurance)

### ☐ 15. `tests/conftest.py` (10 min)
**Why:** Pytest fixtures and test configuration

**Review Items:**
- [ ] Mock setup is comprehensive
- [ ] Fixture scope is appropriate (function/module/session)
- [ ] Shared test utilities are reusable
- [ ] Temporary directories cleaned up
- [ ] No test pollution between tests

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 16. `tests/test_discovery_parser.py` (10 min)
**Why:** Tests for entity extraction

**Review Items:**
- [ ] Test cases cover all entity types
- [ ] Edge cases tested (malformed input, empty strings)
- [ ] False positive scenarios tested
- [ ] Expected behavior is clear from tests

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 17. `tests/test_router.py` (10 min)
**Why:** Tests for AI routing logic

**Review Items:**
- [ ] Routing decision examples are comprehensive
- [ ] Edge cases tested (ambiguous queries)
- [ ] Fallback behavior tested

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 18. `tests/test_attack_graph.py` (10 min)
**Why:** Tests for graph construction

**Review Items:**
- [ ] Graph building scenarios comprehensive
- [ ] Edge inference tested
- [ ] Node/edge creation tested
- [ ] Graph updates tested

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 19. `tests/test_graph_visualizer.py` (10 min)
**Why:** Tests for visualization

**Review Items:**
- [ ] Rendering edge cases tested
- [ ] Empty graph handling tested
- [ ] Output format validated

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 20. `tests/test_tools.py` (5 min)
**Why:** Tests for utility functions

**Review Items:**
- [ ] Sanitization tests comprehensive
- [ ] Search functionality tested
- [ ] Error cases covered

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 21-27. Other Test Files (Optional)
**Review Items:**
- [ ] Quick scan for any critical issues
- [ ] Verify tests are passing

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 📄 Phase 9: Documentation (Final Context)

### ☐ 28. `README.md` (10 min)
**Why:** Project overview and features

**Review Items:**
- [ ] Feature descriptions are accurate
- [ ] Installation instructions are complete
- [ ] Command reference is up-to-date
- [ ] Examples work as described
- [ ] No broken links
- [ ] Reflects current state of project

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 29. `WALKTHROUGH.md` (15 min)
**Why:** Detailed usage guide

**Review Items:**
- [ ] Example workflows are realistic
- [ ] Attack graph examples are accurate
- [ ] Best practices are sound
- [ ] Screenshots/examples are current

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 30. `QUICK_REFERENCE.md` (5 min)
**Why:** Command cheat sheet

**Review Items:**
- [ ] Command list is complete
- [ ] Descriptions are accurate
- [ ] Easy to scan and use

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

### ☐ 31. `SETUP_GUIDE.md` (5 min)
**Why:** Installation details

**Review Items:**
- [ ] Step-by-step instructions are accurate
- [ ] Troubleshooting tips are helpful
- [ ] Prerequisites are listed

**Notes:**
```
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## ✅ Universal Review Checklist

For **each file** reviewed, verify:

- [ ] **Purpose Clear:** I understand what this file does
- [ ] **No Secrets:** No API keys, passwords, or sensitive data
- [ ] **Error Handling:** Edge cases handled gracefully
- [ ] **Code Quality:** Readable, well-commented, follows conventions
- [ ] **Dependencies:** Imports are correct and necessary
- [ ] **TODOs/FIXMEs:** No unfinished work or critical issues
- [ ] **Security:** No path traversal, injection, or sanitization issues
- [ ] **Performance:** No obvious bottlenecks or inefficiencies

---

## 🚨 Pre-Push Security Checklist

**CRITICAL:** Before running `git push`, verify:

- [ ] No API keys or credentials in code
- [ ] `notes/` directory in `.gitignore`
- [ ] `projects/` directory in `.gitignore`
- [ ] No `.env` files committed
- [ ] No personal data in test fixtures
- [ ] No hardcoded file paths specific to my machine
- [ ] Model files (`.gguf`) excluded from git
- [ ] `.venv/` excluded from git
- [ ] `chroma_db/` excluded from git
- [ ] `__pycache__/` excluded from git

**Verify `.gitignore`:**
```bash
cat .gitignore
```

**Check what will be committed:**
```bash
git status
git diff --cached
```

---

## 🎯 Priority Files (Quick Review Mode)

If time-constrained, focus on these **critical files**:

1. [ ] `core/council.py` (Main logic - MUST review)
2. [ ] `core/config.py` (Check for secrets/paths)
3. [ ] `parsing/discovery_parser.py` (Core feature)
4. [ ] `graph/attack_graph.py` (New feature)
5. [ ] `ai/router.py` (AI routing logic)
6. [ ] `.gitignore` (Ensure secrets/data excluded)
7. [ ] `README.md` (Public-facing documentation)

---

## 📊 Review Progress Tracker

| Phase | Files | Status | Time Spent | Issues Found |
|-------|-------|--------|------------|--------------|
| Phase 1: Config | 1 | ☐ | _____ min | _____ |
| Phase 2: Utils | 2 | ☐ | _____ min | _____ |
| Phase 3: UI | 2 | ☐ | _____ min | _____ |
| Phase 4: AI | 3 | ☐ | _____ min | _____ |
| Phase 5: Parsing | 2 | ☐ | _____ min | _____ |
| Phase 6: Graph | 2 | ☐ | _____ min | _____ |
| Phase 7: Core | 2 | ☐ | _____ min | _____ |
| Phase 8: Tests | 6+ | ☐ | _____ min | _____ |
| Phase 9: Docs | 4 | ☐ | _____ min | _____ |
| **TOTAL** | **24+** | ☐ | **_____ min** | **_____** |

---

## 🐛 Issues Found During Review

### Critical Issues (Must Fix Before Push)
```
1. _____________________________________________________________________________
2. _____________________________________________________________________________
3. _____________________________________________________________________________
```

### Medium Issues (Should Fix Soon)
```
1. _____________________________________________________________________________
2. _____________________________________________________________________________
3. _____________________________________________________________________________
```

### Minor Issues (Nice to Have)
```
1. _____________________________________________________________________________
2. _____________________________________________________________________________
3. _____________________________________________________________________________
```

---

## ✅ Final Sign-Off

- [ ] All critical issues resolved
- [ ] Security checklist completed
- [ ] `.gitignore` verified
- [ ] `git status` reviewed
- [ ] Tests passing (`pytest tests/ -v`)
- [ ] Documentation accurate
- [ ] Ready for first push

**Reviewer:** _________________________  
**Date:** _________________________  
**Signature:** _________________________

---

## 💡 Pro Tips

1. **Use your IDE:** Open files in VS Code and use "Go to Definition" to trace function calls
2. **Run tests first:** `pytest tests/ -v` to see everything working
3. **Check git status:** `git status` to see what will be committed
4. **Review diffs:** `git diff` to see changes from any base state
5. **Take breaks:** This is a marathon, not a sprint
6. **Ask questions:** Mark anything unclear for follow-up

---

**Good luck with your review! 🚀**
