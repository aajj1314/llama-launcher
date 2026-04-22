#!/usr/bin/env python3
"""
状态管理模块
负责管理应用的所有状态信息
"""

import os
import time
import subprocess
import threading
import logging
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from config import RunMode, get_config, get_config_manager
from models import ModelManager, ModelInfo


class ProcessStatus(Enum):
    """进程状态"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ProcessInfo:
    """进程信息"""
    status: ProcessStatus = ProcessStatus.STOPPED
    process: Optional[subprocess.Popen] = None
    pid: Optional[int] = None
    start_time: Optional[float] = None
    mode: Optional[RunMode] = None
    model_name: Optional[str] = None
    log_file: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class AppState:
    """应用状态"""
    # 模型信息
    models: List[ModelInfo] = field(default_factory=list)
    selected_model: Optional[str] = None
    # 进程信息
    process_info: ProcessInfo = field(default_factory=ProcessInfo)
    # 回调列表
    callbacks: List[Callable[[], None]] = field(default_factory=list)


class StateManager:
    """状态管理器"""

    def __init__(self):
        self._state = AppState()
        self._lock = threading.RLock()
        self._config = get_config()
        self._model_manager = ModelManager()
        self._setup_logging()
        self._init_models_path()

    def _setup_logging(self) -> None:
        """设置日志"""
        self._logger = logging.getLogger(__name__)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)

    def _init_models_path(self) -> None:
        """初始化模型路径"""
        models_path = os.path.join(self._config.llama_cpp_path, "models")
        self._model_manager.models_path = models_path
        self.scan_models()

    def register_callback(self, callback: Callable[[], None]) -> None:
        """注册状态变更回调"""
        with self._lock:
            if callback not in self._state.callbacks:
                self._state.callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[], None]) -> None:
        """取消注册回调"""
        with self._lock:
            if callback in self._state.callbacks:
                self._state.callbacks.remove(callback)

    def _notify_callbacks(self) -> None:
        """通知所有回调"""
        callbacks = list(self._state.callbacks)
        for callback in callbacks:
            try:
                callback()
            except Exception as e:
                self._logger.error(f"回调执行失败: {e}")

    # 模型管理方法

    def scan_models(self) -> List[ModelInfo]:
        """扫描模型"""
        with self._lock:
            self._state.models = self._model_manager.scan()
            # 如果没有选择模型，选择第一个
            if self._state.selected_model is None and self._state.models:
                self._state.selected_model = self._state.models[0].name
            # 如果选择的模型不存在，清除选择
            elif self._state.selected_model:
                model_exists = any(
                    m.name == self._state.selected_model
                    for m in self._state.models
                )
                if not model_exists:
                    self._state.selected_model = None
                    if self._state.models:
                        self._state.selected_model = self._state.models[0].name
        self._notify_callbacks()
        return self._state.models

    def get_models(self) -> List[ModelInfo]:
        """获取模型列表"""
        with self._lock:
            return list(self._state.models)

    def get_selected_model(self) -> Optional[str]:
        """获取选中的模型"""
        with self._lock:
            return self._state.selected_model

    def set_selected_model(self, model_name: Optional[str]) -> None:
        """设置选中的模型"""
        with self._lock:
            self._state.selected_model = model_name
        self._notify_callbacks()

    # 路径管理方法

    def set_llama_cpp_path(self, path: str) -> bool:
        """设置 llama.cpp 路径"""
        if not os.path.exists(path) or not os.path.isdir(path):
            with self._lock:
                self._state.process_info.status = ProcessStatus.ERROR
                self._state.process_info.error_message = f"路径不存在: {path}"
            self._notify_callbacks()
            return False

        # 更新配置
        config_manager = get_config_manager()
        config_manager.update(llama_cpp_path=path)
        self._config = config_manager.get()

        # 更新模型路径并重新扫描
        models_path = os.path.join(path, "models")
        self._model_manager.models_path = models_path
        self.scan_models()
        return True

    # 进程管理方法

    def get_process_info(self) -> ProcessInfo:
        """获取进程信息"""
        with self._lock:
            # 检查进程是否还在运行
            if self._state.process_info.process is not None:
                if self._state.process_info.process.poll() is not None:
                    # 进程已经停止
                    self._state.process_info.status = ProcessStatus.STOPPED
                    self._state.process_info.process = None
                    self._state.process_info.pid = None
                    self._state.process_info.start_time = None
            return self._state.process_info

    def is_process_running(self) -> bool:
        """检查进程是否正在运行"""
        info = self.get_process_info()
        return info.status == ProcessStatus.RUNNING

    def _get_binary_path(self, mode: RunMode) -> Optional[str]:
        """获取二进制文件路径"""
        binaries = {
            RunMode.CLI: "llama-cli",
            RunMode.SERVER: "llama-server",
            RunMode.EMBEDDING: "llama-embedding",
        }
        binary_name = binaries.get(mode)
        if not binary_name:
            return None

        build_bin = os.path.join(self._config.llama_cpp_path, "build", "bin")
        binary_path = os.path.join(build_bin, binary_name)
        if os.path.exists(binary_path):
            return binary_path

        # 尝试查找其他可能的位置
        paths_to_check = [
            os.path.join(self._config.llama_cpp_path, binary_name),
            binary_name,  # 检查 PATH
        ]
        for path in paths_to_check:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
            # 在 PATH 中查找
            if not os.path.isabs(path):
                for dir_path in os.environ.get("PATH", "").split(os.pathsep):
                    full_path = os.path.join(dir_path, path)
                    if os.path.exists(full_path) and os.access(full_path, os.X_OK):
                        return full_path
        return None

    def start_process(self, mode: RunMode, model_name: str) -> bool:
        """启动模型进程"""
        # 检查是否已经在运行
        with self._lock:
            if self._state.process_info.status in [ProcessStatus.RUNNING, ProcessStatus.STARTING]:
                return False

        # 获取模型信息
        model = self._model_manager.get_model_by_name(model_name)
        if not model:
            with self._lock:
                self._state.process_info.status = ProcessStatus.ERROR
                self._state.process_info.error_message = f"模型不存在: {model_name}"
            self._notify_callbacks()
            return False

        # 查找二进制文件
        binary_path = self._get_binary_path(mode)
        if not binary_path:
            with self._lock:
                self._state.process_info.status = ProcessStatus.ERROR
                self._state.process_info.error_message = f"找不到二进制文件 (mode: {mode.value})"
            self._notify_callbacks()
            return False

        # 创建日志目录
        log_dir = os.path.join(self._config.llama_cpp_path, "logs")
        os.makedirs(log_dir, exist_ok=True)
        timestamp = int(time.time())
        log_file = os.path.join(log_dir, f"{mode.value}_{timestamp}.log")

        # 构建命令
        args = [binary_path, "-m", model.path]
        args.extend(["-ngl", str(self._config.ngl)])
        args.extend(["-c", str(self._config.context_size)])

        if mode == RunMode.SERVER:
            args.extend(["--port", str(self._config.port), "--host", "0.0.0.0"])

        # 更新状态
        with self._lock:
            self._state.process_info.status = ProcessStatus.STARTING
            self._state.process_info.mode = mode
            self._state.process_info.model_name = model_name
            self._state.process_info.log_file = log_file
            self._state.process_info.error_message = None
        self._notify_callbacks()

        # 启动进程
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                process = subprocess.Popen(
                    args,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    preexec_fn=os.setsid  # 让进程独立运行
                )

            with self._lock:
                self._state.process_info.status = ProcessStatus.RUNNING
                self._state.process_info.process = process
                self._state.process_info.pid = process.pid
                self._state.process_info.start_time = time.time()

            # 保存选中的模型到配置
            config_manager = get_config_manager()
            config_manager.update(selected_model=model_name, run_mode=mode)
            self._config = config_manager.get()

            self._notify_callbacks()
            return True

        except Exception as e:
            self._logger.error(f"启动进程失败: {e}")
            with self._lock:
                self._state.process_info.status = ProcessStatus.ERROR
                self._state.process_info.error_message = f"启动失败: {str(e)}"
            self._notify_callbacks()
            return False

    def stop_process(self) -> bool:
        """停止模型进程"""
        with self._lock:
            if self._state.process_info.status not in [ProcessStatus.RUNNING, ProcessStatus.STARTING]:
                return True

            process = self._state.process_info.process
            if process is None:
                self._state.process_info.status = ProcessStatus.STOPPED
                self._state.process_info.pid = None
                self._state.process_info.start_time = None
                self._notify_callbacks()
                return True

            self._state.process_info.status = ProcessStatus.STOPPING
        self._notify_callbacks()

        try:
            # 尝试正常停止
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # 超时强制杀死
                    process.kill()
                    process.wait(timeout=2)

            with self._lock:
                self._state.process_info.status = ProcessStatus.STOPPED
                self._state.process_info.process = None
                self._state.process_info.pid = None
                self._state.process_info.start_time = None
            self._notify_callbacks()
            return True

        except Exception as e:
            self._logger.error(f"停止进程失败: {e}")
            with self._lock:
                self._state.process_info.status = ProcessStatus.ERROR
                self._state.process_info.error_message = f"停止失败: {str(e)}"
            self._notify_callbacks()
            return False

    def restart_process(self) -> bool:
        """重启进程"""
        with self._lock:
            mode = self._state.process_info.mode
            model_name = self._state.process_info.model_name

        if mode is None or model_name is None:
            return False

        self.stop_process()
        # 等待完全停止
        time.sleep(0.5)
        return self.start_process(mode, model_name)

    def get_log_content(self, max_lines: int = 100) -> List[str]:
        """获取日志内容"""
        with self._lock:
            log_file = self._state.process_info.log_file

        if not log_file or not os.path.exists(log_file):
            return []

        try:
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                return lines[-max_lines:]
        except Exception as e:
            self._logger.error(f"读取日志失败: {e}")
            return [f"读取日志失败: {str(e)}"]

    # 状态获取方法

    def get_state_dict(self) -> Dict[str, Any]:
        """获取完整的状态字典"""
        with self._lock:
            info = self.get_process_info()
            return {
                "models": [m.to_dict() for m in self._state.models],
                "selected_model": self._state.selected_model,
                "process": {
                    "status": info.status.value if info.status else "stopped",
                    "mode": info.mode.value if info.mode else None,
                    "model_name": info.model_name,
                    "pid": info.pid,
                    "start_time": info.start_time,
                    "log_file": info.log_file,
                    "error_message": info.error_message,
                },
                "config": self._config.to_dict(),
            }


# 全局状态管理器实例
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """获取状态管理器单例"""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager
