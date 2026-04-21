#!/usr/bin/env python3
"""
Shared State Manager - Singleton pattern for TUI and WebUI state synchronization
"""

import os
import threading
import time
import json
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
import logging

# Constants (shared with main application)
LLAMA_CPP_PATH = os.environ.get("LLAMA_CPP_PATH", "/home/anan/llama.cpp")
MODELS_PATH = os.path.join(LLAMA_CPP_PATH, "models")
BUILD_BIN_PATH = os.path.join(LLAMA_CPP_PATH, "build", "bin")
LOG_DIR = os.path.join(LLAMA_CPP_PATH, "logs")

# Configure logging
import logging.handlers

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler with rotation
log_file = os.path.join(LOG_DIR, "llama_launcher.log")
file_handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB per file
    backupCount=5  # Keep up to 5 backup files
)

# Create console handler
console_handler = logging.StreamHandler()

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Set formatters
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

CTX_SIZE_OPTIONS = [4096, 8192, 16384, 32768, 65536, 131072]
NGL_OPTIONS = [0, 33, 66, 99, 999]
LARGE_MODEL_THRESHOLD = 1024 * 1024 * 1024  # 1GB

# Configuration file path
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".llama_launcher_config.json")


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
    current_mode: int = 0  # 0: CLI, 1: Server, 2: Embedding
    
    # Configuration
    ctx_idx: int = 0
    ngl_idx: int = 4
    port: int = 80
    llama_cpp_path: str = LLAMA_CPP_PATH
    timeout: int = 30  # Model loading timeout in seconds
    log_level: str = "INFO"  # Log level: DEBUG, INFO, WARNING, ERROR
    gpu_memory: int = 0  # GPU memory limit in MB (0 = no limit)
    
    # Models
    models: List[Dict[str, Any]] = field(default_factory=list)
    
    # Server stats
    server_stats: ServerStats = field(default_factory=ServerStats)
    
    # Log file path
    log_file: str = ""
    
    # WebUI status
    webui_online: bool = False
    
    # TUI status
    tui_online: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "process_pid": self.process_pid,
            "current_model_name": self.current_model_name,
            "current_model_path": self.current_model_path,
            "current_mode": self.current_mode,
            "current_mode_name": ["CLI", "Server", "Embedding"][self.current_mode] if 0 <= self.current_mode <= 2 else "Unknown",
            "ctx_idx": self.ctx_idx,
            "ctx_size": CTX_SIZE_OPTIONS[self.ctx_idx] if 0 <= self.ctx_idx < len(CTX_SIZE_OPTIONS) else 4096,
            "ngl_idx": self.ngl_idx,
            "ngl": NGL_OPTIONS[self.ngl_idx] if 0 <= self.ngl_idx < len(NGL_OPTIONS) else 0,
            "port": self.port,
            "llama_cpp_path": self.llama_cpp_path,
            "timeout": self.timeout,
            "log_level": self.log_level,
            "gpu_memory": self.gpu_memory,
            "models": self.models,
            "server_stats": self.server_stats.to_dict(),
            "log_file": self.log_file,
            "webui_online": self.webui_online,
            "tui_online": self.tui_online
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
        
        # Load configuration from file
        self._load_config()
        
        logger.info("StateManager initialized")
    
    def _load_config(self):
        """Load configuration from file into state"""
        # Declare global variables at the beginning
        global LLAMA_CPP_PATH, MODELS_PATH, BUILD_BIN_PATH, LOG_DIR
        
        try:
            config = load_config()
            if config:
                # Load path configurations
                if "llama_cpp_path" in config:
                    # Validate path exists
                    if os.path.exists(config["llama_cpp_path"]):
                        LLAMA_CPP_PATH = config["llama_cpp_path"]
                        MODELS_PATH = os.path.join(LLAMA_CPP_PATH, "models")
                        BUILD_BIN_PATH = os.path.join(LLAMA_CPP_PATH, "build", "bin")
                        LOG_DIR = os.path.join(LLAMA_CPP_PATH, "logs")
                        # Create necessary directories
                        for path in [MODELS_PATH, BUILD_BIN_PATH, LOG_DIR]:
                            os.makedirs(path, exist_ok=True)
                        # Update state
                        self._state.llama_cpp_path = LLAMA_CPP_PATH
                    else:
                        logger.warning(f"Configured llama_cpp_path does not exist: {config['llama_cpp_path']}")
                
                # Load application settings with validation
                if "ctx_idx" in config:
                    if 0 <= config["ctx_idx"] < len(CTX_SIZE_OPTIONS):
                        self._state.ctx_idx = config["ctx_idx"]
                    else:
                        logger.warning(f"Invalid ctx_idx in config: {config['ctx_idx']}, using default")
                if "ngl_idx" in config:
                    if 0 <= config["ngl_idx"] < len(NGL_OPTIONS):
                        self._state.ngl_idx = config["ngl_idx"]
                    else:
                        logger.warning(f"Invalid ngl_idx in config: {config['ngl_idx']}, using default")
                if "port" in config:
                    if 1 <= config["port"] <= 65535:
                        self._state.port = config["port"]
                    else:
                        logger.warning(f"Invalid port in config: {config['port']}, using default")
                if "current_mode" in config:
                    if 0 <= config["current_mode"] <= 2:
                        self._state.current_mode = config["current_mode"]
                    else:
                        logger.warning(f"Invalid current_mode in config: {config['current_mode']}, using default")
                if "timeout" in config:
                    if config["timeout"] > 0:
                        self._state.timeout = config["timeout"]
                    else:
                        logger.warning(f"Invalid timeout in config: {config['timeout']}, using default")
                if "log_level" in config:
                    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
                    if config["log_level"].upper() in valid_log_levels:
                        self._state.log_level = config["log_level"].upper()
                        # Update logging level
                        logger.setLevel(getattr(logging, config["log_level"].upper()))
                    else:
                        logger.warning(f"Invalid log_level in config: {config['log_level']}, using default")
                if "gpu_memory" in config:
                    if config["gpu_memory"] >= 0:
                        self._state.gpu_memory = config["gpu_memory"]
                    else:
                        logger.warning(f"Invalid gpu_memory in config: {config['gpu_memory']}, using default")
        except Exception as e:
            logger.error(f"Error in _load_config: {e}")
            # Ensure default directories exist
            os.makedirs(MODELS_PATH, exist_ok=True)
            os.makedirs(BUILD_BIN_PATH, exist_ok=True)
            os.makedirs(LOG_DIR, exist_ok=True)
            # Update state with default path
            self._state.llama_cpp_path = LLAMA_CPP_PATH
    
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
    
    def set_config(self, ctx_idx: int = None, ngl_idx: int = None, port: int = None, 
                   timeout: int = None, log_level: str = None, gpu_memory: int = None) -> bool:
        """Update configuration with validation"""
        try:
            with self._state_lock:
                if ctx_idx is not None:
                    if 0 <= ctx_idx < len(CTX_SIZE_OPTIONS):
                        self._state.ctx_idx = ctx_idx
                    else:
                        logger.warning(f"Invalid ctx_idx: {ctx_idx}, using current value")
                if ngl_idx is not None:
                    if 0 <= ngl_idx < len(NGL_OPTIONS):
                        self._state.ngl_idx = ngl_idx
                    else:
                        logger.warning(f"Invalid ngl_idx: {ngl_idx}, using current value")
                if port is not None:
                    if 1 <= port <= 65535:
                        self._state.port = port
                    else:
                        logger.warning(f"Invalid port: {port}, using current value")
                if timeout is not None:
                    if timeout > 0:
                        self._state.timeout = timeout
                    else:
                        logger.warning(f"Invalid timeout: {timeout}, using current value")
                if log_level is not None:
                    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
                    if log_level.upper() in valid_log_levels:
                        self._state.log_level = log_level.upper()
                        # Update logging level
                        logger.setLevel(getattr(logging, log_level.upper()))
                    else:
                        logger.warning(f"Invalid log_level: {log_level}, using current value")
                if gpu_memory is not None:
                    if gpu_memory >= 0:
                        self._state.gpu_memory = gpu_memory
                    else:
                        logger.warning(f"Invalid gpu_memory: {gpu_memory}, using current value")
                self._notify_watchers()
            # Save configuration to file
            self._save_config()
            return True
        except Exception as e:
            logger.error(f"Error in set_config: {e}")
            return False
    
    def _save_config(self):
        """Save current state to configuration file"""
        try:
            with self._state_lock:
                config = {
                    "llama_cpp_path": LLAMA_CPP_PATH,
                    "ctx_idx": self._state.ctx_idx,
                    "ngl_idx": self._state.ngl_idx,
                    "port": self._state.port,
                    "current_mode": self._state.current_mode,
                    "timeout": self._state.timeout,
                    "log_level": self._state.log_level,
                    "gpu_memory": self._state.gpu_memory
                }
            save_config(config)
            logger.debug("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error in _save_config: {e}")
    
    def set_run_mode(self, mode: int) -> bool:
        """Set run mode (0: CLI, 1: Server, 2: Embedding) with validation"""
        try:
            if 0 <= mode <= 2:
                with self._state_lock:
                    self._state.current_mode = mode
                    self._notify_watchers()
                # Save configuration to file
                self._save_config()
                return True
            else:
                logger.warning(f"Invalid run mode: {mode}, must be 0, 1, or 2")
                return False
        except Exception as e:
            logger.error(f"Error in set_run_mode: {e}")
            return False
    
    def set_process(self, is_running: bool, pid: Optional[int] = None, 
                    process_obj: Any = None, model_name: str = "", 
                    model_path: str = "", mode: int = 0, log_file: str = "") -> bool:
        """Update process status with validation"""
        try:
            with self._state_lock:
                # Validate parameters
                if is_running:
                    if pid is not None and not isinstance(pid, int):
                        logger.warning(f"Invalid pid: {pid}, setting to None")
                        pid = None
                    if mode < 0 or mode > 2:
                        logger.warning(f"Invalid mode: {mode}, using 0 (CLI)")
                        mode = 0
                
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
            return True
        except Exception as e:
            logger.error(f"Error in set_process: {e}")
            return False
    
    def update_stats(self, stats: ServerStats) -> bool:
        """Update server stats with validation"""
        try:
            with self._state_lock:
                if isinstance(stats, ServerStats):
                    self._state.server_stats = stats
                else:
                    logger.warning("Invalid stats object, using default ServerStats")
                    self._state.server_stats = ServerStats()
                # Don't notify for stats updates to avoid flooding
            return True
        except Exception as e:
            logger.error(f"Error in update_stats: {e}")
            return False
    
    def set_webui_status(self, online: bool) -> bool:
        """Set WebUI online status with validation"""
        try:
            with self._state_lock:
                # Ensure online is a boolean
                self._state.webui_online = bool(online)
                self._notify_watchers()
            return True
        except Exception as e:
            logger.error(f"Error in set_webui_status: {e}")
            return False
    
    def set_tui_status(self, online: bool) -> bool:
        """Set TUI online status with validation"""
        try:
            with self._state_lock:
                # Ensure online is a boolean
                self._state.tui_online = bool(online)
                self._notify_watchers()
            return True
        except Exception as e:
            logger.error(f"Error in set_tui_status: {e}")
            return False
    
    def register_callback(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """Register a state change callback with validation"""
        try:
            if callable(callback):
                with self._callbacks_lock:
                    self._callbacks.append(callback)
                return True
            else:
                logger.warning("Attempted to register non-callable as callback")
                return False
        except Exception as e:
            logger.error(f"Error in register_callback: {e}")
            return False
    
    def unregister_callback(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """Unregister a state change callback with validation"""
        try:
            if callable(callback):
                with self._callbacks_lock:
                    if callback in self._callbacks:
                        self._callbacks.remove(callback)
                        return True
                    else:
                        logger.warning("Callback not found in registry")
                        return False
            else:
                logger.warning("Attempted to unregister non-callable as callback")
                return False
        except Exception as e:
            logger.error(f"Error in unregister_callback: {e}")
            return False
    
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
    
    def clear_process(self) -> bool:
        """Clear process info when stopped with error handling"""
        try:
            with self._state_lock:
                self._state.is_running = False
                self._state.process_pid = None
                # Clear process object reference
                self._state.process_obj = None
                self._state.log_file = ""
                self._state.server_stats = ServerStats()
                self._notify_watchers()
            return True
        except Exception as e:
            logger.error(f"Error in clear_process: {e}")
            return False


def get_state_manager() -> StateManager:
    """Get the singleton StateManager instance"""
    return StateManager()


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


def load_config() -> Dict[str, Any]:
    """Load configuration from file"""
    config = {}
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
    return config

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file"""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving config: {e}")

def scan_models(models_path: str = None) -> List[Dict[str, Any]]:
    """Scan for GGUF model files with optimized performance"""
    if models_path is None:
        models_path = MODELS_PATH
    
    models = []
    try:
        os.makedirs(models_path, exist_ok=True)
        # Use os.scandir for better performance
        with os.scandir(models_path) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith(".gguf"):
                    stat_info = entry.stat()
                    # Show all models regardless of size for WebUI
                    models.append({
                        "name": entry.name,
                        "path": entry.path,
                        "size": stat_info.st_size,
                        "size_formatted": format_size(stat_info.st_size)
                    })
    except Exception as e:
        logger.error(f"Error scanning models: {e}")
    
    # Sort models by name for consistent ordering
    return sorted(models, key=lambda m: m["name"])