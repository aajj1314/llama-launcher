# llama.cpp 路径选择功能实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现让用户选择 llama.cpp 具体位置的功能，不再强制用户安装在指定位置。

**Architecture:** 通过动态路径配置实现，在配置模块中添加路径更新功能，在状态管理中处理路径变更，在 TUI 和 WebUI 中添加路径选择界面。

**Tech Stack:** Python, FastAPI, Vue.js, llama.cpp

---

## 文件结构

### 修改文件：
1. `config.py` - 添加动态路径配置功能
2. `state_manager.py` - 处理路径变更和模型刷新
3. `run.py` - 添加 TUI 路径选择界面
4. `web_app.py` - 添加 WebUI 路径配置端点
5. `templates/index.html` - 添加 WebUI 路径选择界面

### 测试文件：
1. `tests/test_config.py` - 测试路径配置功能
2. `tests/test_state_manager.py` - 测试路径变更处理

---

### Task 1: 更新 config.py 以支持动态路径配置

**Files:**
- Modify: `config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: 编写失败测试**

```python
def test_update_llama_cpp_path():
    from config import update_llama_cpp_path, get_current_paths
    
    # 初始路径
    initial_paths = get_current_paths()
    
    # 更新路径
    new_path = "/custom/path/to/llama.cpp"
    update_llama_cpp_path(new_path)
    
    # 验证路径已更新
    updated_paths = get_current_paths()
    assert updated_paths['llama_cpp_path'] == new_path
    
    # 恢复原始路径
    update_llama_cpp_path(initial_paths['llama_cpp_path'])
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_config.py::test_update_llama_cpp_path -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: 编写最小实现**

```python
# config.py

# 全局路径变量
LLAMA_CPP_PATH = "/default/path/to/llama.cpp"
MODEL_DIR = f"{LLAMA_CPP_PATH}/models"

# 更新 llama.cpp 路径
def update_llama_cpp_path(new_path):
    global LLAMA_CPP_PATH, MODEL_DIR
    LLAMA_CPP_PATH = new_path
    MODEL_DIR = f"{LLAMA_CPP_PATH}/models"

# 获取当前路径
def get_current_paths():
    return {
        'llama_cpp_path': LLAMA_CPP_PATH,
        'model_dir': MODEL_DIR
    }
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_config.py::test_update_llama_cpp_path -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add config.py tests/test_config.py
git commit -m "feat: add dynamic llama.cpp path configuration"
```

### Task 2: 更新 state_manager.py 以使用动态路径配置

**Files:**
- Modify: `state_manager.py`
- Test: `tests/test_state_manager.py`

- [ ] **Step 1: 编写失败测试**

```python
def test_set_llama_cpp_path():
    from state_manager import StateManager
    from config import get_current_paths
    
    manager = StateManager()
    initial_paths = get_current_paths()
    
    # 设置新路径
    new_path = "/custom/path/to/llama.cpp"
    manager.set_llama_cpp_path(new_path)
    
    # 验证路径已更新
    updated_paths = manager.get_paths()
    assert updated_paths['llama_cpp_path'] == new_path
    
    # 恢复原始路径
    manager.set_llama_cpp_path(initial_paths['llama_cpp_path'])
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_state_manager.py::test_set_llama_cpp_path -v`
Expected: FAIL with "method not defined"

- [ ] **Step 3: 编写最小实现**

```python
# state_manager.py

from config import update_llama_cpp_path, get_current_paths

class StateManager:
    # 现有代码...
    
    def set_llama_cpp_path(self, new_path):
        """设置 llama.cpp 路径并刷新模型"""
        update_llama_cpp_path(new_path)
        self.models = self._load_models()
        return get_current_paths()
    
    def get_paths(self):
        """获取当前路径配置"""
        return get_current_paths()
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_state_manager.py::test_set_llama_cpp_path -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add state_manager.py tests/test_state_manager.py
git commit -m "feat: add path management to state manager"
```

### Task 3: 添加 TUI 界面用于路径选择

**Files:**
- Modify: `run.py`

- [ ] **Step 1: 编写 TUI 路径选择功能**

```python
# run.py

# 现有代码...
def print_controls():
    """打印控制说明"""
    print("Controls:")
    print("  ↑/↓: 选择模型")
    print("  Enter: 启动/停止模型")
    print("  L: 配置 llama.cpp 路径")
    print("  Q: 退出")

def configure_llama_cpp_path():
    """配置 llama.cpp 路径"""
    from state_manager import StateManager
    manager = StateManager()
    current_paths = manager.get_paths()
    
    print("\n=== 配置 llama.cpp 路径 ===")
    print(f"当前路径: {current_paths['llama_cpp_path']}")
    
    new_path = input("请输入新的 llama.cpp 路径 (留空保持当前路径): ").strip()
    
    if new_path:
        try:
            manager.set_llama_cpp_path(new_path)
            print("\n✅ 路径更新成功!")
            print(f"新路径: {new_path}")
            print(f"模型目录: {current_paths['model_dir']}")
        except Exception as e:
            print(f"\n❌ 路径更新失败: {e}")
    else:
        print("\nℹ️  保持当前路径不变")
    
    input("按 Enter 键返回...")

# 主循环中添加 'L' 键处理
# 现有代码...
while True:
    # 现有代码...
    key = getch()
    
    if key == 'q' or key == 'Q':
        break
    elif key == 'L' or key == 'l':
        configure_llama_cpp_path()
        # 重新加载状态以显示最新模型
        state = StateManager()
        models = state.get_models()
        selected_model = 0
    # 现有代码...

# 在打印页脚时添加路径信息
def print_footer():
    """打印页脚信息"""
    from state_manager import StateManager
    state = StateManager()
    paths = state.get_paths()
    
    print("\n" + "-" * 80)
    print(f"llama.cpp 路径: {paths['llama_cpp_path']}")
    print(f"模型目录: {paths['model_dir']}")
    print("-" * 80)
```

