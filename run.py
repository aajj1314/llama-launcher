#!/usr/bin/env python3
"""
Llama. cpp Model Launcher (Python) - Cyberpunk Edition
Uses shared StateManager for TUI + WebUI synchronization
"""

import os
import sys
import subprocess
import time
import signal
import re
import threading
import logging
import logging.handlers
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

# Import shared state manager
from state_manager import (
    StateManager, get_state_manager, ServerStats,
    scan_models, CTX_SIZE_OPTIONS, NGL_OPTIONS,
    LLAMA_CPP_PATH, BUILD_BIN_PATH, LOG_DIR,
    LARGE_MODEL_THRESHOLD, format_size, format_ctx
)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler with rotation
log_file = os.path.join(LOG_DIR, "llama_launcher_tui.log")
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

# Get singleton state manager
state_mgr = get_state_manager()

# Use shared constants from state_manager
MODELS_PATH = os.path.join(LLAMA_CPP_PATH, "models")

def format_speed(speed: float) -> str:
    if speed >= 1000:
        return f"{speed:.0f}"
    elif speed >= 1:
        return f"{speed:.1f}"
    return f"{speed:.2f}"

C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_dim = "\033[2m"
C_cyan = "\033[1;38;5;51m"
C_magenta = "\033[1;38;5;201m"
C_orange = "\033[1;38;5;208m"
C_green = "\033[1;38;5;46m"
C_red = "\033[1;38;5;196m"
C_yellow = "\033[1;38;5;226m"
C_blue = "\033[1;38;5;39m"
C_purple = "\033[1;38;5;93m"
C_teal = "\033[1;38;5;43m"

BG_dark = "\033[48;5;16m"
BG_cyan = "\033[48;5;30m"
BG_magenta = "\033[48;5;53m"

def scan_large_models() -> List[Dict[str, Any]]:
    """Scan for large models (>1GB) - for TUI display"""
    # Optimized version that filters during scanning
    if MODELS_PATH is None:
        return []
    
    models = []
    try:
        os.makedirs(MODELS_PATH, exist_ok=True)
        # Use os.scandir for better performance
        with os.scandir(MODELS_PATH) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith(".gguf"):
                    stat_info = entry.stat()
                    # Filter large models during scanning
                    if stat_info.st_size > LARGE_MODEL_THRESHOLD:
                        models.append({
                            "name": entry.name,
                            "path": entry.path,
                            "size": stat_info.st_size,
                            "size_formatted": format_size(stat_info.st_size)
                        })
    except Exception as e:
        print(f"  {C_red}✗ Error scanning models: {e}{C_RESET}")
    
    # Sort models by name for consistent ordering
    return sorted(models, key=lambda m: m["name"])


def clear_screen():
    print("\033[2J\033[H", end="")


def terminate_process(proc: Optional[subprocess.Popen], timeout: int = 5) -> None:
    if not proc or proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def parse_server_log(log_file: str) -> ServerStats:
    stats = ServerStats()
    if not os.path.exists(log_file):
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

        ppd_match = re.search(r'prompt.*?(\d+\.?\d*) tok/s', content, re.IGNORECASE)
        if ppd_match:
            stats.prompt_per_second = float(ppd_match.group(1))

        epd_match = re.search(r'(\d+\.?\d*) tok/s', content)
        if epd_match:
            stats.eval_per_second = float(epd_match.group(1))

        ctx_match = re.search(r'context.*?(\d+)/(\d+)', content, re.IGNORECASE)
        if ctx_match:
            stats.ctx_used = int(ctx_match.group(1))
            stats.ctx_total = int(ctx_match.group(2))

        time_match = re.search(r'(\d+\.?\d+) s', content)
        if time_match:
            stats.total_time = float(time_match.group(1))
    except:
        pass
    return stats


def get_key():
    import termios
    import tty
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            next1 = sys.stdin.read(1)
            next2 = sys.stdin.read(1)
            if next1 == '[':
                if next2 == 'A':
                    return 'UP'
                elif next2 == 'B':
                    return 'DOWN'
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def get_input(prompt: str, default: str = "") -> str:
    print(f"\n\033[1;38;5;208m{prompt}\033[0m ", end="", flush=True)
    try:
        user_input = input().strip()
        return user_input if user_input else default
    except (EOFError, KeyboardInterrupt):
        return default

