#!/usr/bin/env python3
"""
Shared State Manager - Singleton pattern for TUI and WebUI state synchronization
"""

import os
import threading
import time
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
import logging

# Import configuration
from config import (
    LLAMA_CPP_PATH, WEB_HOST, WEB_PORT, DEFAULT_MODE,
    DEFAULT_CTX_IDX, DEFAULT_NGL_IDX, DEFAULT_PORT,
    LARGE_MODEL_THRESHOLD, LOG_DIR
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ServerStats:
    """Server metrics data class"""
    prompt_tokens: int = 0
    eval_tokens: int = 0
    prompt_per_second: float = 0.0
    eval_per_second: float = 0.0
    ctx_used: int = 0
    ctx_total: int = 0
    total_time: float = 0.0

    def is_valid(self) -> bool:
        return self.eval_tokens > 0 or self.prompt_tokens > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "eval_tokens": self.eval_tokens,
            "prompt_per_second": self.prompt_per_second,
            "eval_per_second": self.eval_per_second,
            "ctx_used": self.ctx_used,
            "ctx_total": self.ctx_total,
            "total_time": self.total_time
        }


@dataclass
class ModelInfo:
    """Model information"""
    name: str
    path: str
    size: int


@dataclass
class AppState:
    """Application state container"""
    # Process info
    is_running: bool = False
    process_pid: Optional[int] = None
    process_obj: Optional[Any] = None
    
    # Model info
    current_model_name: str = ""
    current_model_path: str = ""
    current_mode: int = DEFAULT_MODE  # 0: CLI, 1: Server, 2: Embedding
    
    # Configuration
    ctx_idx: int = DEFAULT_CTX_IDX
    ngl_idx: int = DEFAULT_NGL_IDX
    port: int = DEFAULT_PORT
    
    # Models
    models: List[Dict[str, Any]] = field(default_factory=list)
    
    # Server stats
    server_stats: ServerStats = field(default_factory=ServerStats)
    
    # Log file path
    log_file: str = ""
    
    # WebUI status
    webui_online: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "process_pid": self.process_pid,
            "current_model_name": self.current_model_name,
            "current_model_path": self.current_model_path,
            "current_mode": self.current_mode,
            "current_mode_name": ["CLI", "Server", "Embedding"][self.current_mode] if 0 <= self.current_mode <= 2 else "Unknown",
            "ctx_idx": self.ctx_idx,
            "ctx_size": CTX_SIZE_OPTIONS[self.ctx_idx] if 0 <= self.ctx_idx < len(CTX_SIZE_OPTIONS) else CTX_SIZE_OPTIONS[0],
            "ngl_idx": self.ngl_idx,
            "ngl": NGL_OPTIONS[self.ngl_idx] if 0 <= self.ngl_idx < len(NGL_OPTIONS) else NGL_OPTIONS[0],
            "port": self.port,
            "models": self.models,
            "server_stats": self.server_stats.to_dict(),
            "log_file": self.log_file,
            "webui_online": self.webui_online
        }


