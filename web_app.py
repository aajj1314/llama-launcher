#!/usr/bin/env python3
"""
FastAPI Web Backend for llama-launcher
Provides RESTful API for model management and monitoring
"""

import os
import time
import threading
import logging
from typing import Dict, Any

# Import shared modules first to get LOG_DIR
from state_manager import (
    get_state_manager, ServerStats,
    scan_models, CTX_SIZE_OPTIONS, NGL_OPTIONS,
    LLAMA_CPP_PATH, LOG_DIR, format_size, format_ctx
)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
import logging.handlers

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler with rotation
log_file = os.path.join(LOG_DIR, "llama_launcher_web.log")
file_handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB per file
    backupCount=5  # Keep up to 5 backup files
)

# Create console handler
console_handler = logging.StreamHandler()

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Set formatters
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# ============== Server Configuration ==============
WEB_HOST = "0.0.0.0"
WEB_PORT = 8000  # 默认端口

# Create FastAPI app
app = FastAPI(
    title="Llama Launcher WebUI",
    description="Web interface for llama.cpp model management",
    version="3.2"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# State manager instance
state_mgr = get_state_manager()

# ============== Server Stats Parsing ==============
from utils import parse_server_log, terminate_process
from process_manager import run_cli, run_server, run_embedding, validate_binary


# ============== Process Management ==============


# Background stats update thread
_stats_thread = None


def stats_updater():
    """Background thread to update server stats"""
    while True:
        try:
            state = state_mgr.state
            if state.is_running and state.log_file:
                stats = parse_server_log(state.log_file)
                state_mgr.update_stats(stats)
        except Exception as e:
            logger.error(f"Stats update error: {e}")
        time.sleep(1.0)


# ============== API Routes ==============

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    # Set WebUI status to online
    state_mgr.set_webui_status(True)
    
    # Start stats update thread
    global _stats_thread
    _stats_thread = threading.Thread(target=stats_updater, daemon=True)
    _stats_thread.start()
    
    # Scan models and update state
    models = scan_models()
    state_mgr.set_models(models)
    
    logger.info("WebUI started and online")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # Stop stats update thread
    global _stats_thread_running
    _stats_thread_running = False
    
    # Set WebUI status to offline
    state_mgr.set_webui_status(False)
    
    # Stop any running process
    state = state_mgr.state
    if state.is_running:
        proc = state.process_obj
        if proc:
            terminate_process(proc)
        state_mgr.clear_process()
    
    logger.info("WebUI shutdown")


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
    """Get current application state with error handling"""
    try:
        state = state_mgr.get_state()
        return JSONResponse(content=state)
    except Exception as e:
        logger.error(f"Error in get_state: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/models")
async def get_models():
    """Get model list with error handling"""
    try:
        models = scan_models()
        state_mgr.set_models(models)
        return JSONResponse(content={"models": models})
    except Exception as e:
        logger.error(f"Error in get_models: {e}")
        return JSONResponse(content={"error": str(e), "models": []}, status_code=500)


@app.post("/api/config")
async def update_config(request: Request):
    """Update configuration with error handling"""
    try:
        data = await request.json()
        ctx_idx = data.get("ctx_idx")
        ngl_idx = data.get("ngl_idx")
        port = data.get("port")
        llama_cpp_path = data.get("llama_cpp_path")
        timeout = data.get("timeout")
        log_level = data.get("log_level")
        gpu_memory = data.get("gpu_memory")
        mode = data.get("mode")
        
        # Update path configuration if provided
        if llama_cpp_path is not None:
            if llama_cpp_path:
                global LLAMA_CPP_PATH, MODELS_PATH, BUILD_BIN_PATH, LOG_DIR
                # Validate path exists
                if os.path.exists(llama_cpp_path):
                    LLAMA_CPP_PATH = llama_cpp_path
                    MODELS_PATH = os.path.join(LLAMA_CPP_PATH, "models")
                    BUILD_BIN_PATH = os.path.join(LLAMA_CPP_PATH, "build", "bin")
                    LOG_DIR = os.path.join(LLAMA_CPP_PATH, "logs")
                    # Create necessary directories
                    for path in [MODELS_PATH, BUILD_BIN_PATH, LOG_DIR]:
                        os.makedirs(path, exist_ok=True)
                else:
                    return JSONResponse(content={"success": False, "error": f"Path does not exist: {llama_cpp_path}"}, status_code=400)
        
        # Update run mode if provided
        if mode is not None:
            try:
                mode = int(mode)
                if 0 <= mode <= 2:
                    state_mgr.set_run_mode(mode)
                else:
                    return JSONResponse(content={"success": False, "error": "Invalid mode"}, status_code=400)
            except ValueError:
                return JSONResponse(content={"success": False, "error": "Invalid mode format"}, status_code=400)
        
        # Validate and update configuration
        success = state_mgr.set_config(
            ctx_idx=ctx_idx, 
            ngl_idx=ngl_idx, 
            port=port,
            timeout=timeout,
            log_level=log_level,
            gpu_memory=gpu_memory
        )
        if success:
            return JSONResponse(content={"success": True, "state": state_mgr.get_state()})
        else:
            return JSONResponse(content={"success": False, "error": "Failed to update configuration"}, status_code=500)
    except Exception as e:
        logger.error(f"Error in update_config: {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@app.post("/api/start")
async def start_model(request: Request):
    """Start a model with error handling"""
    try:
        data = await request.json()
        model_name = data.get("model_name")
        mode = data.get("mode", 1)
        
        # Validate input
        if not model_name:
            return JSONResponse(content={"success": False, "error": "Model name is required"}, status_code=400)
        
        if mode < 0 or mode > 2:
            return JSONResponse(content={"success": False, "error": "Invalid mode"}, status_code=400)
        
        # Find model in list
        models = scan_models()
        model = None
        for m in models:
            if m["name"] == model_name:
                model = m
                break
        
        if not model:
            return JSONResponse(content={"success": False, "error": "Model not found"}, status_code=404)
        
        # Check if model file exists
        if not os.path.exists(model["path"]):
            return JSONResponse(content={"success": False, "error": f"Model file does not exist: {model['path']}"}, status_code=404)
        
        # Check if llama.cpp binaries exist
        if not validate_binary(mode):
            binaries = {0: "llama-cli", 1: "llama-server", 2: "llama-embedding"}
            binary_name = binaries.get(mode, "unknown")
            return JSONResponse(content={"success": False, "error": f"{binary_name} binary not found"}, status_code=500)
        
        # Get current configuration
        state = state_mgr.state
        ctx_size = CTX_SIZE_OPTIONS[state.ctx_idx]
        ngl = NGL_OPTIONS[state.ngl_idx]
        port = state.port
        
        # Stop any running process first
        if state.is_running:
            proc = state.process_obj
            if proc:
                terminate_process(proc)
            state_mgr.clear_process()
        
        proc = None
        log_file = ""
        
        try:
            if mode == 0:  # CLI
                proc = run_cli(model["path"], ctx_size, ngl)
            elif mode == 1:  # Server
                proc, log_file = run_server(model["path"], ctx_size, ngl, port)
            elif mode == 2:  # Embedding
                proc = run_embedding(model["path"], ngl)
            
            # Verify process started
            if not proc or proc.poll() is not None:
                return JSONResponse(content={"success": False, "error": "Failed to start process"}, status_code=500)
            
            pid = proc.pid if proc else None
            success = state_mgr.set_process(
                is_running=True,
                pid=pid,
                process_obj=proc,
                model_name=model["name"],
                model_path=model["path"],
                mode=mode,
                log_file=log_file
            )
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": f"Model '{model_name}' started",
                    "pid": pid
                })
            else:
                # Clean up process if state update failed
                if proc:
                    terminate_process(proc)
                return JSONResponse(content={"success": False, "error": "Failed to update process state"}, status_code=500)
        except Exception as e:
            # Clean up process if any error occurs
            if proc:
                terminate_process(proc)
            logger.error(f"Error starting model: {e}")
            return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
    except Exception as e:
        logger.error(f"Error in start_model: {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@app.post("/api/stop")
async def stop_model():
    """Stop current model with error handling"""
    try:
        state = state_mgr.state
        
        if not state.is_running:
            return JSONResponse(content={"success": True, "message": "No model running"})
        
        try:
            proc = state.process_obj
            if proc:
                # Try to terminate process gracefully
                success = terminate_process(proc)
                if not success:
                    logger.warning("Failed to terminate process gracefully")
            
            # Clear process state
            clear_success = state_mgr.clear_process()
            if clear_success:
                return JSONResponse(content={
                    "success": True,
                    "message": "Model stopped"
                })
            else:
                return JSONResponse(content={"success": False, "error": "Failed to clear process state"}, status_code=500)
        except Exception as e:
            logger.error(f"Error stopping model: {e}")
            # Still try to clear process state
            state_mgr.clear_process()
            return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
    except Exception as e:
        logger.error(f"Error in stop_model: {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


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
        ],
        "log_level_options": [
            {"value": "DEBUG", "label": "Debug"},
            {"value": "INFO", "label": "Info"},
            {"value": "WARNING", "label": "Warning"},
            {"value": "ERROR", "label": "Error"}
        ],
        "timeout_options": [
            {"value": 10, "label": "10s"},
            {"value": 30, "label": "30s"},
            {"value": 60, "label": "1m"},
            {"value": 120, "label": "2m"},
            {"value": 300, "label": "5m"}
        ]
    })