def print_header():
    clear_screen()
    print(f"{BG_dark}{C_cyan}╔{'═' * 78}╗{C_RESET}")
    print(f"{BG_dark}{C_cyan}║{C_RESET}  {C_magenta}{C_BOLD}◈◈◈ LLAMA.CPP MODEL LAUNCHER v3.0 ◈◈◈{C_RESET}  {C_cyan}║{C_RESET}")
    print(f"{BG_dark}{C_cyan}║{C_RESET}  {C_dim}Cyberpunk Edition{C_RESET}  {'':30}  {C_cyan}║{C_RESET}")
    print(f"{BG_dark}{C_cyan}╚{'═' * 78}╝{C_RESET}\n")

def print_models(models: List[Dict[str, Any]], selected_idx: int):
    print(f"  {C_orange}{C_BOLD}▸ AVAILABLE MODELS{C_RESET} {C_dim}({len(models)} found){C_RESET}\n")

    if not models:
        print(f"  {C_red}⚠ No large models (>1GB) found in models directory{C_RESET}\n")
        return

    for i, model in enumerate(models):
        if i == selected_idx:
            print(f"  {C_cyan}►{C_RESET} {BG_cyan}{C_cyan}{i+1:2d}. {model['name']:<42} {format_size(model['size']):>12} {C_RESET}")
        else:
            print(f"  {C_dim}  {i+1:2d}.{C_RESET} {model['name']:<45} {C_dim}{format_size(model['size'])}{C_RESET}")

def print_settings(run_mode: int, ctx_idx: int, ngl_idx: int, port: int):
    modes = {0: ("CLI", C_green), 1: ("SERVER", C_blue), 2: ("EMBED", C_purple)}
    mode_name, mode_color = modes.get(run_mode, ("UNKNOWN", C_red))

    print(f"\n  {C_orange}{C_BOLD}▸ CONFIGURATION{C_RESET}\n")
    print(f"  ┌──────────────────────────────────────────────────────────────┐")
    print(f"  │  {C_cyan}MODE{C_RESET}:    {mode_color}{C_BOLD}{mode_name:<12}{C_RESET}", end="")
    print(f"  {C_cyan}CONTEXT{C_RESET}: {C_cyan}{C_BOLD}{format_ctx(CTX_SIZE_OPTIONS[ctx_idx]):>6}{C_RESET}", end="")
    print(f"  {C_cyan}NGL{C_RESET}:    {C_cyan}{C_BOLD}{NGL_OPTIONS[ngl_idx]:>4}{C_RESET}", end="")
    print(f"  {C_cyan}PORT{C_RESET}:   {C_cyan}{C_BOLD}{port}{C_RESET}  │")
    print(f"  └──────────────────────────────────────────────────────────────┘")

