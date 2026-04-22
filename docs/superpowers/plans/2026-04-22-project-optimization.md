# Llama Launcher Optimization Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Optimize the Llama Launcher project for better performance, code quality, and maintainability

**Architecture:** Refactor codebase to eliminate duplication, improve error handling, enhance performance, and add missing features

**Tech Stack:** Python, FastAPI, Uvicorn, llama.cpp

---

## File Structure

**Current files to modify:**
- `run.py` - TUI interface and main logic
- `state_manager.py` - State management
- `web_app.py` - WebUI implementation
- `templates/index.html` - WebUI frontend

**New files to create:**
- `utils.py` - Shared utility functions
- `config.py` - Configuration management
- `process_manager.py` - Process management

---

### Task 1: Create Shared Utility Module

**Files:**
- Create: `utils.py`
- Modify: `run.py:132-166`, `web_app.py:86-122`

- [ ] **Step 1: Create utils.py with shared functions**

```python
#!/usr/bin/env python3
"""
Shared utility functions for llama-launcher
"""

import re
from typing import Optional
from state_manager import ServerStats

def parse_server_log(log_file: str) -> ServerStats:
    """Parse server log to extract metrics"""
    stats = ServerStats()
    if not log_file:
        return stats
    
    try:
        with open(log_file, "r") as f:
            content = f.read()
        
        prompt_match = re.search(r'prompt token.*?(\d+)', content, re.IGNORECASE)
        if prompt_match:
            stats.prompt_tokens = int(prompt_match.group(1))
        
        eval_match = re.search(r'evaluation.*?(\d+) tokens', content, re.IGNORECASE)
        if eval_match:
            stats.eval_tokens = int(eval_match.group(1))
        
        ppd_match = re.search(r'prompt.*?(\d+\.?\d*) tok/ ?s', content, re.IGNORECASE)
        if ppd_match:
            stats.prompt_per_second = float(ppd_match.group(1))
        
        epd_match = re.search(r'(\d+\.?\d*) tok/ ?s', content)
        if epd_match:
            stats.eval_per_second = float(epd_match.group(1))
        
        ctx_match = re.search(r'context.*?(\d+)/(\d+)', content, re.IGNORECASE)
        if ctx_match:
            stats.ctx_used = int(ctx_match.group(1))
            stats.ctx_total = int(ctx_match.group(2))
        
        time_match = re.search(r'(\d+\.?\d+) s', content)
        if time_match:
            stats.total_time = float(time_match.group(1))
    except Exception as e:
        from state_manager import logger
        logger.error(f"Error parsing server log: {e}")
    return stats

def terminate_process(proc: Optional[subprocess.Popen], timeout: int = 5) -> bool:
    """Terminate a process gracefully"""
    if not proc or proc.poll() is not None:
        return True
    try:
        proc.terminate()
        proc.wait(timeout=timeout)
        return True
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return True
    except Exception as e:
        from state_manager import logger
        logger.error(f"Error terminating process: {e}")
        return False
```

- [ ] **Step 2: Update run.py to use shared utils**

```python
# Add import
from utils import parse_server_log, terminate_process

# Remove duplicate functions
# Delete lines 132-166 (parse_server_log)
# Delete lines 121-130 (terminate_process)
```

- [ ] **Step 3: Update web_app.py to use shared utils**

```python
# Add import
from utils import parse_server_log, terminate_process

# Remove duplicate functions
# Delete lines 86-122 (parse_server_log)
# Delete lines 125-139 (terminate_process)
```

- [ ] **Step 4: Test the changes**

Run: `python3 run.py`
Expected: Application starts without errors

- [ ] **Step 5: Commit**

```bash
git add utils.py run.py web_app.py
git commit -m "refactor: create shared utility module"
```

### Task 2: Improve Configuration Management

**Files:**
- Create: `config.py`
- Modify: `state_manager.py:15-62`

- [ ] **Step 1: Create config.py**

