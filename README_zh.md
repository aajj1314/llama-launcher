# Llama Launcher

<p align="center">
  <img src="https://img.shields.io/badge/版本-3.1-blue?style=for-the-badge" alt="版本">
  <img src="https://img.shields.io/badge/许可证-MIT-green?style=for-the-badge" alt="许可证">
  <img src="https://img.shields.io/badge/Python-3.8+-orange?style=for-the-badge" alt="Python">
</p>

> 一个**赛博朋克风格 TUI 启动器**，用于管理 llama.cpp 模型，支持实时指标监控和 WebUI 界面。

## ✨ 功能特性

- 🎨 **赛博朋克界面** - 霓虹配色方案 + 字符绘制边框
- 📊 **实时监控** - 实时显示 Token 速度和上下文使用情况
- ⚡ **三种模式** - CLI 交互模式、Server API 模式、Embedding 模式
- 🔄 **动态扫描** - 自动检测 models 目录下的模型
- 🖥️ **跨平台** - 支持 Linux、macOS 和 Windows
- 🌐 **WebUI 支持** - 基于浏览器的远程管理界面
- 📁 **模块化架构** - 清晰、组织良好的代码结构
- 🔧 **配置管理** - 外部配置文件支持
- 🛡️ **增强错误处理** - 健壮的错误管理

## 🚀 快速开始

### 环境要求

- Python 3.8+
- llama.cpp 安装在 `/home/anan/llama.cpp`
- models 目录下有 GGUF 模型文件（>1GB）
- 额外的 Python 依赖：
  ```bash
  pip install fastapi uvicorn requests
  ```

### 运行方法

```bash
# 同时运行 TUI 和 WebUI
python3 launcher.py

# 仅运行 TUI
python3 run.py

# 仅运行 WebUI
python3 launcher.py --mode web --web-port 8087
```

## 🎮 操作指南

| 按键 | 功能 |
|------|------|
| `↑↓` / `W/S` / `4/5` | 上下选择模型 |
| `1` | CLI 交互模式 |
| `2` | Server API 模式 |
| `3` | Embedding 模式 |
| `C` | 循环切换 Context 大小 (4k → 128k) |
| `G` | 循环切换 NGL 值 |
| `P` | 设置端口号 |
| `R` | 刷新模型列表 |
| `ENTER` | 启动选中的模型 |
| `K` | 停止当前运行的模型 |
| `Q` | 退出程序 |

## ⚙️ 配置选项

### 路径配置

在 `config.py` 中修改以下路径：

```python
LLAMA_CPP_PATH = os.environ.get("LLAMA_CPP_PATH", "/home/anan/llama.cpp")
MODELS_PATH = os.path.join(LLAMA_CPP_PATH, "models")
BUILD_BIN_PATH = os.path.join(LLAMA_CPP_PATH, "build", "bin")
LOG_DIR = os.path.join(LLAMA_CPP_PATH, "logs")
```

### Context 大小选项

```python
CTX_SIZE_OPTIONS = [4096, 8192, 16384, 32768, 65536, 131072]
# 对应: 4k, 8k, 16k, 32k, 64k, 128k
```

### NGL 选项

```python
NGL_OPTIONS = [0, 33, 66, 99, 999]
```

## 📡 Server 模式

当运行在 Server 模式时：

- 监听 `0.0.0.0`（所有网络接口）
- 日志写入 `llama.cpp/logs/server_{端口号}.log`
- 实时从服务器日志解析指标数据

### API 端点

```
http://localhost:8080/
http://localhost:8080/v1/models
http://localhost:8080/v1/completions
http://localhost:8080/embedding
```

## 🌐 WebUI

WebUI 提供基于浏览器的界面，用于管理 llama.cpp 模型：

- **访问地址**：`http://localhost:8087`
- **功能**：
  - 模型列表和选择
  - 模型启动/停止控制
  - 实时指标监控
  - 配置管理
  - 响应式设计，支持不同设备

## 📊 指标说明

| 指标 | 说明 |
|------|------|
| PROMPT TOK | 已处理的提示词 Token 数量 |
| EVAL TOK | 已生成的回复 Token 数量 |
| PPD | 每秒处理的提示词 Token 数 |
| EPD | 每秒生成的 Token 数 |
| CONTEXT | 可视化进度条 + 百分比 |

## 🖥️ 界面预览

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ◈◈◈ LLAMA.CPP MODEL LAUNCHER v3.1 ◈◈◈  ║
║  Cyberpunk Edition                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ▸ AVAILABLE MODELS (2 found)

  ►  1. gemma-4-E4B-it-Q4_K_M.gguf                      4.64 GB
     2. gemma-4-E4B-it-Q5_K_M.gguf                    5.11 GB

  ▸ CONFIGURATION

  ┌──────────────────────────────────────────────────────────────┐
  │  MODE:    CLI           CONTEXT:     4k  NGL:     999  PORT:   8080  │
  └──────────────────────────────────────────────────────────────┘

  ▸ SERVER METRICS

  ┌──────────────────────────────────────────────────────────────┐
  │  ● RUNNING  PID: 12345  Port: 8080                         │
  │                                                              │
  │  ┌───────────┬───────────┬───────────┬───────────┐        │
  │  │ PROMPT TOK│  EVAL TOK │    PPD    │    EPD    │        │
  │  │     128   │    1024   │   42.5    │   28.3    │        │
  │  └───────────┴───────────┴───────────┴───────────┘        │
  │                                                              │
  │  CONTEXT: ████████████████░░░░░░░ 62.5% (5120/8192)       │
  └──────────────────────────────────────────────────────────────┘
```

## 🛠️ 开发

```bash
# 克隆仓库
git clone https://github.com/aajj1314/llama-launcher.git

# 进入目录
cd llama-launcher

# 安装依赖
pip install fastapi uvicorn requests

# 运行
python3 launcher.py
```

## 📁 项目结构

```
├── launcher.py        # 统一启动脚本
├── run.py             # TUI 界面实现
├── state_manager.py   # 状态管理（单例模式）
├── web_app.py         # WebUI 实现（FastAPI）
├── config.py          # 配置管理
├── utils.py           # 工具函数
├── process_manager.py # 进程管理
├── templates/         # WebUI 模板
│   └── index.html     # WebUI 主页面
├── README.md          # 英文文档
└── README_zh.md       # 中文文档
```

## 📝 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE)。

## 🤝 贡献

欢迎提交 Pull Request！如有建议或问题，请随时提交 Issue。

---

<p align="center">
  为 llama.cpp 社区 ❤️ 而生
</p>
