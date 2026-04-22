#!/usr/bin/env python3
"""
Shared utility functions for llama-launcher
"""

import re
import subprocess
from typing import Optional
from state_manager import ServerStats

def parse_server_log(log_file: str) -> ServerStats:
    """Parse server log to extract metrics"""
    stats = ServerStats()
    if not log_file:
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
    except Exception as e:
        from state_manager import logger
        logger.error(f"Error parsing server log: {e}")
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
        from state_manager import logger
        logger.error(f"Error terminating process: {e}")
        return False