class StateManager:
    """
    Singleton State Manager for TUI and WebUI synchronization.
    Uses threading locks for thread-safe state access.
    """
    _instance: Optional['StateManager'] = None
    _lock = threading.Lock()
    _state_lock = threading.RLock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._state = AppState()
        self._callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._callbacks_lock = threading.Lock()
        logger.info("StateManager initialized")
    
    @property
    def state(self) -> AppState:
        """Get current state (thread-safe)"""
        with self._state_lock:
            return self._state
    
    def get_state(self) -> Dict[str, Any]:
        """Get state as dictionary (for API responses)"""
        with self._state_lock:
            return self._state.to_dict()
    
    def set_models(self, models: List[Dict[str, Any]]) -> None:
        """Update model list"""
        with self._state_lock:
            self._state.models = models
            self._notify_watchers()
    
    def set_config(self, ctx_idx: int = None, ngl_idx: int = None, port: int = None) -> None:
        """Update configuration"""
        with self._state_lock:
            if ctx_idx is not None:
                self._state.ctx_idx = ctx_idx
            if ngl_idx is not None:
                self._state.ngl_idx = ngl_idx
            if port is not None:
                self._state.port = port
            self._notify_watchers()
    
    def set_run_mode(self, mode: int) -> None:
        """Set run mode (0: CLI, 1: Server, 2: Embedding)"""
        with self._state_lock:
            if 0 <= mode <= 2:
                self._state.current_mode = mode
                self._notify_watchers()
    
    def set_process(self, is_running: bool, pid: Optional[int] = None, 
                    process_obj: Any = None, model_name: str = "", 
                    model_path: str = "", mode: int = 0, log_file: str = "") -> None:
        """Update process status"""
        with self._state_lock:
            self._state.is_running = is_running
            self._state.process_pid = pid
            self._state.process_obj = process_obj
            self._state.current_model_name = model_name
            self._state.current_model_path = model_path
            self._state.current_mode = mode
            self._state.log_file = log_file
            if not is_running:
                self._state.server_stats = ServerStats()
            self._notify_watchers()
    
    def update_stats(self, stats: ServerStats) -> None:
        """Update server stats"""
        with self._state_lock:
            self._state.server_stats = stats
            # Don't notify for stats updates to avoid flooding
    
    def set_webui_status(self, online: bool) -> None:
        """Set WebUI online status"""
        with self._state_lock:
            self._state.webui_online = online
            self._notify_watchers()
    
    def register_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a state change callback"""
        with self._callbacks_lock:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Unregister a state change callback"""
        with self._callbacks_lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
    
    def _notify_watchers(self) -> None:
        """Notify all registered callbacks of state change"""
        with self._callbacks_lock:
            callbacks = self._callbacks.copy()
        state_dict = self._state.to_dict()
        for callback in callbacks:
            try:
                callback(state_dict)
            except Exception as e:
                logger.error(f"Error in state callback: {e}")
    
    def clear_process(self) -> None:
        """Clear process info when stopped"""
        with self._state_lock:
            self._state.is_running = False
            self._state.process_pid = None
            self._state.process_obj = None
            self._state.log_file = ""
            self._state.server_stats = ServerStats()
            self._notify_watchers()


def get_state_manager() -> StateManager:
    """Get the singleton StateManager instance"""
    return StateManager()


# Constants (shared with main application)
MODELS_PATH = os.path.join(LLAMA_CPP_PATH, "models")
BUILD_BIN_PATH = os.path.join(LLAMA_CPP_PATH, "build", "bin")

CTX_SIZE_OPTIONS = [4096, 8192, 16384, 32768, 65536, 131072]
NGL_OPTIONS = [0, 33, 66, 99, 999]


def format_size(size: int) -> str:
    """Format file size to human readable string"""
    if size >= 1024 ** 3:
        return f"{size / (1024 ** 3):.2f} GB"
    elif size >= 1024 ** 2:
        return f"{size / (1024 ** 2):.2f} MB"
    elif size >= 1024:
        return f"{size / 1024:.2f} KB"
    return f"{size} B"


def format_ctx(ctx: int) -> str:
    """Format context size"""
    if ctx >= 1024:
        return f"{ctx // 1024}k"
    return str(ctx)


def scan_models(models_path: str = None) -> List[Dict[str, Any]]:
    """Scan for GGUF model files"""
    if models_path is None:
        models_path = MODELS_PATH
    
    models = []
    try:
        os.makedirs(models_path, exist_ok=True)
        for entry in os.listdir(models_path):
            entry_path = os.path.join(models_path, entry)
            if os.path.isfile(entry_path) and entry.endswith(".gguf"):
                stat_info = os.stat(entry_path)
                # Show all models regardless of size for WebUI
                models.append({
                    "name": entry,
                    "path": entry_path,
                    "size": stat_info.st_size,
                    "size_formatted": format_size(stat_info.st_size)
                })
    except Exception as e:
        logger.error(f"Error scanning models: {e}")
    
    return sorted(models, key=lambda m: m["name"])