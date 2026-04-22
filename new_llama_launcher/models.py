#!/usr/bin/env python3
"""
模型管理模块
负责模型扫描、加载和管理
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import glob


@dataclass
class ModelInfo:
    """模型信息"""
    name: str
    path: str
    size: int
    size_formatted: str

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "path": self.path,
            "size": self.size,
            "size_formatted": self.size_formatted
        }


def format_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


class ModelManager:
    """模型管理器"""

    def __init__(self, models_path: Optional[str] = None):
        self.models_path = models_path
        self._models: List[ModelInfo] = []

    def scan(self, models_path: Optional[str] = None) -> List[ModelInfo]:
        """扫描模型目录"""
        if models_path is not None:
            self.models_path = models_path

        if self.models_path is None:
            return []

        # 确保目录存在
        try:
            os.makedirs(self.models_path, exist_ok=True)
        except Exception as e:
            print(f"警告：无法创建模型目录 ({e})")
            return []

        self._models = []

        # 扫描 GGUF 模型
        pattern = os.path.join(self.models_path, "*.gguf")
        for file_path in glob.glob(pattern):
            if os.path.isfile(file_path):
                stat_info = os.stat(file_path)
                self._models.append(ModelInfo(
                    name=os.path.basename(file_path),
                    path=file_path,
                    size=stat_info.st_size,
                    size_formatted=format_size(stat_info.st_size)
                ))

        # 按名称排序
        self._models.sort(key=lambda m: m.name.lower())
        return self._models

    def get_models(self) -> List[ModelInfo]:
        """获取模型列表"""
        if not self._models:
            self.scan()
        return self._models

    def get_model_by_name(self, name: str) -> Optional[ModelInfo]:
        """根据名称获取模型"""
        for model in self._models:
            if model.name == name:
                return model
        return None

    def get_models_dict(self) -> List[Dict[str, Any]]:
        """获取模型字典列表"""
        return [model.to_dict() for model in self.get_models()]