```python
#!/usr/bin/env python3
"""
Configuration management for llama-launcher
"""

import os
import json
from typing import Dict, Any

# Default values
DEFAULT_LLAMA_CPP_PATH = os.environ.get("LLAMA_CPP_PATH", "/home/anan/llama.cpp")
DEFAULT_PORT = 8000
DEFAULT_TIMEOUT = 30
DEFAULT_LOG_LEVEL = "INFO"

# Configuration file path
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".llama_launcher_config.json")

# Context size options
CTX_SIZE_OPTIONS = [4096, 8192, 16384, 32768, 65536, 131072]

# NGL options
NGL_OPTIONS = [0, 33, 66, 99, 999]

# Large model threshold
LARGE_MODEL_THRESHOLD = 1024 * 1024 * 1024  # 1GB

def load_config() -> Dict[str, Any]:
    """Load configuration from file"""
    config = {}
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
    return config

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file"""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config: {e}")

def get_paths(llama_cpp_path: str) -> Dict[str, str]:
    """Get all paths based on llama_cpp_path"""
    return {
        "llama_cpp_path": llama_cpp_path,
        "models_path": os.path.join(llama_cpp_path, "models"),
        "build_bin_path": os.path.join(llama_cpp_path, "build", "bin"),
        "log_dir": os.path.join(llama_cpp_path, "logs")
    }

def create_directories(paths: Dict[str, str]) -> None:
    """Create necessary directories"""
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
```

- [ ] **Step 2: Update state_manager.py to use config.py**

```python
# Add import
from config import (
    load_config, save_config, get_paths, create_directories,
    DEFAULT_LLAMA_CPP_PATH, CTX_SIZE_OPTIONS, NGL_OPTIONS,
    LARGE_MODEL_THRESHOLD
)

# Update constants section
LLAMA_CPP_PATH = DEFAULT_LLAMA_CPP_PATH
_paths = get_paths(LLAMA_CPP_PATH)
MODELS_PATH = _paths["models_path"]
BUILD_BIN_PATH = _paths["build_bin_path"]
LOG_DIR = _paths["log_dir"]

# Update _load_config method
# Modify lines 191-260 to use config.py functions
```

- [ ] **Step 3: Test configuration loading**

Run: `python3 run.py`
Expected: Configuration loads correctly

- [ ] **Step 4: Commit**

```bash
git add config.py state_manager.py
git commit -m "refactor: improve configuration management"
```

### Task 3: Enhance Process Management

**Files:**
- Create: `process_manager.py`
- Modify: `run.py:271-303`, `web_app.py:143-181`

- [ ] **Step 1: Create process_manager.py**

```python
#!/usr/bin/env python3
"""
Process management for llama-launcher
"""

import os
import subprocess
from typing import Optional, Tuple

from state_manager import BUILD_BIN_PATH, LOG_DIR

def run_cli(model_path: str, ctx_size: int, ngl: int) -> Optional[subprocess.Popen]:
    """Run CLI mode"""
    try:
        args = [
            os.path.join(BUILD_BIN_PATH, "llama-cli"),
            "-m", model_path,
            "-ngl", str(ngl),
            "-c", str(ctx_size),
            "--color", "on"
        ]
        return subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        from state_manager import logger
        logger.error(f"Error running CLI: {e}")
        return None

def run_server(model_path: str, ctx_size: int, ngl: int, port: int) -> Tuple[Optional[subprocess.Popen], str]:
    """Run Server mode"""
    try:
        import os
        os.makedirs(LOG_DIR, exist_ok=True)
        log_file = os.path.join(LOG_DIR, f"server_{port}.log")
        with open(log_file, "w") as f:
            f.write("")
        args = [
            os.path.join(BUILD_BIN_PATH, "llama-server"),
            "-m", model_path,
            "-ngl", str(ngl),
            "-c", str(ctx_size),
            "--port", str(port),
            "--host", "0.0.0.0"
        ]
        with open(log_file, "a") as f:
            proc = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT)
        return proc, log_file
    except Exception as e:
        from state_manager import logger
        logger.error(f"Error running Server: {e}")
        return None, ""

def run_embedding(model_path: str, ngl: int) -> Optional[subprocess.Popen]:
    """Run Embedding mode"""
    try:
        args = [
            os.path.join(BUILD_BIN_PATH, "llama-embedding"),
            "-m", model_path,
            "-ngl", str(ngl)
        ]
        return subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        from state_manager import logger
        logger.error(f"Error running Embedding: {e}")
        return None

def validate_binary(mode: int) -> bool:
    """Validate that required binary exists"""
    binaries = {
        0: "llama-cli",
        1: "llama-server",
        2: "llama-embedding"
    }
    binary_name = binaries.get(mode)
    if not binary_name:
        return False
    binary_path = os.path.join(BUILD_BIN_PATH, binary_name)
    return os.path.exists(binary_path)
```

- [ ] **Step 2: Update run.py to use process_manager**

```python
# Add import
from process_manager import run_cli, run_server, run_embedding

# Replace process functions
# Delete lines 271-303 (run_cli, run_server, run_embedding)
```

- [ ] **Step 3: Update web_app.py to use process_manager**

```python
# Add import
from process_manager import run_cli, run_server, run_embedding, validate_binary

# Replace process functions and add validation
# Delete lines 143-181 (run_cli, run_server, run_embedding)
# Update start_model endpoint to use validate_binary
```

