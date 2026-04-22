#!/usr/bin/env python3
"""
Llama Launcher v4.0 - 用户友好版
主入口文件
"""

import argparse
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web import start_web_server
from config import get_config


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Llama Launcher v4.0 - 用户友好的 llama.cpp 模型启动器"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Web服务器监听地址 (默认: 从配置读取)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Web服务器监听端口 (默认: 从配置读取)"
    )
    
    args = parser.parse_args()
    
    # 获取配置
    config = get_config()
    
    host = args.host or config.web_host
    port = args.port or config.web_port
    
    print("=" * 60)
    print("🤖 Llama Launcher v4.0 - 用户友好版")
    print("=" * 60)
    print(f"Web服务将在 http://{host}:{port} 启动")
    print("请在浏览器中打开这个地址")
    print("=" * 60)
    print()
    
    # 启动Web服务器
    try:
        start_web_server(host=host, port=port)
    except KeyboardInterrupt:
        print("\n正在停止...")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
