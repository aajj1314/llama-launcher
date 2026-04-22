# Llama Launcher Code Wiki

## 项目概览

Llama Launcher 是一个基于 Python 的 cyberpunk 风格 TUI 启动器，用于管理和启动 llama.cpp 模型。它提供实时性能指标监控、多种运行模式、WebUI 支持和跨平台支持，为用户提供直观的模型管理体验。

### 主要功能

- 🎨 **Cyberpunk UI** - 霓虹色彩方案，使用框绘字符
- 📊 **实时指标** - 实时监控令牌速度和上下文使用情况
- ⚡ **三种模式** - CLI 交互模式、Server API 模式、Embedding 模式
- 🔄 **动态扫描** - 自动检测模型目录中的模型
- 🖥️ **跨平台** - 支持 Linux、macOS 和 Windows
- 🌐 **WebUI 支持** - 基于浏览器的远程管理界面
- 📁 **模块化架构** - 清晰、组织良好的代码结构
- 🔧 **配置管理** - 外部配置文件支持
- 🛡️ **增强错误处理** - 健壮的错误管理
- ✅ **参数持久化** - WebUI 参数修改后不再自动重置

## 项目架构

Llama Launcher 采用模块化设计，主要由以下几个核心组件组成：

```
├── launcher.py        # 统一启动脚本
├── run.py             # TUI 界面实现
├── state_manager.py   # 状态管理（单例模式）
├── web_app.py         # WebUI 实现（FastAPI）
├── config.py          # 配置管理
├── utils.py           # 工具函数
├── process_manager.py # 进程管理
└── templates/         # WebUI 模板
    └── index.html     # WebUI 主页面
```

### 核心模块关系

1. **配置管理模块** (`config.py`) - 管理应用配置，提供配置加载和保存功能
2. **状态管理模块** (`state_manager.py`) - 作为核心，管理应用状态，为 TUI 和 WebUI 提供共享状态
3. **进程管理模块** (`process_manager.py`) - 负责启动和管理不同模式的模型进程
4. **工具模块** (`utils.py`) - 提供通用工具函数，如日志解析和进程终止
5. **TUI 模块** (`run.py`) - 提供终端用户界面，用于模型选择和配置
6. **WebUI 模块** (`web_app.py`) - 提供基于 FastAPI 的 Web 界面和 RESTful API
7. **启动模块** (`launcher.py`) - 统一启动脚本，支持单独或同时启动 TUI 和 WebUI

## 主要模块职责

### 1. 配置管理模块 (`config.py`)

**职责**：
- 管理应用配置，包括路径、上下文大小、NGL 值等
- 提供配置加载和保存功能
- 支持环境变量配置覆盖

**核心功能**：
- 定义配置常量
- 提供配置获取和设置方法
- 支持从环境变量读取配置

### 2. 状态管理模块 (`state_manager.py`)

**职责**：
- 管理应用的全局状态，使用单例模式确保状态一致性
- 为 TUI 和 WebUI 提供共享状态
- 线程安全的状态访问和更新
- 模型扫描和管理

**核心功能**：
- 管理模型列表
- 管理运行模式和配置
- 管理进程状态
- 提供状态变更回调机制

### 3. 进程管理模块 (`process_manager.py`)

**职责**：
- 负责启动和管理不同模式的模型进程
- 处理进程启动参数和环境设置
- 提供进程终止功能

**核心功能**：
- `run_cli()` - 启动 CLI 模式进程
- `run_server()` - 启动 Server 模式进程
- `run_embedding()` - 启动 Embedding 模式进程
- 进程参数构建和验证

### 4. 工具模块 (`utils.py`)

**职责**：
- 提供通用工具函数
- 处理日志解析和进程管理

**核心功能**：
- `parse_server_log()` - 解析服务器日志，提取性能指标
- `terminate_process()` - 安全终止进程

### 5. TUI 模块 (`run.py`)

**职责**：
- 提供终端用户界面，展示模型列表和配置
- 处理用户输入，响应用户操作
- 启动和停止模型进程
- 显示实时性能指标

**核心功能**：
- 模型选择和导航
- 运行模式切换（CLI、Server、Embedding）
- 上下文大小和 NGL 值配置
- 端口设置
- 实时指标显示

### 6. WebUI 模块 (`web_app.py`)

**职责**：
- 提供基于 FastAPI 的 Web 界面
- 提供 RESTful API 用于模型管理
- 实时监控模型性能
- 支持远程管理

**核心功能**：
- 模型列表获取和刷新
- 模型启动和停止
- 配置更新
- 实时性能指标监控
- Web 界面展示