@app.get("/api/path")
async def get_path():
    """Get current llama.cpp path"""
    try:
        paths = state_mgr.get_paths()
        return JSONResponse(content={"success": True, "paths": paths})
    except Exception as e:
        logger.error(f"Error in get_path: {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@app.post("/api/path")
async def update_path(request: Request):
    """Update llama.cpp path"""
    try:
        data = await request.json()
        path = data.get("path")
        
        if not path:
            return JSONResponse(content={"success": False, "error": "Path is required"}, status_code=400)
        
        # Update path using state manager
        paths = state_mgr.set_llama_cpp_path(path)
        
        # Update global paths
        global LLAMA_CPP_PATH, MODELS_PATH, BUILD_BIN_PATH, LOG_DIR
        LLAMA_CPP_PATH = paths["llama_cpp_path"]
        MODELS_PATH = paths["models_path"]
        BUILD_BIN_PATH = paths["build_bin_path"]
        LOG_DIR = paths["log_dir"]
        
        # Rescan models with new path
        models = scan_models()
        state_mgr.set_models(models)
        
        return JSONResponse(content={"success": True, "paths": paths})
    except Exception as e:
        logger.error(f"Error in update_path: {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


def start_web_server(host: str = WEB_HOST, port: int = WEB_PORT):
    """Start the web server"""
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_web_server()