# 测试和部署计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 进行全方位测试，验证功能正常运行后上传到 GitHub 分支。

**Architecture:** 按阶段执行：功能测试 → WebUI 浏览器测试 → 部署到 GitHub。

**Tech Stack:** Python, FastAPI, Vue.js, llama.cpp, git

---

## 测试范围

### 功能测试
1. TUI 界面功能测试
2. WebUI 界面功能测试
3. llama.cpp 路径选择功能测试
4. 模型启动/停止功能测试
5. 状态管理功能测试

### 浏览器测试
1. WebUI 页面加载测试
2. 路径配置功能测试
3. 模型选择和启动测试
4. 响应式设计测试

---

### Task 1: 功能测试 - TUI 界面

**Files:**
- `run.py`
- `config.py`
- `state_manager.py`

- [ ] **Step 1: 运行 TUI 界面测试**

Run: `python run.py`
Expected: 
- TUI 界面正常显示
- 可以看到控制说明，包括 'L' 键用于路径配置
- 页脚显示当前 llama.cpp 路径和模型目录
- 可以正常查看和选择模型

- [ ] **Step 2: 测试 llama.cpp 路径选择功能**

在 TUI 界面中按 'L' 键进入路径配置界面：
Expected:
- 显示当前路径
- 可以输入新路径
- 路径更新成功后显示确认信息
- 返回主界面后模型列表刷新

---

### Task 2: 功能测试 - WebUI 后端

**Files:**
- `web_app.py`
- `config.py`
- `state_manager.py`

- [ ] **Step 1: 启动 Web 服务器**

Run: `python web_app.py`
Expected: 服务器在 http://localhost:8000 正常启动

- [ ] **Step 2: 测试路径配置 API 端点**

Run: `curl -X GET http://localhost:8000/api/path`
Expected: 返回当前路径配置的 JSON 数据

Run: `curl -X POST -H "Content-Type: application/json" -d '{"path": "/test/path"}' http://localhost:8000/api/path`
Expected: 返回更新成功的 JSON 数据

- [ ] **Step 3: 测试其他 API 端点**

Run: `curl -X GET http://localhost:8000/api/models`
Expected: 返回可用模型列表

Run: `curl -X GET http://localhost:8000/api/state`
Expected: 返回当前状态信息

---

### Task 3: 浏览器测试 - WebUI 界面

**Files:**
- `templates/index.html`
- `web_app.py`

- [ ] **Step 1: 锁定浏览器并导航到 WebUI**

调用浏览器锁定工具，然后导航到 http://localhost:8000

- [ ] **Step 2: 测试页面加载**

检查页面是否正常加载，所有元素是否正确显示。

- [ ] **Step 3: 测试路径配置功能**

1. 找到 llama.cpp 路径配置区域
2. 输入新的路径
3. 点击更新按钮
4. 验证路径更新成功，模型列表刷新

- [ ] **Step 4: 测试模型选择功能**

1. 查看可用模型列表
2. 选择一个模型
3. 测试启动/停止功能

- [ ] **Step 5: 测试响应式设计**

调整浏览器窗口大小，验证界面在不同尺寸下都能正常显示。

- [ ] **Step 6: 解锁浏览器**

完成测试后调用浏览器解锁工具。

---

### Task 4: 完整功能集成测试

**Files:**
- All modified files

- [ ] **Step 1: 同时测试 TUI 和 WebUI**

1. 启动 TUI 界面（run.py）
2. 配置 llama.cpp 路径
3. 启动 Web 服务器（web_app.py）
4. 验证两个界面都能正常工作
5. 验证路径变更在两个界面间同步

- [ ] **Step 2: 测试完整工作流程**

1. 选择 llama.cpp 路径
2. 扫描可用模型
3. 选择并启动模型
4. 验证模型状态更新
5. 停止模型
6. 验证模型状态正确更新

---

### Task 5: 准备部署到 GitHub

**Files:**
- All modified files

- [ ] **Step 1: 检查 git 状态**

Run: `cd /workspace && git status`
Expected: 工作区干净或有需要提交的变更

- [ ] **Step 2: 查看 git 日志**

Run: `cd /workspace && git log --oneline -10`
Expected: 显示最近的提交记录

- [ ] **Step 3: 提交所有变更**

Run: 
```bash
cd /workspace
git add .
git commit -m "feat: complete llama.cpp path selection feature and testing"
```

---

### Task 6: 推送到 GitHub

**Files:**
- Git configuration

- [ ] **Step 1: 检查远程仓库配置**

Run: `cd /workspace && git remote -v`
Expected: 显示远程仓库信息

- [ ] **Step 2: 推送到当前分支**

Run: `cd /workspace && git push origin trae/solo-agent-iFS47n`
Expected: 成功推送到 GitHub

---

### Task 7: 验证部署

**Files:**
- GitHub repository

- [ ] **Step 1: 验证推送成功**

确认代码已成功推送到 GitHub 分支。

- [ ] **Step 2: 创建最终测试报告**

记录所有测试结果和功能验证情况。

---

## 执行交接

计划已完成并保存到 `docs/superpowers/plans/2026-04-22-test-and-deploy.md`。

**两种执行选项：**

**1. 子代理驱动（推荐）** - 我为每个任务分派一个新的子代理，任务之间进行审查，快速迭代

**2. 内联执行** - 在当前会话中执行任务，批量执行并设置检查点

**选择哪种方法？**