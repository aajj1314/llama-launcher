#!/usr/bin/env python3
"""
Llama Launcher - Unified Launcher Script
Supports running TUI, WebUI, or both simultaneously
"""

import sys
import os
import argparse
import threading
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_webui_thread():
    """Start WebUI in a background thread"""
    import web_app
    web_app.start_web_server(host=web_app.WEB_HOST, port=web_app.WEB_PORT)

def start_tui():
    """Start TUI in the main thread"""
    import run
    run.main()

def main():
    parser = argparse.ArgumentParser(
        description="Llama Launcher - TUI and WebUI Management"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["tui", "web", "both"],
        default="both",
        help="Launch mode: tui (terminal UI), web (web UI), both (default)"
    )
    parser.add_argument(
        "--web-port", "-p",
        type=int,
        default=8087,
        help="Web server port (default: 80...)"
    )
    parser.add_argument(
        "--web-host",
        type=str,
        default="0.0.0.0",
        help="Web server host (default: 0.0.0.0)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  Llama Launcher v3.1 - Starting...")
    print("=" * 60)
    print(f"  Mode: {args.mode.upper()}")
    print(f"  Web UI: {args.web_host}:{args.web_port}")
    print("=" * 60)
    
    if args.mode == "web":
        # Start only WebUI
        print("\n  Starting WebUI...")
        import web_app
        web_app.start_web_server(host=args.web_host, port=args.web_port)
        
    elif args.mode == "tui":
        # Start only TUI
        print("\n  Starting TUI...")
        start_tui()
        
    elif args.mode == "both":
        # Start both: WebUI in background thread, TUI in main thread
        print("\n  Starting WebUI in background thread...")
        print("  Starting TUI in main thread...")
        print("\n  Press Ctrl+C to exit\n")
        
        # Modify web_app port before starting
        import web_app
        web_app.WEB_PORT = args.web_port
        web_app.WEB_HOST = args.web_host
        
        # Start WebUI in background thread
        web_thread = threading.Thread(
            target=start_webui_thread,
            daemon=True,
            name="WebUI-Thread"
        )
        web_thread.start()
        
        # Give WebUI time to start
        time.sleep(1)
        
        # Start TUI in main thread
        try:
            start_tui()
        except KeyboardInterrupt:
            print("\n\n  Shutting down...")
            print("  Goodbye!")
    
    print("\n  Exiting...")

if __name__ == "__main__":
    main()