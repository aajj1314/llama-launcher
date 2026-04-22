#!/usr/bin/env python3
"""
Web界面模块
提供REST API和Web界面
"""

import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any, Optional
from config import RunMode, get_config, get_config_manager
from state import get_state_manager, ProcessStatus


app = FastAPI(title="Llama Launcher", description="用户友好的 llama.cpp 模型启动器", version="4.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    state_manager = get_state_manager()
    state_manager.scan_models()


@app.get("/", response_class=HTMLResponse)
async def get_index():
    """主页"""
    index_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return """<html><head><title>Llama Launcher</title></head>
<body><h1>加载中...</h1><p>请确保 templates/index.html 文件存在</p></body></html>"""


@app.get("/api/state")
async def get_state():
    """获取当前状态"""
    state_manager = get_state_manager()
    return JSONResponse(content=state_manager.get_state_dict())


@app.post("/api/models/scan")
async def scan_models():
    """扫描模型"""
    state_manager = get_state_manager()
    state_manager.scan_models()
    return JSONResponse(content={"success": True})


@app.post("/api/models/select")
async def select_model(request: Request):
    """选择模型"""
    try:
        data = await request.json()
        model_name = data.get("model_name")
        state_manager = get_state_manager()
        state_manager.set_selected_model(model_name)
        return JSONResponse(content={"success": True})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/config/update")
async def update_config(request: Request):
    """更新配置"""
    try:
        data = await request.json()
        config_manager = get_config_manager()
        # 更新配置
        config_manager.update(**data)
        return JSONResponse(content={"success": True, "config": config_manager.get().to_dict()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/path/update")
async def update_path(request: Request):
    """更新 llama.cpp 路径"""
    try:
        data = await request.json()
        path = data.get("path")
        if not path:
            raise HTTPException(status_code=400, detail="路径不能为空")
        state_manager = get_state_manager()
        success = state_manager.set_llama_cpp_path(path)
        if success:
            return JSONResponse(content={"success": True})
        else:
            state_dict = state_manager.get_state_dict()
            raise HTTPException(status_code=400, detail=state_dict["process"]["error_message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/process/start")
async def start_process(request: Request):
    """启动进程"""
    try:
        data = await request.json()
        mode_str = data.get("mode")
        model_name = data.get("model_name")

        if not mode_str or not model_name:
            raise HTTPException(status_code=400, detail="模式和模型不能为空")

        mode = RunMode(mode_str)
        state_manager = get_state_manager()
        success = state_manager.start_process(mode, model_name)

        if success:
            return JSONResponse(content={"success": True})
        else:
            state_dict = state_manager.get_state_dict()
            raise HTTPException(status_code=400, detail=state_dict["process"]["error_message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/process/stop")
async def stop_process():
    """停止进程"""
    try:
        state_manager = get_state_manager()
        success = state_manager.stop_process()
        return JSONResponse(content={"success": success})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/process/restart")
async def restart_process():
    """重启进程"""
    try:
        state_manager = get_state_manager()
        success = state_manager.restart_process()
        return JSONResponse(content={"success": success})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/logs")
async def get_logs(max_lines: int = 100):
    """获取日志"""
    state_manager = get_state_manager()
    lines = state_manager.get_log_content(max_lines)
    return JSONResponse(content={"logs": lines})


def start_web_server(host: str = "0.0.0.0", port: int = 8000):
    """启动Web服务器"""
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_web_server()
