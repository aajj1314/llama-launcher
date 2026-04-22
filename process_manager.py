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