- [ ] **Step 2: 测试 TUI 路径选择功能**

Run: `python run.py`
Expected: 可以通过按 'L' 键进入路径配置界面，输入新路径后更新成功

- [ ] **Step 3: 提交**

```bash
git add run.py
git commit -m "feat: add TUI interface for llama.cpp path selection"
```

### Task 4: 添加 WebUI 端点用于路径配置

**Files:**
- Modify: `web_app.py`

- [ ] **Step 1: 编写 WebUI 路径配置端点**

```python
# web_app.py

# 现有代码...

@app.get("/api/path")
def get_path():
    """获取当前路径配置"""
    from state_manager import StateManager
    manager = StateManager()
    return manager.get_paths()

@app.post("/api/path")
def update_path(path: str):
    """更新 llama.cpp 路径"""
    from state_manager import StateManager
    manager = StateManager()
    try:
        result = manager.set_llama_cpp_path(path)
        return {"success": True, "paths": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

- [ ] **Step 2: 测试 WebUI 路径配置端点**

Run: `curl -X GET http://localhost:8000/api/path`
Expected: 返回当前路径配置

Run: `curl -X POST -H "Content-Type: application/json" -d '{"path": "/custom/path"}' http://localhost:8000/api/path`
Expected: 返回更新后的路径配置

- [ ] **Step 3: 提交**

```bash
git add web_app.py
git commit -m "feat: add WebUI endpoints for llama.cpp path configuration"
```

### Task 5: 添加 WebUI 界面用于路径选择

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: 编写 WebUI 路径选择界面**

```html
<!-- templates/index.html -->

<!-- 现有代码... -->

<div class="card mb-4">
  <div class="card-header">
    <h5 class="card-title">llama.cpp 路径配置</h5>
  </div>
  <div class="card-body">
    <div class="mb-3">
      <label for="llamaCppPath" class="form-label">llama.cpp 路径</label>
      <input type="text" class="form-control" id="llamaCppPath" v-model="llamaCppPath">
    </div>
    <div class="mb-3">
      <label class="form-label">模型目录</label>
      <input type="text" class="form-control" v-model="modelDir" disabled>
    </div>
    <button class="btn btn-primary" @click="updatePath" :disabled="isUpdating">
      {{ isUpdating ? '更新中...' : '更新路径' }}
    </button>
    <div v-if="pathMessage" class="mt-3 alert" :class="pathMessage.type === 'success' ? 'alert-success' : 'alert-danger'">
      {{ pathMessage.text }}
    </div>
  </div>
</div>

<!-- 现有代码... -->

<script>
// 现有代码...

new Vue({
  el: '#app',
  data: {
    // 现有数据...
    llamaCppPath: '',
    modelDir: '',
    pathMessage: null,
    isUpdating: false
  },
  methods: {
    // 现有方法...
    
    async getPathConfig() {
      try {
        const response = await fetch('/api/path');
        const data = await response.json();
        this.llamaCppPath = data.llama_cpp_path;
        this.modelDir = data.model_dir;
      } catch (error) {
        console.error('获取路径配置失败:', error);
      }
    },
    
    async updatePath() {
      if (!this.llamaCppPath) {
        this.pathMessage = { type: 'danger', text: '路径不能为空' };
        return;
      }
      
      this.isUpdating = true;
      this.pathMessage = null;
      
      try {
        const response = await fetch('/api/path', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ path: this.llamaCppPath })
        });
        
        const data = await response.json();
        
        if (data.success) {
          this.pathMessage = { type: 'success', text: '路径更新成功' };
          this.modelDir = data.paths.model_dir;
          // 刷新模型列表
          this.loadModels();
        } else {
          this.pathMessage = { type: 'danger', text: `更新失败: ${data.error}` };
        }
      } catch (error) {
        this.pathMessage = { type: 'danger', text: `更新失败: ${error.message}` };
      } finally {
        this.isUpdating = false;
      }
    }
  },
  mounted() {
    // 现有代码...
    this.getPathConfig();
  }
});
</script>
```

- [ ] **Step 2: 测试 WebUI 路径选择功能**

Run: 启动应用并访问 WebUI
Expected: 可以在路径配置部分输入新路径并更新，更新后模型列表会自动刷新

- [ ] **Step 3: 提交**

```bash
git add templates/index.html
git commit -m "feat: add WebUI interface for llama.cpp path selection"
```

### Task 6: 运行完整测试

**Files:**
- All modified files

- [ ] **Step 1: 运行所有测试**

Run: `pytest`
Expected: 所有测试通过

- [ ] **Step 2: 测试完整功能**

1. 启动应用
2. 通过 TUI 测试路径选择功能
3. 通过 WebUI 测试路径选择功能
4. 验证路径变更后模型列表是否正确刷新

- [ ] **Step 3: 提交最终代码**

```bash
git add .
git commit -m "feat: complete llama.cpp path selection feature"
```

---

## 执行交接

计划已完成并保存到 `docs/superpowers/plans/2026-04-22-llama-cpp-path-selection.md`。

**两种执行选项：**

**1. 子代理驱动（推荐）** - 我为每个任务分派一个新的子代理，任务之间进行审查，快速迭代

**2. 内联执行** - 使用 executing-plans 在当前会话中执行任务，批量执行并设置检查点

**选择哪种方法？**