### 7. 启动模块 (`launcher.py`)

**职责**：
- 统一启动脚本，支持不同启动模式
- 配置 WebUI 端口和主机
- 管理 TUI 和 WebUI 的启动顺序和方式

**核心功能**：
- 支持三种启动模式：TUI、WebUI、两者同时启动
- 配置 WebUI 端口和主机
- 后台线程启动 WebUI
- 主线程启动 TUI

## 关键类与函数

### 配置管理模块

#### 配置常量

**描述**：定义应用的配置常量，如路径、上下文大小选项、NGL 选项等。

**主要常量**：
- `LLAMA_CPP_PATH` - llama.cpp 安装路径
- `MODELS_PATH` - 模型目录路径
- `BUILD_BIN_PATH` - 构建二进制文件路径
- `LOG_DIR` - 日志目录路径
- `CTX_SIZE_OPTIONS` - 上下文大小选项
- `NGL_OPTIONS` - NGL 值选项

### 状态管理模块

#### `StateManager` 类

**描述**：单例模式的状态管理器，用于管理应用状态并确保线程安全。

**主要方法**：
- `get_state()` - 获取当前状态（字典形式）
- `set_models(models)` - 更新模型列表
- `set_config(ctx_idx, ngl_idx, port)` - 更新配置
- `set_run_mode(mode)` - 设置运行模式
- `set_process(is_running, pid, process_obj, model_name, model_path, mode, log_file)` - 更新进程状态
- `update_stats(stats)` - 更新服务器统计信息
- `clear_process()` - 清除进程信息

#### `ServerStats` 类

**描述**：服务器性能指标数据类。

**属性**：
- `prompt_tokens` - 处理的提示令牌数
- `eval_tokens` - 生成的响应令牌数
- `prompt_per_second` - 提示令牌处理速度
- `eval_per_second` - 评估令牌生成速度
- `ctx_used` - 使用的上下文大小
- `ctx_total` - 总上下文大小
- `total_time` - 总处理时间

**方法**：
- `is_valid()` - 检查统计信息是否有效
- `to_dict()` - 将统计信息转换为字典

#### `scan_models()` 函数

**描述**：扫描模型目录中的 GGUF 模型文件。

**参数**：
- `models_path` - 模型目录路径（可选）

**返回值**：模型信息列表，每个模型包含名称、路径、大小等信息。

### 进程管理模块

#### `run_cli()` 函数

**描述**：启动 CLI 模式的模型进程。

**参数**：
- `model_path` - 模型路径
- `ctx_size` - 上下文大小
- `ngl` - NGL 值

**返回值**：启动的进程对象。

#### `run_server()` 函数

**描述**：启动 Server 模式的模型进程。

**参数**：
- `model_path` - 模型路径
- `ctx_size` - 上下文大小
- `ngl` - NGL 值
- `port` - 服务器端口

**返回值**：启动的进程对象和日志文件路径。

#### `run_embedding()` 函数

**描述**：启动 Embedding 模式的模型进程。

**参数**：
- `model_path` - 模型路径
- `ctx_size` - 上下文大小
- `ngl` - NGL 值

**返回值**：启动的进程对象。

### 工具模块

#### `parse_server_log()` 函数

**描述**：解析服务器日志文件，提取性能指标。

**参数**：
- `log_file` - 日志文件路径

**返回值**：`ServerStats` 对象，包含解析的性能指标。

#### `terminate_process()` 函数

**描述**：安全终止进程。

**参数**：
- `process` - 进程对象
- `timeout` - 超时时间（默认：5秒）

**返回值**：布尔值，表示进程是否成功终止。

### TUI 模块

#### `main()` 函数

**描述**：TUI 主循环，处理用户输入和界面更新。

**功能**：
- 初始化状态
- 显示界面
- 处理用户输入
- 启动和停止模型进程
- 更新实时指标

### WebUI 模块

#### `app` 对象

**描述**：FastAPI 应用实例，提供 Web 界面和 RESTful API。

**路由**：
- `GET /` - 主页面
- `GET /api/state` - 获取当前应用状态
- `GET /api/models` - 获取模型列表
- `POST /api/config` - 更新配置
- `POST /api/start` - 启动模型
- `POST /api/stop` - 停止模型
- `GET /api/options` - 获取可用选项

#### `start_web_server()` 函数

**描述**：启动 Web 服务器。

**参数**：
- `host` - 服务器主机（默认：0.0.0.0）
- `port` - 服务器端口（默认：8087）

### 启动模块

#### `main()` 函数