- [ ] **Step 4: Test process management**

Run: `python3 run.py`
Expected: Processes start and stop correctly

- [ ] **Step 5: Commit**

```bash
git add process_manager.py run.py web_app.py
git commit -m "refactor: enhance process management"
```

### Task 4: Improve Error Handling and Logging

**Files:**
- Modify: `run.py`, `state_manager.py`, `web_app.py`

- [ ] **Step 1: Enhance error handling in run.py**

```python
# Add proper error handling around subprocess calls
# Add try-except blocks for critical operations
# Improve error messages
```

- [ ] **Step 2: Improve logging in state_manager.py**

```python
# Add more detailed logging
# Add log rotation configuration
# Improve error logging
```

- [ ] **Step 3: Enhance error handling in web_app.py**

```python
# Add more comprehensive error handling
# Improve API error responses
# Add validation for all inputs
```

- [ ] **Step 4: Test error handling**

Run: `python3 run.py`
Expected: Application handles errors gracefully

- [ ] **Step 5: Commit**

```bash
git add run.py state_manager.py web_app.py
git commit -m "improve: error handling and logging"
```

### Task 5: Implement Missing WebUI Features

**Files:**
- Modify: `run.py:448-457`, `web_app.py`, `templates/index.html`

- [ ] **Step 1: Implement WebUI toggle in run.py**

```python
# Update the WebUI toggle functionality
# Add proper implementation for 'w' key press
```

- [ ] **Step 2: Enhance WebUI API endpoints**

```python
# Add more comprehensive API endpoints
# Improve response formats
# Add health check endpoint
```

- [ ] **Step 3: Update WebUI frontend**

```html
<!-- Improve the WebUI interface -->
<!-- Add real-time metrics display -->
<!-- Improve responsiveness -->
```

- [ ] **Step 4: Test WebUI features**

Run: `python3 web_app.py`
Expected: WebUI loads and functions correctly

- [ ] **Step 5: Commit**

```bash
git add run.py web_app.py templates/index.html
git commit -m "feat: implement WebUI features"
```

### Task 6: Performance Optimizations

**Files:**
- Modify: `state_manager.py:541-565`, `run.py:87-114`

- [ ] **Step 1: Optimize model scanning**

```python
# Add caching for model scans
# Implement incremental scanning
# Improve performance for large directories
```

- [ ] **Step 2: Optimize stats parsing**

```python
# Add incremental log parsing
# Implement caching for stats
# Reduce I/O operations
```

- [ ] **Step 3: Optimize thread management**

```python
# Improve thread synchronization
# Reduce unnecessary thread creation
# Optimize stats update frequency
```

- [ ] **Step 4: Test performance improvements**

Run: `python3 run.py`
Expected: Application starts faster and uses less resources

- [ ] **Step 5: Commit**

```bash
git add state_manager.py run.py
git commit -m "optimize: performance improvements"
```

### Task 7: Security Enhancements

**Files:**
- Modify: `web_app.py`, `state_manager.py`

- [ ] **Step 1: Add input validation**

```python
# Add validation for all user inputs
# Sanitize file paths and commands
# Implement proper error handling for invalid inputs
```

- [ ] **Step 2: Improve CORS configuration**

```python
# Restrict CORS origins to specific domains
# Add proper CORS headers
# Implement security best practices
```

- [ ] **Step 3: Enhance process security**

```python
# Add process validation
# Implement proper process termination
# Add resource limits for processes
```

- [ ] **Step 4: Test security enhancements**

Run: `python3 run.py`
Expected: Application handles security edge cases

- [ ] **Step 5: Commit**

```bash
git add web_app.py state_manager.py
git commit -m "security: enhance security measures"
```

### Task 8: Code Quality Improvements

**Files:**
- Modify: `run.py`, `state_manager.py`, `web_app.py`

- [ ] **Step 1: Add type annotations**

```python
# Add comprehensive type annotations
# Improve type consistency
# Add type checking
```

- [ ] **Step 2: Improve code structure**

```python
# Refactor large functions
# Improve code organization
# Add documentation
```

- [ ] **Step 3: Implement linting and formatting**

```python
# Add linting configuration
# Implement code formatting
# Ensure code consistency
```

- [ ] **Step 4: Test code quality**

Run: `python3 -m pylint run.py state_manager.py web_app.py`
Expected: No major linting errors

- [ ] **Step 5: Commit**

```bash
git add run.py state_manager.py web_app.py
git commit -m "quality: improve code quality"
```

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-04-22-project-optimization.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**