# Llama Launcher

<p align="center">
  <img src="https://img.shields.io/badge/Version-3.0-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Python-3.8+-orange?style=for-the-badge" alt="Python">
</p>

> A **cyberpunk-themed TUI launcher** for llama.cpp models with real-time metrics monitoring.

## ✨ Features

- 🎨 **Cyberpunk UI** - Neon color scheme with box-drawing characters
- 📊 **Real-time Metrics** - Live token speed and context usage monitoring
- ⚡ **Three Modes** - CLI interactive mode, Server API mode, Embedding mode
- 🔄 **Dynamic Scanning** - Auto-detect models in the models directory
- 🖥️ **Cross-platform** - Supports Linux, macOS, and Windows

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- llama.cpp installed at `/home/anan/llama.cpp`
- GGUF model files in the models directory (>1GB)

### Usage

```bash
python3 run.py
```

## 🎮 Controls

| Key | Action |
|-----|--------|
| `↑↓` / `W/S` / `4/5` | Navigate model list |
| `1` | CLI Mode |
| `2` | Server Mode |
| `3` | Embedding Mode |
| `C` | Cycle Context size (4k → 128k) |
| `G` | Cycle NGL value |
| `P` | Set port number |
| `R` | Refresh model list |
| `ENTER` | Launch selected model |
| `K` | Kill running model |
| `Q` | Quit |

## ⚙️ Configuration

### Paths

Edit the following in `run.py`:

```python
LLAMA_CPP_PATH = "/home/anan/llama.cpp"
MODELS_PATH = os.path.join(LLAMA_CPP_PATH, "models")
BUILD_BIN_PATH = os.path.join(LLAMA_CPP_PATH, "build", "bin")
```

### Context Size Options

```python
CTX_SIZE_OPTIONS = [4096, 8192, 16384, 32768, 65536, 131072]
# 4k, 8k, 16k, 32k, 64k, 128k
```

### NGL Options

```python
NGL_OPTIONS = [0, 33, 66, 99, 999]
```

## 📡 Server Mode

When running in Server mode:

- Binds to `0.0.0.0` (all network interfaces)
- Logs are written to `llama.cpp/logs/server_{port}.log`
- Real-time metrics parsed from server logs

### API Endpoints

```
http://localhost:8080/
http://localhost:8080/v1/models
http://localhost:8080/v1/completions
http://localhost:8080/embedding
```

## 📊 Metrics Display

| Metric | Description |
|--------|-------------|
| PROMPT TOK | Processed prompt tokens |
| EVAL TOK | Generated response tokens |
| PPD | Prompt tokens per second |
| EPD | Evaluation tokens per second |
| CONTEXT | Visual progress bar with percentage |

## 🛠️ Development

```bash
# Clone the repository
git clone https://github.com/aajj1314/llama-launcher.git

# Navigate to directory
cd llama-launcher

# Run
python3 run.py
```

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

## 🤝 Contributing

Pull requests are welcome! Feel free to open an issue for any suggestions or bugs.

---

<p align="center">
  Made with ❤️ for llama.cpp community
</p>
