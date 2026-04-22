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

# Global paths
LLAMA_CPP_PATH = DEFAULT_LLAMA_CPP_PATH
MODELS_PATH = os.path.join(LLAMA_CPP_PATH, "models")
BUILD_BIN_PATH = os.path.join(LLAMA_CPP_PATH, "build", "bin")
LOG_DIR = os.path.join(LLAMA_CPP_PATH, "logs")

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
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error loading config: {e}")
    return config

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file"""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error saving config: {e}")

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

def update_llama_cpp_path(new_path: str) -> Dict[str, str]:
    """Update the llama.cpp path and related paths"""
    global LLAMA_CPP_PATH, MODELS_PATH, BUILD_BIN_PATH, LOG_DIR
    LLAMA_CPP_PATH = new_path
    MODELS_PATH = os.path.join(LLAMA_CPP_PATH, "models")
    BUILD_BIN_PATH = os.path.join(LLAMA_CPP_PATH, "build", "bin")
    LOG_DIR = os.path.join(LLAMA_CPP_PATH, "logs")
    return {
        "llama_cpp_path": LLAMA_CPP_PATH,
        "models_path": MODELS_PATH,
        "build_bin_path": BUILD_BIN_PATH,
        "log_dir": LOG_DIR
    }

def get_current_paths() -> Dict[str, str]:
    """Get current paths"""
    return {
        "llama_cpp_path": LLAMA_CPP_PATH,
        "models_path": MODELS_PATH,
        "build_bin_path": BUILD_BIN_PATH,
        "log_dir": LOG_DIR
    }