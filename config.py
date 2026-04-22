#!/usr/bin/env python3
"""
Configuration file for Llama Launcher
"""

import os
import json
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    "llama_cpp_path": "/home/anan/llama.cpp",
    "web_host": "0.0.0.0",
    "web_port": 8087,
    "default_mode": 0,  # 0: CLI, 1: Server, 2: Embedding
    "default_ctx_idx": 0,
    "default_ngl_idx": 4,
    "default_port": 8080,
    "large_model_threshold": 1024 * 1024 * 1024,  # 1GB
    "log_dir": "logs"
}

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config() -> Dict[str, Any]:
    """Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config file: {e}")
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config file: {e}")

# Load config
config = load_config()

# Export configuration variables
LLAMA_CPP_PATH = config.get("llama_cpp_path", DEFAULT_CONFIG["llama_cpp_path"])
WEB_HOST = config.get("web_host", DEFAULT_CONFIG["web_host"])
WEB_PORT = config.get("web_port", DEFAULT_CONFIG["web_port"])
DEFAULT_MODE = config.get("default_mode", DEFAULT_CONFIG["default_mode"])
DEFAULT_CTX_IDX = config.get("default_ctx_idx", DEFAULT_CONFIG["default_ctx_idx"])
DEFAULT_NGL_IDX = config.get("default_ngl_idx", DEFAULT_CONFIG["default_ngl_idx"])
DEFAULT_PORT = config.get("default_port", DEFAULT_CONFIG["default_port"])
LARGE_MODEL_THRESHOLD = config.get("large_model_threshold", DEFAULT_CONFIG["large_model_threshold"])
LOG_DIR = os.path.join(LLAMA_CPP_PATH, config.get("log_dir", DEFAULT_CONFIG["log_dir"]))