def print_stats(stats: ServerStats, process: Optional[subprocess.Popen], port: int):
    print(f"\n  {C_orange}{C_BOLD}▸ SERVER METRICS{C_RESET}\n")

    if not process or process.poll() is not None:
        print(f"  {C_dim}┌──────────────────────────────────────────────────────────────┐")
        print(f"  │                                                              │")
        print(f"  │  {C_red}● IDLE{C_RESET} - No model running                                   │")
        print(f"  │                                                              │")
        print(f"  └──────────────────────────────────────────────────────────────┘")
        return

    ctx_percent = (stats.ctx_used / stats.ctx_total * 100) if stats.ctx_total > 0 else 0
    ctx_bar_len = 30
    filled = int(ctx_bar_len * stats.ctx_used / stats.ctx_total) if stats.ctx_total > 0 else 0
    ctx_bar = "█" * filled + "░" * (ctx_bar_len - filled)

    ctx_color = C_green if ctx_percent < 60 else C_orange if ctx_percent < 85 else C_red

    print(f"  {C_dim}┌──────────────────────────────────────────────────────────────┐{C_RESET}")
    print(f"  {C_dim}│{C_RESET}  {C_green}● RUNNING{C_RESET}  {C_cyan}PID:{C_RESET}{process.pid:>6}  {C_cyan}Port:{C_RESET}{port:>5}              {C_dim}│{C_RESET}")
    print(f"  {C_dim}│{C_RESET}                                                              {C_dim}│{C_RESET}")
    print(f"  {C_dim}│{C_RESET}  {C_cyan}┌─────────────┬─────────────┬─────────────┬─────────────┐{C_RESET}  {C_dim}│{C_RESET}")
    print(f"  {C_dim}│{C_RESET}  {C_cyan}│{C_RESET}  {C_yellow}PROMPT TOK{C_RESET}  {C_cyan}│{C_RESET}   {C_green}EVAL TOK{C_RESET}   {C_cyan}│{C_RESET}   {C_magenta}PPD{C_RESET}   {C_cyan}│{C_RESET}   {C_orange}EPD{C_RESET}   {C_cyan}│{C_RESET}  {C_dim}│{C_RESET}")
    print(f"  {C_dim}│{C_RESET}  {C_cyan}│{C_RESET}    {C_BOLD}{stats.prompt_tokens:>6}{C_RESET}      {C_cyan}│{C_RESET}    {C_BOLD}{stats.eval_tokens:>6}{C_RESET}      {C_cyan}│{C_RESET}  {stats.prompt_per_second:>5.1f}  {C_cyan}│{C_RESET}  {stats.eval_per_second:>5.1f}  {C_cyan}│{C_RESET}  {C_dim}│{C_RESET}")
    print(f"  {C_dim}│{C_RESET}  {C_cyan}└─────────────┴─────────────┴─────────────┴─────────────┘{C_RESET}  {C_dim}│{C_RESET}")
    print(f"  {C_dim}│{C_RESET}                                                              {C_dim}│{C_RESET}")
    print(f"  {C_dim}│{C_RESET}  {C_cyan}CONTEXT:{C_RESET} {ctx_color}[{ctx_bar}]{C_RESET} {ctx_percent:>5.1f}% ({stats.ctx_used}/{stats.ctx_total})   {C_dim}│{C_RESET}")
    print(f"  {C_dim}│{C_RESET}                                                              {C_dim}│{C_RESET}")
    print(f"  {C_dim}└──────────────────────────────────────────────────────────────┘{C_RESET}")

def print_controls():
    print(f"\n  {C_orange}{C_BOLD}▸ CONTROLS{C_RESET}\n")
    print(f"  {C_dim}[{C_RESET}{C_cyan}↑↓/WS/45{C_RESET}{C_dim}]{C_RESET} Navigate  {C_dim}[{C_RESET}{C_cyan}1/2/3{C_RESET}{C_dim}]{C_RESET} Mode  {C_dim}[{C_RESET}{C_cyan}C{C_RESET}{C_dim}]{C_RESET} Context  {C_dim}[{C_RESET}{C_cyan}G{C_RESET}{C_dim}]{C_RESET} NGL")
    print(f"  {C_dim}[{C_RESET}{C_cyan}P{C_RESET}{C_dim}]{C_RESET} Port  {C_dim}[{C_RESET}{C_cyan}R{C_RESET}{C_dim}]{C_RESET} Refresh  {C_dim}[{C_RESET}{C_cyan}K{C_RESET}{C_dim}]{C_RESET} Kill  {C_dim}[{C_RESET}{C_cyan}ENTER{C_RESET}{C_dim}]{C_RESET} Launch  {C_dim}[{C_RESET}{C_cyan}Q{C_RESET}{C_dim}]{C_RESET} Quit")
    print(f"  {C_dim}[{C_RESET}{C_cyan}T{C_RESET}{C_dim}]{C_RESET} Toggle TUI  {C_dim}[{C_RESET}{C_cyan}W{C_RESET}{C_dim}]{C_RESET} Toggle WebUI  {C_dim}[{C_RESET}{C_cyan}S{C_RESET}{C_dim}]{C_RESET} Save Config")

def print_footer():
    print(f"\n  {C_dim}─────────────────────────────────────────────────────────────────────────────{C_RESET}")
    print(f"  {C_dim}│{C_RESET}  {C_cyan}llama.cpp{C_RESET} {C_dim}|{C_RESET} {C_purple}Python TUI{C_RESET} {C_dim}|{C_RESET} {C_teal}Cyberpunk Edition v3.0{C_RESET}  {'':20}  {C_dim}│{C_RESET}")
    print(f"  {C_dim}─────────────────────────────────────────────────────────────────────────────{C_RESET}")

def run_cli(model_path: str, ctx_size: int, ngl: int):
    args = [
        os.path.join(BUILD_BIN_PATH, "llama-cli"),
        "-m", model_path,
        "-ngl", str(ngl),
        "-c", str(ctx_size),
        "--color", "on"
    ]
    return subprocess.Popen(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

def run_server(model_path: str, ctx_size: int, ngl: int, port: int):
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
        return subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT), log_file