**描述**：启动脚本的主函数，解析命令行参数并启动相应的界面。

**参数**：
- `--mode` - 启动模式：tui、web、both（默认）
- `--web-port` - Web 服务器端口（默认：8087）
- `--web-host` - Web 服务器主机（默认：0.0.0.0）

## 依赖关系

### 核心依赖

| 依赖项 | 版本/要求 | 用途 | 来源 |
|--------|-----------|------|------|
| Python | 3.8+ | 运行环境 | [run.py](file:///workspace/run.py) |
| llama.cpp | 安装于 `/home/anan/llama.cpp` | 底层模型运行库 | [config.py](file:///workspace/config.py) |
| FastAPI | - | Web 框架 | [web_app.py](file:///workspace/web_app.py) |
| uvicorn | - | ASGI 服务器 | [web_app.py](file:///workspace/web_app.py) |
| requests | - | HTTP 客户端 | [web_app.py](file:///workspace/web_app.py) |

### 标准库依赖

| 模块 | 用途 | 来源 |
|------|------|------|
| os | 文件系统操作 | [run.py](file:///workspace/run.py), [state_manager.py](file:///workspace/state_manager.py), [web_app.py](file:///workspace/web_app.py), [config.py](file:///workspace/config.py) |
| sys | 系统操作 | [run.py](file:///workspace/run.py), [launcher.py](file:///workspace/launcher.py) |
| subprocess | 启动子进程 | [run.py](file:///workspace/run.py), [web_app.py](file:///workspace/web_app.py), [process_manager.py](file:///workspace/process_manager.py) |
| threading | 线程管理 | [run.py](file:///workspace/run.py), [state_manager.py](file:///workspace/state_manager.py), [web_app.py](file:///workspace/web_app.py), [launcher.py](file:///workspace/launcher.py) |
| time | 时间操作 | [run.py](file:///workspace/run.py), [state_manager.py](file:///workspace/state_manager.py), [web_app.py](file:///workspace/web_app.py), [launcher.py](file:///workspace/launcher.py) |
| re | 正则表达式 | [run.py](file:///workspace/run.py), [web_app.py](file:///workspace/web_app.py), [utils.py](file:///workspace/utils.py) |
| dataclasses | 数据类 | [run.py](file:///workspace/run.py), [state_manager.py](file:///workspace/state_manager.py), [web_app.py](file:///workspace/web_app.py) |
| argparse | 命令行参数解析 | [launcher.py](file:///workspace/launcher.py) |
| logging | 日志记录 | [state_manager.py](file:///workspace/state_manager.py) |

## 项目运行方式

### 基本运行

1. **直接运行 TUI**：
   ```bash
   python run.py
   ```

2. **使用启动脚本**：
   ```bash
   # 启动 TUI
   python launcher.py --mode tui
   
   # 启动 WebUI
   python launcher.py --mode web --web-port 8080
   
   # 同时启动 TUI 和 WebUI
   python launcher.py --mode both --web-port 8080
   ```

### 配置选项

1. **路径配置**：
   在 `config.py` 中修改：
   ```python
   LLAMA_CPP_PATH = os.environ.get("LLAMA_CPP_PATH", "/home/anan/llama.cpp")
   MODELS_PATH = os.path.join(LLAMA_CPP_PATH, "models")
   BUILD_BIN_PATH = os.path.join(LLAMA_CPP_PATH, "build", "bin")
   LOG_DIR = os.path.join(LLAMA_CPP_PATH, "logs")
   ```

2. **上下文大小选项**：
   ```python
   CTX_SIZE_OPTIONS = [4096, 8192, 16384, 32768, 65536, 131072]
   # 4k, 8k, 16k, 32k, 64k, 128k
   ```

3. **NGL 选项**：
   ```python
   NGL_OPTIONS = [0, 33, 66, 99, 999]
   ```

### 使用流程

1. **启动应用**：运行 `python run.py` 或 `python launcher.py`
2. **选择模型**：使用上下箭头、W/S 或 4/5 键导航模型列表
3. **选择运行模式**：按 1（CLI）、2（Server）或 3（Embedding）键
4. **配置参数**：
   - 按 C 键循环切换上下文大小
   - 按 G 键循环切换 NGL 值
   - 按 P 键设置服务器端口
5. **启动模型**：按 Enter 键启动选定的模型
6. **监控指标**：在 Server 模式下，实时显示性能指标
7. **停止模型**：按 K 键停止运行中的模型
8. **退出应用**：按 Q 键退出

## WebUI API 文档

### 主要 API 端点

| 方法 | 端点 | 功能 | 响应 |
|------|------|------|------|
| GET | / | 主页面 | HTML 页面 |
| GET | /api/state | 获取当前应用状态 | JSON 状态对象 |
| GET | /api/models | 获取模型列表 | JSON 模型列表 |
| POST | /api/config | 更新配置 | JSON 成功状态和新状态 |
| POST | /api/start | 启动模型 | JSON 成功状态和进程信息 |
| POST | /api/stop | 停止模型 | JSON 成功状态和消息 |
| GET | /api/options | 获取可用选项 | JSON 选项列表 |

### API 请求示例

1. **启动模型**：
   ```bash
   curl -X POST http://localhost:8087/api/start \
     -H "Content-Type: application/json" \
     -d '{"model_name": "model.gguf", "mode": 1}'
   ```

2. **更新配置**：
   ```bash
   curl -X POST http://localhost:8087/api/config \
     -H "Content-Type: application/json" \
     -d '{"ctx_idx": 2, "ngl_idx": 1, "port": 8080}'
   ```

## 性能指标说明

| 指标 | 描述 | 单位 |
|------|------|------|
| PROMPT TOK | 处理的提示令牌数 | 数量 |
| EVAL TOK | 生成的响应令牌数 | 数量 |
| PPD | 提示令牌处理速度 | 令牌/秒 |
| EPD | 评估令牌生成速度 | 令牌/秒 |
| CONTEXT | 上下文使用情况 | 百分比 |

## 故障排除

### 常见问题

1. **模型未找到**：
   - 确保模型文件位于 `LLAMA_CPP_PATH/models` 目录中
   - 确保模型文件扩展名为 `.gguf`
   - 按 R 键刷新模型列表

2. **服务器无法启动**：
   - 检查端口是否被占用
   - 确保 llama.cpp 已正确安装
   - 检查日志文件（位于 `LLAMA_CPP_PATH/logs` 目录）

3. **性能指标不显示**：
   - 确保模型正在服务器模式下运行
   - 检查日志文件是否存在并可访问
   - 等待几秒钟让指标更新

4. **WebUI 无法访问**：
   - 检查 WebUI 端口是否正确（默认：8087）
   - 确保启动脚本使用了正确的模式（--mode web 或 --mode both）
   - 检查防火墙设置

### 日志位置

- 服务器日志：`LLAMA_CPP_PATH/logs/server_{port}.log`
- 应用日志：标准输出和错误输出

## 开发指南

### 项目结构

- **核心模块**：
  - `config.py` - 配置管理
  - `state_manager.py` - 状态管理
  - `process_manager.py` - 进程管理
  - `utils.py` - 工具函数
  - `run.py` - TUI 实现
  - `web_app.py` - WebUI 实现
  - `launcher.py` - 启动脚本

- **资源文件**：
  - `templates/index.html` - WebUI 主页面

### 扩展功能

1. **添加新的运行模式**：
   - 在 `process_manager.py` 中添加新的启动函数
   - 在 `state_manager.py` 中更新模式定义
   - 在 `run.py` 和 `web_app.py` 中添加相应的处理逻辑

2. **添加新的配置选项**：
   - 在 `config.py` 中添加新的选项常量
   - 在 `state_manager.py` 中更新配置管理
   - 在 `run.py` 和 `web_app.py` 中添加相应的处理逻辑

3. **改进 UI**：
   - 调整 `run.py` 中的 TUI 显示逻辑
   - 修改 `templates/index.html` 中的 WebUI 样式

### 测试

1. **功能测试**：
   - 测试模型扫描功能
   - 测试不同运行模式的启动和停止
   - 测试配置更新功能
   - 测试性能指标监控

2. **集成测试**：
   - 测试 TUI 和 WebUI 之间的状态同步
   - 测试多线程环境下的状态一致性

## 总结

Llama Launcher 是一个功能强大、界面美观的 llama.cpp 模型管理工具，通过 TUI 和 WebUI 两种方式提供模型管理和监控功能。它采用模块化设计，使用单例模式管理应用状态，确保 TUI 和 WebUI 之间的状态一致性。

该项目的核心价值在于：
- 提供直观的用户界面，简化模型管理流程
- 实时监控模型性能，帮助用户了解模型运行状态
- 支持多种运行模式，满足不同场景的需求
- 跨平台支持，适用于不同的操作系统环境
- WebUI 支持，实现远程管理能力
- 模块化架构，提高代码可维护性

Llama Launcher 为 llama.cpp 社区提供了一个便捷、高效的模型管理工具，使模型的部署和监控变得更加简单和直观。