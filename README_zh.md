# Llama Launcher

<p align="center">
  <img src="https://img.shields.io/badge/版本-3.0-blue?style=for-the-badge" alt="版本">
  <img src="https://img.shields.io/badge/许可证-MIT-green?style=for-the-badge" alt="许可证">
  <img src="https://img.shields.io/badge/Python-3.8+-orange?style=for-the-badge" alt="Python">
</p>

> 一个**赛博朋克风格 TUI 启动器**，用于管理 llama.cpp 模型，支持实时指标监控。

## ✨ 功能特性

- 🎨 **赛博朋克界面** - 霓虹配色方案 + 字符绘制边框
- 📊 **实时监控** - 实时显示 Token 速度和上下文使用情况
- ⚡ **三种模式** - CLI 交互模式、Server API 模式、Embedding 模式
- 🔄 **动态扫描** - 自动检测 models 目录下的模型
- 🖥️ **跨平台** - 支持 Linux、macOS 和 Windows

## 🚀 快速开始

### 环境要求

- Python 3.8+
- llama.cpp 安装在 `/home/anan/llama.cpp`
- models 目录下有 GGUF 模型文件（>1GB）

### 运行方法

```bash
python3 run.py
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

在 `run.py` 中修改以下路径：

```python
LLAMA_CPP_PATH = "/home/anan/llama.cpp"
MODELS_PATH = os.path.join(LLAMA_CPP_PATH, "models")
BUILD_BIN_PATH = os.path.join(LLAMA_CPP_PATH, "build", "bin")
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
║  ◈◈◈ LLAMA.CPP MODEL LAUNCHER v3.0 ◈◈◈  ║
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

# 运行
python3 run.py
```

## 📝 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE)。

## 🤝 贡献

欢迎提交 Pull Request！如有建议或问题，请随时提交 Issue。

---

<p align="center">
  为 llama.cpp 社区 ❤️ 而生
</p>