def run_embedding(model_path: str, ngl: int):
    args = [
        os.path.join(BUILD_BIN_PATH, "llama-embedding"),
        "-m", model_path,
        "-ngl", str(ngl)
    ]
    return subprocess.Popen(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

def on_state_change(state_dict):
    """Callback function for state changes"""
    pass

def main():
    """Main TUI loop with state manager integration"""
    running = True
    selected_idx = 0
    last_update_time = 0
    
    try:
        # Set TUI status to online
        state_mgr.set_tui_status(True)
        
        # Register state change callback
        state_mgr.register_callback(on_state_change)
        
        # Sync initial state from state manager
        models = scan_large_models()
        state = state_mgr.state
        run_mode = state.current_mode
        ctx_idx = state.ctx_idx
        ngl_idx = state.ngl_idx
        port = state.port if state.port != 80 else 8000
        
        # Sync models to state manager (only once at start)
        all_models = scan_models(MODELS_PATH)
        state_mgr.set_models(all_models)
        
        print_header()
        print(f"  {C_green}✓ Initializing Llama.cpp Launcher v3.1 (Cyberpunk Edition)...{C_RESET}")
        print(f"  {C_green}✓ Found {len(models)} large models{C_RESET}")
        print(f"  {C_green}✓ State Manager connected{C_RESET}")
        time.sleep(0.5)

        while running:
            # Get state from state manager
            state = state_mgr.state
            
            # Get process state from state manager
            current_process = state.process_obj
            current_log_file = state.log_file
            run_mode = state.current_mode
            ctx_idx = state.ctx_idx
            ngl_idx = state.ngl_idx
            port = state.port
            
            # Get server stats from state manager
            server_stats = state.server_stats
            
            # Update stats from log file for server mode
            current_time = time.time()
            if current_process and current_process.poll() is None and current_log_file:
                if current_time - last_update_time > 0.5:
                    parsed_stats = parse_server_log(current_log_file)
                    if parsed_stats.is_valid():
                        server_stats = parsed_stats
                        state_mgr.update_stats(server_stats)
                    last_update_time = current_time
            
            # Re-scan models only if list is empty (avoid repeated scanning)
            if not state.models:
                all_models = scan_models(MODELS_PATH)
                state_mgr.set_models(all_models)
            
            models = [m for m in state.models if m.get("size", 0) > LARGE_MODEL_THRESHOLD]
            
            # Adjust selection if needed
            if selected_idx >= len(models) and models:
                selected_idx = len(models) - 1
            
            print_header()
            print_models(models, selected_idx)
            print_settings(run_mode, ctx_idx, ngl_idx, port)
            print_stats(server_stats, current_process, port)
            print_controls()
            print_footer()
            print(f"\n\033[1;38;5;51m> \033[0m", end="", flush=True)
            
            # Check if process is still running
            if current_process and current_process.poll() is not None:
                state_mgr.clear_process()
                current_process = None
                current_log_file = ""
            
            try:
                key = get_key()
            except:
                key = 'q'
            
            # Configuration change handlers - sync to state manager
            if key in ('UP', 'w', 'W', '4'):
                if selected_idx > 0:
                    selected_idx -= 1
            elif key in ('DOWN', 's', 'S', '5'):
                if selected_idx < len(models) - 1:
                    selected_idx += 1
            elif key == '1':
                state_mgr.set_run_mode(0)
            elif key == '2':
                state_mgr.set_run_mode(1)
            elif key == '3':
                state_mgr.set_run_mode(2)
            elif key in ('c', 'C'):
                new_ctx = (ctx_idx + 1) % len(CTX_SIZE_OPTIONS)
                state_mgr.set_config(ctx_idx=new_ctx)
            elif key in ('g', 'G'):
                new_ngl = (ngl_idx + 1) % len(NGL_OPTIONS)
                state_mgr.set_config(ngl_idx=new_ngl)
            elif key in ('p', 'P'):
                print_header()
                print_models(models, selected_idx)
                print_settings(run_mode, ctx_idx, ngl_idx, port)
                print_stats(server_stats, current_process, port)
                print_controls()
                print_footer()
                port_input = get_input("Enter port number (1-65535):")
                if port_input:
                    try:
                        new_port = int(port_input)
                        if 1 <= new_port <= 65535:
                            state_mgr.set_config(port=new_port)
                        else:
                            print(f"\n  {C_red}✗ Port must be between 1 and 65535{C_RESET}")
                            time.sleep(1)
                    except ValueError:
                        print(f"\n  {C_red}✗ Invalid port number: {port_input}{C_RESET}")
                        time.sleep(1)
            elif key in ('r', 'R'):
                all_models = scan_models(MODELS_PATH)
                state_mgr.set_models(all_models)
                print(f"\n  {C_green}✓ Models refreshed{C_RESET}")
                time.sleep(0.3)
            elif key in ('k', 'K'):
                if state.is_running:
                    proc = state.process_obj
                    if proc:
                        try:
                            proc.terminate()
                            proc.wait(timeout=5)
                        except:
                            proc.kill()
                    state_mgr.clear_process()
            elif key in ('t', 'T'):
                # Toggle TUI status
                current_tui_status = state.tui_online
                state_mgr.set_tui_status(not current_tui_status)
                print(f"  {C_green}✓ TUI status toggled to {'Online' if not current_tui_status else 'Offline'}{C_RESET}")
                time.sleep(0.3)
            elif key in ('w', 'W'):
                # Toggle WebUI status (placeholder)
                print(f"  {C_yellow}⚠ WebUI toggle not implemented yet{C_RESET}")
                time.sleep(0.3)
            elif key in ('s', 'S'):
                # Save configuration
                try:
                    # This will trigger save_config through set_config
                    state_mgr.set_config(ctx_idx=ctx_idx, ngl_idx=ngl_idx, port=port)
                    print(f"  {C_green}✓ Configuration saved{C_RESET}")
                except Exception as e:
                    print(f"  {C_red}✗ Error saving configuration: {e}{C_RESET}")
                time.sleep(0.3)
            elif key in ('\r', '\n'):
                if models and 0 <= selected_idx < len(models):
                    model = models[selected_idx]
                    
                    # Stop any running process first
                    if state.is_running:
                        proc = state.process_obj
                        if proc:
                            try:
                                proc.terminate()
                                proc.wait(timeout=5)
                            except:
                                proc.kill()
                        state_mgr.clear_process()
                    
                    # Start new process
                    ctx_size = CTX_SIZE_OPTIONS[ctx_idx]
                    ngl = NGL_OPTIONS[ngl_idx]
                    
                    if run_mode == 0:  # CLI
                        proc = run_cli(model["path"], ctx_size, ngl)
                        state_mgr.set_process(
                            is_running=True,
                            pid=proc.pid,
                            process_obj=proc,
                            model_name=model["name"],
                            model_path=model["path"],
                            mode=run_mode,
                            log_file=""
                        )
                    elif run_mode == 1:  # Server
                        proc, log_file = run_server(model["path"], ctx_size, ngl, port)
                        state_mgr.set_process(
                            is_running=True,
                            pid=proc.pid,
                            process_obj=proc,
                            model_name=model["name"],
                            model_path=model["path"],
                            mode=run_mode,
                            log_file=log_file
                        )
                    elif run_mode == 2:  # Embedding
                        proc = run_embedding(model["path"], ngl)
                        state_mgr.set_process(
                            is_running=True,
                            pid=proc.pid,
                            process_obj=proc,
                            model_name=model["name"],
                            model_path=model["path"],
                            mode=run_mode,
                            log_file=""
                        )
            elif key in ('q', 'Q'):
                running = False
        
        # Cleanup: stop any running process
        state = state_mgr.state
        if state.is_running:
            proc = state.process_obj
            if proc:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except:
                    proc.kill()
            state_mgr.clear_process()
        
        # Set TUI status to offline
        state_mgr.set_tui_status(False)
        
        clear_screen()
        print(f"\n  {C_green}✓ Goodbye!{C_RESET}\n")
    except Exception as e:
        print(f"\n  {C_red}✗ Error: {e}{C_RESET}\n")
        # Cleanup before exiting
        try:
            state = state_mgr.state
            if state.is_running:
                proc = state.process_obj
                if proc:
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                    except:
                        proc.kill()
                state_mgr.clear_process()
            # Set TUI status to offline
            state_mgr.set_tui_status(False)
        except:
            pass
        finally:
            clear_screen()
            print(f"\n  {C_red}✗ Application exited with error{C_RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\n  {C_red}✗ Fatal error: {e}{C_RESET}\n")
