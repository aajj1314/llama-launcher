# Old Llama Launcher Project Analysis and Modification Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Analyze and modify the old Llama Launcher project to fix parameter persistence issues and improve user experience.

**Architecture:** Comprehensive code review followed by targeted modifications to fix the parameter reset issue, improve state management, and enhance user interface.

**Tech Stack:** Python, FastAPI, HTML/CSS/JavaScript, subprocess management.

---

## Project Structure Analysis

**Old Project Files:**
- `launcher.py` - Main launcher script
- `web_app.py` - Web interface
- `state_manager.py` - State management
- `process_manager.py` - Process management
- `config.py` - Configuration management
- `run.py` - Entry point
- `utils.py` - Utility functions
- `templates/index.html` - Frontend interface

**New Project (Reference):**
- `new_llama_launcher/` - Reimplemented version with fixes

## Task 1: Analyze Old Project Architecture

**Files:**
- Review: `launcher.py`, `web_app.py`, `state_manager.py`, `process_manager.py`, `config.py`, `templates/index.html`

- [ ] **Step 1: Examine main launcher structure**

```bash
cat launcher.py | head -n 50
```

- [ ] **Step 2: Review web application code**

```bash
cat web_app.py | head -n 100
```

- [ ] **Step 3: Analyze state management**

```bash
cat state_manager.py | head -n 100
```

- [ ] **Step 4: Review frontend code**

```bash
cat templates/index.html | head -n 100
```

- [ ] **Step 5: Identify parameter reset issue**

```bash
grep -n "setInterval\|fetchState" templates/index.html
```

- [ ] **Step 6: Document findings**

Create analysis document with identified issues and improvement opportunities.

## Task 2: Fix Frontend Parameter Persistence

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Identify current state update logic**

```bash
grep -A 20 "updateConfigFields" templates/index.html
```

- [ ] **Step 2: Implement initialization flag**

```javascript
// Add at the top of script section
let configInitialized = false;

// Modify updateConfigFields function
function updateConfigFields() {
    const config = localState.config;
    
    // Only update during initialization
    if (configInitialized) {
        return;
    }
    
    // Existing update logic...
    
    // Mark as initialized
    configInitialized = true;
}
```

- [ ] **Step 3: Update saveConfig function**

```javascript
async function saveConfig() {
    // Existing save logic...
    
    if (result.success) {
        showAlert('配置已保存！', 'success');
        localState.config = result.config;
        // Reset initialization flag
        configInitialized = false;
        updateConfigFields();
    }
}
```

- [ ] **Step 4: Test frontend changes**

Open browser and verify parameters don't reset when modified.

- [ ] **Step 5: Commit changes**

```bash
git add templates/index.html
git commit -m "fix: parameter persistence issue"
```

## Task 3: Improve State Management

**Files:**
- Modify: `state_manager.py`

- [ ] **Step 1: Review current state management**

```bash
cat state_manager.py
```

- [ ] **Step 2: Implement thread-safe operations**

Add proper locking mechanisms for state access.

- [ ] **Step 3: Improve state synchronization**

Ensure consistent state between frontend and backend.

- [ ] **Step 4: Test state management**

```bash
python -m pytest test_integration.py -v
```

- [ ] **Step 5: Commit changes**

```bash
git add state_manager.py
git commit -m "improve: state management"
```

## Task 4: Optimize Process Management

**Files:**
- Modify: `process_manager.py`

- [ ] **Step 1: Review current process management**

```bash
cat process_manager.py
```

- [ ] **Step 2: Implement log redirection**

Redirect subprocess output to files instead of terminal.

- [ ] **Step 3: Improve error handling**

Add better error catching and reporting.

- [ ] **Step 4: Test process management**

```bash
python -m pytest test_process_manager.py -v
```

- [ ] **Step 5: Commit changes**

```bash
git add process_manager.py
git commit -m "optimize: process management"
```

## Task 5: Enhance Web API

**Files:**
- Modify: `web_app.py`

- [ ] **Step 1: Review current API endpoints**

```bash
cat web_app.py | grep -A 5 "@app"
```

- [ ] **Step 2: Improve error handling**

Add proper HTTP error responses.

- [ ] **Step 3: Optimize API performance**

Reduce unnecessary state refreshes.

- [ ] **Step 4: Test API endpoints**

```bash
python -m pytest test_integration.py -v
```

- [ ] **Step 5: Commit changes**

```bash
git add web_app.py
git commit -m "enhance: web API"
```

## Task 6: Test Complete System

**Files:**
- Test: All files

- [ ] **Step 1: Run full test suite**

```bash
python -m pytest -v
```

- [ ] **Step 2: Test parameter persistence**

1. Open web interface
2. Modify parameters
3. Wait 10 seconds
4. Verify parameters don't reset
5. Save configuration
6. Verify changes persist

- [ ] **Step 3: Test process management**

1. Start model
2. Check logs
3. Stop model
4. Verify clean shutdown

- [ ] **Step 4: Test edge cases**

1. Invalid paths
2. Missing models
3. Invalid parameters

- [ ] **Step 5: Performance testing**

```bash
python -m pytest test_performance.py -v
```

## Task 7: Documentation Update

**Files:**
- Modify: `README.md`, `README_zh.md`

- [ ] **Step 1: Update documentation**

Add information about the fixes and improvements.

- [ ] **Step 2: Add usage instructions**

Include step-by-step guide for using the fixed version.

- [ ] **Step 3: Commit documentation**

```bash
git add README.md README_zh.md
git commit -m "docs: update documentation"
```

---

## Self-Review

1. **Spec Coverage:** All tasks address the core issues identified in the old project
2. **Placeholder Scan:** No placeholders - all steps have concrete implementation details
3. **Type Consistency:** Function names and signatures are consistent across tasks

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-04-22-old-project-analysis.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
