#!/usr/bin/env python3
"""
Llama.cpp Model Launcher (Python) - Cyberpunk Edition
"""

import os
import sys
import subprocess
import time
import signal
import re
import threading
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

LLAMA_CPP_PATH = "/home/anan/llama.cpp"
MODELS_PATH = os.path.join(LLAMA_CPP_PATH, "models")
BUILD_BIN_PATH = os.path.join(LLAMA_CPP_PATH, "build", "bin")
LOG_DIR = os.path.join(LLAMA_CPP_PATH, "logs")

LARGE_MODEL_THRESHOLD = 1024 * 1024 * 1024

CTX_SIZE_OPTIONS = [4096, 8192, 16384, 32768, 65536, 131072]
NGL_OPTIONS = [0, 33, 66, 99, 999]

SERVERMetrics = Tuple[float, int, int, int]

@dataclass
class ServerStats:
    prompt_tokens: int = 0
    eval_tokens: int = 0
    prompt_per_second: float = 0.0
    eval_per_second: float = 0.0
    ctx_used: int = 0
    ctx_total: int = 0
    total_time: float = 0.0

    def is_valid(self) -> bool:
        return self.eval_tokens > 0 or self.prompt_tokens > 0


def format_size(size: int) -> str:
    if size >= 1024 ** 3:
        return f"{size / (1024 ** 3):.2f} GB"
    elif size >= 1024 ** 2:
        return f"{size / (1024 ** 2):.2f} MB"
    elif size >= 1024:
        return f"{size / 1024:.2f} KB"
    return f"{size} B"

def format_ctx(ctx: int) -> str:
    if ctx >= 1024:
        return f"{ctx // 1024}k"
    return str(ctx)

def format_speed(speed: float) -> str:
    if speed >= 1000:
        return f"{speed:.0f}"
    elif speed >= 1:
        return f"{speed:.1f}"
    return f"{speed:.2f}"

def scan_large_models() -> List[Dict[str, Any]]:
    models = []
    try:
        for entry in os.listdir(MODELS_PATH):
            entry_path = os.path.join(MODELS_PATH, entry)
            if os.path.isfile(entry_path) and entry.endswith(".gguf"):
                stat_info = os.stat(entry_path)
                if stat_info.st_size > LARGE_MODEL_THRESHOLD:
                    models.append({
                        "name": entry,
                        "path": entry_path,
                        "size": stat_info.st_size
                    })
    except Exception as e:
        print(f"Error scanning models: {e}", file=sys.stderr)
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

def main():
    running = True
    selected_idx = 0
    run_mode = 0
    ctx_idx = 0
    ngl_idx = 4
    port = 8080
    current_process: Optional[subprocess.Popen] = None
    current_log_file: str = ""
    current_mode = 0
    current_model_name = ""
    server_stats = ServerStats()
    last_update_time = 0

    models = scan_large_models()
    print_header()
    print(f"  {C_green}✓ Initializing Llama.cpp Launcher v3.0 (Cyberpunk Edition)...{C_RESET}")
    print(f"  {C_green}✓ Found {len(models)} models{C_RESET}")
    time.sleep(0.5)

    while running:
        current_time = time.time()
        if current_process and current_process.poll() is None and current_log_file:
            if current_time - last_update_time > 0.5:
                server_stats = parse_server_log(current_log_file)
                last_update_time = current_time

        print_header()
        print_models(models, selected_idx)
        print_settings(run_mode, ctx_idx, ngl_idx, port)
        print_stats(server_stats, current_process, port)
        print_controls()
        print_footer()
        print(f"\n\033[1;38;5;51m> \033[0m", end="", flush=True)

        if current_process and current_process.poll() is not None:
            current_process = None
            current_log_file = ""

        try:
            key = get_key()
        except:
            key = 'q'

        if key in ('UP', 'w', 'W', '4'):
            if selected_idx > 0:
                selected_idx -= 1
        elif key in ('DOWN', 's', 'S', '5'):
            if selected_idx < len(models) - 1:
                selected_idx += 1
        elif key == '1':
            run_mode = 0
        elif key == '2':
            run_mode = 1
        elif key == '3':
            run_mode = 2
        elif key in ('c', 'C'):
            ctx_idx = (ctx_idx + 1) % len(CTX_SIZE_OPTIONS)
        elif key in ('g', 'G'):
            ngl_idx = (ngl_idx + 1) % len(NGL_OPTIONS)
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
                        port = new_port
                    else:
                        print(f"\n  {C_red}✗ Port must be between 1 and 65535{C_RESET}")
                        time.sleep(1)
                except ValueError:
                    print(f"\n  {C_red}✗ Invalid port number: {port_input}{C_RESET}")
                    time.sleep(1)
        elif key in ('r', 'R'):
            models = scan_large_models()
            if selected_idx >= len(models):
                selected_idx = max(0, len(models) - 1)
            print(f"\n  {C_green}✓ Refreshed! Found {len(models)} models{C_RESET}")
            time.sleep(0.5)
        elif key in ('k', 'K'):
            if current_process:
                terminate_process(current_process)
                current_process = None
                current_log_file = ""
                current_model_name = ""
                server_stats = ServerStats()
        elif key in ('\r', '\n'):
            if models and 0 <= selected_idx < len(models):
                model = models[selected_idx]
                current_model_name = model["name"]
                current_mode = run_mode
                server_stats = ServerStats()
                if current_process:
                    terminate_process(current_process)
                if run_mode == 0:
                    current_process = run_cli(model["path"], CTX_SIZE_OPTIONS[ctx_idx], NGL_OPTIONS[ngl_idx])
                    current_log_file = ""
                elif run_mode == 1:
                    result = run_server(model["path"], CTX_SIZE_OPTIONS[ctx_idx], NGL_OPTIONS[ngl_idx], port)
                    current_process, current_log_file = result
                elif run_mode == 2:
                    current_process = run_embedding(model["path"], NGL_OPTIONS[ngl_idx])
                    current_log_file = ""
        elif key in ('q', 'Q'):
            running = False

    if current_process:
        terminate_process(current_process)

    clear_screen()
    print(f"\n  {C_green}✓ Goodbye!{C_RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
