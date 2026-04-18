#!/usr/bin/env python3
"""
FastAPI Web Backend for llama-launcher
Provides RESTful API for model management and monitoring
"""

import os
import sys
import time
import re
import subprocess
import threading
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ============== Server Configuration ==============
WEB_HOST = "0.0.0.0"
WEB_PORT = 80  # 默认端口

# Create FastAPI app
app = FastAPI(
    title="Llama Launcher WebUI",
    description="Web interface for llama.cpp model management",
    version="3.1"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import shared modules
from state_manager import (
    StateManager, get_state_manager, ServerStats,
    scan_models, CTX_SIZE_OPTIONS, NGL_OPTIONS,
    LLAMA_CPP_PATH, BUILD_BIN_PATH, LOG_DIR, format_size
)

# State manager instance
state_mgr = get_state_manager()

# ============== Server Stats Parsing ==============
def parse_server_log(log_file: str) -> ServerStats:
    """Parse server log to extract metrics"""
    stats = ServerStats()
    if not log_file or not os.path.exists(log_file):
        return stats
    
    try:
        with open(log_file, "r") as f:
            content = f.read()
        
        prompt_match = re.search(r'prompt token.*?(\d+)', content, re.IGNORECASE)
        if prompt_match:
            stats.prompt_tokens = int(prompt_match.group(1))
        
        eval_match = re.search(r'evaluation.*?(\d+) tokens', content, re.IGNORECASE)
        if eval_match:
            stats.eval_tokens = int(eval_match.group(1))
        
        ppd_match = re.search(r'prompt.*?(\d+\.?\d*) tok/ ?s', content, re.IGNORECASE)
        if ppd_match:
            stats.prompt_per_second = float(ppd_match.group(1))
        
        epd_match = re.search(r'(\d+\.?\d*) tok/ ?s', content)
        if epd_match:
            stats.eval_per_second = float(epd_match.group(1))
        
        ctx_match = re.search(r'context.*?(\d+)/(\d+)', content, re.IGNORECASE)
        if ctx_match:
            stats.ctx_used = int(ctx_match.group(1))
            stats.ctx_total = int(ctx_match.group(2))
        
        time_match = re.search(r'(\d+\.?\d+) s', content)
        if time_match:
            stats.total_time = float(time_match.group(1))
    except Exception:
        pass
    return stats


def terminate_process(proc: Optional[subprocess.Popen], timeout: int = 5) -> bool:
    """Terminate a process gracefully"""
    if not proc or proc.poll() is not None:
        return True
    try:
        proc.terminate()
        proc.wait(timeout=timeout)
        return True
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return True
    except Exception as e:
        print(f"Error terminating process: {e}")
        return False


# ============== Process Management ==============
def run_cli(model_path: str, ctx_size: int, ngl: int) -> subprocess.Popen:
    """Run CLI mode"""
    args = [
        os.path.join(BUILD_BIN_PATH, "llama-cli"),
        "-m", model_path,
        "-ngl", str(ngl),
        "-c", str(ctx_size),
        "--color", "on"
    ]
    return subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_server(model_path: str, ctx_size: int, ngl: int, port: int):
    """Run Server mode"""
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"server_{port}.log")
    with open(log_file, "w") as f:
        f.write("")
    args = [
        os.path.join(BUILD_BIN_PATH, "llama-server"),
        "-m", model_path,
        "-ngl", str(ngl),
        "-c", str(ctx_size),
        "--port", str(port),
        "--host", "0.0.0.0"
    ]
    with open(log_file, "a") as f:
        proc = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT)
    return proc, log_file


def run_embedding(model_path: str, ngl: int) -> subprocess.Popen:
    """Run Embedding mode"""
    args = [
        os.path.join(BUILD_BIN_PATH, "llama-embedding"),
        "-m", model_path,
        "-ngl", str(ngl)
    ]
    return subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# Background stats update thread
_stats_thread_running = True
_stats_thread = None


