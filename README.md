# Llama Launcher

<p align="center">
  <img src="https://img.shields.io/badge/Version-3.2-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Python-3.8+-orange?style=for-the-badge" alt="Python">
</p>

> A **cyberpunk-themed TUI launcher** for llama.cpp models with real-time metrics monitoring and WebUI support. Now supports custom llama.cpp path configuration!

## ✨ Features

- 🎨 **Cyberpunk UI** - Neon color scheme with box-drawing characters
- 📊 **Real-time Metrics** - Live token speed and context usage monitoring
- ⚡ **Three Modes** - CLI interactive mode, Server API mode, Embedding mode
- 🔄 **Dynamic Scanning** - Auto-detect models in the models directory
- 🖥️ **Cross-platform** - Supports Linux, macOS, and Windows
- 🌐 **WebUI Support** - Browser-based interface for remote management
- 📁 **Modular Architecture** - Clean, organized code structure
- 🔧 **Configurable llama.cpp Path** - Set custom llama.cpp installation path (TUI + WebUI)
- 🛡️ **Enhanced Error Handling** - Robust error management
- ✅ **Parameter Persistence** - WebUI parameters no longer auto-reset when modified

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- llama.cpp installation (can be at any path)
- GGUF model files in the models directory
- Additional Python dependencies:
  ```bash
  pip install fastapi uvicorn requests
  ```

### Usage

```bash
# Run TUI and WebUI together
python launcher.py

# Run only TUI
python run.py

# Run only WebUI
python launcher.py --mode web --web-port 8087
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
| `L` | Configure llama.cpp path |
| `R` | Refresh model list |
| `ENTER` | Launch selected model |
| `K` | Kill running model |
| `Q` | Quit |

## 🔧 Configuration

### Path Configuration

You can configure the llama.cpp path through:

1. **TUI** - Press `L` in the TUI interface
2. **WebUI** - Use the path configuration section in the web interface
3. **Environment Variable** - Set `LLAMA_CPP_PATH` before running
4. **Config File** - Saved configuration will be loaded automatically

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

The web server provides these REST API endpoints:

- `GET /` - Main UI
- `GET /api/state` - Get current application state
- `GET /api/models` - Get model list
- `GET /api/path` - Get current llama.cpp path
- `POST /api/config` - Update configuration
- `POST /api/path` - Update llama.cpp path
- `POST /api/start` - Start a model
- `POST /api/stop` - Stop running model
- `GET /api/options` - Get available options

## 🌐 WebUI

The WebUI provides a browser-based interface for managing llama.cpp models:

- **Access URL**: `http://localhost:8087`
- **Features**:
  - Model list and selection
  - Model start/stop control
  - Real-time metrics monitoring
  - Configuration management
  - Llama.cpp path configuration
  - Responsive design for different devices

## 📊 Metrics Display

| Metric | Description |
|--------|-------------|
| PROMPT TOK | Processed prompt tokens |
| EVAL TOK | Generated response tokens |
| PPD | Prompt tokens per second |
| EPD | Evaluation tokens per second |
| CONTEXT | Visual progress bar with percentage |

## 📁 Project Structure

```
llama-launcher/
├── launcher.py           # Unified startup script
├── run.py                # TUI interface implementation
├── state_manager.py      # State manager (singleton pattern)
├── web_app.py            # WebUI implementation (FastAPI)
├── process_manager.py    # Process management
├── utils.py              # Utility functions
├── config.py             # Configuration management
├── templates/
│   └── index.html        # WebUI main page
├── docs/
│   └── superpowers/
│       └── plans/        # Implementation plans and history
├── README.md             # This file
└── README_zh.md          # 中文文档
```

## 🛠️ Development

```bash
# Clone the repository
git clone https://github.com/aajj1314/llama-launcher.git

# Navigate to directory
cd llama-launcher

# Install dependencies
pip install fastapi uvicorn requests

# Run
python launcher.py
```

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

## 🤝 Contributing

Pull requests are welcome! Feel free to open an issue for any suggestions or bugs.

## 📚 Documentation

- **README.md** - English documentation (this file)
- **README_zh.md** - Chinese documentation
- **CODE_WIKI.md** - Code reference and architecture documentation
- **docs/superpowers/plans/** - Implementation history and planning documents

---

<p align="center">
  Made with ❤️ for llama.cpp community
</p>
