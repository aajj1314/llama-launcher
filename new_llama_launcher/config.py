#!/usr/bin/env python3
"""
配置管理模块
负责项目的所有配置项定义和管理
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class RunMode(Enum):
    """运行模式枚举"""
    CLI = "cli"
    SERVER = "server"
    EMBEDDING = "embedding"


@dataclass
class AppConfig:
    """应用配置类"""
    # 路径配置
    llama_cpp_path: str
    # 运行配置
    run_mode: RunMode
    selected_model: Optional[str]
    context_size: int
    ngl: int
    port: int
    timeout: int
    log_level: str
    gpu_memory_limit: Optional[int]
    # Web服务配置
    web_host: str
    web_port: int

    @classmethod
    def default(cls) -> "AppConfig":
        """获取默认配置"""
        return cls(
            llama_cpp_path=cls._default_llama_cpp_path(),
            run_mode=RunMode.CLI,
            selected_model=None,
            context_size=4096,
            ngl=0,
            port=8000,
            timeout=30,
            log_level="info",
            gpu_memory_limit=None,
            web_host="0.0.0.0",
            web_port=8000
        )

    @staticmethod
    def _default_llama_cpp_path() -> str:
        """获取默认的 llama.cpp 路径"""
        home = os.path.expanduser("~")
        paths = [
            os.path.join(home, "llama.cpp"),
            "/opt/llama.cpp",
            os.getcwd(),
        ]
        for path in paths:
            if os.path.exists(path) and os.path.isdir(path):
                return path
        return home

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["run_mode"] = self.run_mode.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        """从字典创建配置"""
        if "run_mode" in data and isinstance(data["run_mode"], str):
            data["run_mode"] = RunMode(data["run_mode"])
        # 过滤掉不认识的字段
        valid_fields = {f.name for f in cls.__dataclass_fields__.keys()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".llama_launcher_v4")
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "config.json")
        self._config: Optional[AppConfig] = None
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """确保配置目录存在"""
        os.makedirs(self.config_dir, exist_ok=True)

    def load(self) -> AppConfig:
        """加载配置"""
        if self._config is not None:
            return self._config

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._config = AppConfig.from_dict(data)
            except Exception as e:
                print(f"警告：加载配置失败，使用默认配置 ({e})")
                self._config = AppConfig.default()
        else:
            self._config = AppConfig.default()

        return self._config

    def save(self, config: Optional[AppConfig] = None) -> None:
        """保存配置"""
        if config is not None:
            self._config = config
        if self._config is None:
            return

        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"错误：保存配置失败 ({e})")

    def get(self) -> AppConfig:
        """获取当前配置"""
        return self.load()

    def update(self, **kwargs) -> AppConfig:
        """更新配置的部分字段"""
        config = self.load()
        for key, value in kwargs.items():
            if hasattr(config, key):
                if key == "run_mode" and isinstance(value, str):
                    value = RunMode(value)
                setattr(config, key, value)
        self.save(config)
        return config


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取配置管理器单例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AppConfig:
    """获取当前配置"""
    return get_config_manager().get()