def stats_updater():
    """Background thread to update server stats"""
    global _stats_thread_running
    while _stats_thread_running:
        try:
            state = state_mgr.state
            if state.is_running and state.log_file:
                stats = parse_server_log(state.log_file)
                state_mgr.update_stats(stats)
        except Exception as e:
            print(f"Stats update error: {e}")
        time.sleep(1.0)


# ============== API Routes ==============

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    state_mgr.set_webui_status(True)
    global _stats_thread
    _stats_thread = threading.Thread(target=stats_updater, daemon=True)
    _stats_thread.start()
    
    # Scan models
    models = scan_models()
    state_mgr.set_models(models)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global _stats_thread_running
    _stats_thread_running = False
    state_mgr.set_webui_status(False)


@app.get("/", response_class=HTMLResponse)
async def index():
    """Main page"""
    html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            return f.read()
    return """<html><head><title>Llama Launcher</title></head><body><h1>Loading...</h1></body></html>"""


@app.get("/api/state")
async def get_state():
    """Get current application state"""
    return JSONResponse(content=state_mgr.get_state())


@app.get("/api/models")
async def get_models():
    """Get model list"""
    models = scan_models()
    state_mgr.set_models(models)
    return JSONResponse(content={"models": models})


@app.post("/api/config")
async def update_config(request: Request):
    """Update configuration"""
    data = await request.json()
    ctx_idx = data.get("ctx_idx")
    ngl_idx = data.get("ngl_idx")
    port = data.get("port")
    
    state_mgr.set_config(ctx_idx=ctx_idx, ngl_idx=ngl_idx, port=port)
    return JSONResponse(content={"success": True, "state": state_mgr.get_state()})


@app.post("/api/start")
async def start_model(request: Request):
    """Start a model"""
    data = await request.json()
    model_name = data.get("model_name")
    mode = data.get("mode", 1)
    
    # Find model in list
    models = scan_models()
    model = None
    for m in models:
        if m["name"] == model_name:
            model = m
            break
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    state = state_mgr.state
    ctx_size = CTX_SIZE_OPTIONS[state.ctx_idx]
    ngl = NGL_OPTIONS[state.ngl_idx]
    port = state.port
    
    try:
        proc = None
        log_file = ""
        
        if mode == 0:  # CLI
            proc = run_cli(model["path"], ctx_size, ngl)
        elif mode == 1:  # Server
            proc, log_file = run_server(model["path"], ctx_size, ngl, port)
        elif mode == 2:  # Embedding
            proc = run_embedding(model["path"], ngl)
        
        pid = proc.pid if proc else None
        state_mgr.set_process(
            is_running=True,
            pid=pid,
            process_obj=proc,
            model_name=model["name"],
            model_path=model["path"],
            mode=mode,
            log_file=log_file
        )
        
        return JSONResponse(content={
            "success": True,
            "message": f"Model '{model_name}' started",
            "pid": pid
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stop")
async def stop_model():
    """Stop current model"""
    state = state_mgr.state
    
    if not state.is_running:
        return JSONResponse(content={"success": True, "message": "No model running"})
    
    try:
        proc = state.process_obj
        if proc:
            terminate_process(proc)
        
        state_mgr.clear_process()
        
        return JSONResponse(content={
            "success": True,
            "message": "Model stopped"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/options")
async def get_options():
    """Get available options"""
    return JSONResponse(content={
        "ctx_options": [
            {"idx": i, "value": v, "label": format_ctx(v)} 
            for i, v in enumerate(CTX_SIZE_OPTIONS)
        ],
        "ngl_options": [
            {"idx": i, "value": v} 
            for i, v in enumerate(NGL_OPTIONS)
        ],
        "mode_options": [
            {"value": 0, "label": "CLI"},
            {"value": 1, "label": "Server"},
            {"value": 2, "label": "Embedding"}
        ]
    })


def format_ctx(ctx: int) -> str:
    """Format context size"""
    if ctx >= 1024:
        return f"{ctx // 1024}k"
    return str(ctx)


def start_web_server(host: str = WEB_HOST, port: int = WEB_PORT):
    """Start the web server"""
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_web_server()