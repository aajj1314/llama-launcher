#!/usr/bin/env python3
"""
Test script for performance testing
"""

import os
import time
import psutil
from state_manager import get_state_manager, scan_models


def test_startup_time():
    """Test startup time"""
    print("Testing startup time...")
    
    start_time = time.time()
    
    # Initialize state manager
    state_mgr = get_state_manager()
    
    # Scan models
    models = scan_models()
    
    end_time = time.time()
    startup_time = end_time - start_time
    
    print(f"Startup time: {startup_time:.3f} seconds")
    print(f"Scanned {len(models)} models")
    
    if startup_time <= 3:
        print("✓ Startup time meets requirement (≤ 3 seconds)")
    else:
        print("✗ Startup time exceeds requirement (> 3 seconds)")
    
    return startup_time


def test_memory_usage():
    """Test memory usage"""
    print("\nTesting memory usage...")
    
    # Get current process
    process = psutil.Process(os.getpid())
    
    # Initialize state manager
    state_mgr = get_state_manager()
    
    # Scan models
    models = scan_models()
    
    # Get memory usage
    memory_info = process.memory_info()
    memory_usage_mb = memory_info.rss / (1024 * 1024)
    
    print(f"Memory usage: {memory_usage_mb:.2f} MB")
    
    if memory_usage_mb <= 500:
        print("✓ Memory usage meets requirement (≤ 500 MB)")
    else:
        print("✗ Memory usage exceeds requirement (> 500 MB)")
    
    return memory_usage_mb


def test_model_scan_performance():
    """Test model scan performance"""
    print("\nTesting model scan performance...")
    
    start_time = time.time()
    
    # Scan models multiple times to get average time
    scan_times = []
    for i in range(5):
        start_scan = time.time()
        models = scan_models()
        end_scan = time.time()
        scan_time = end_scan - start_scan
        scan_times.append(scan_time)
        print(f"Scan {i+1}: {scan_time:.3f} seconds")
    
    average_scan_time = sum(scan_times) / len(scan_times)
    print(f"Average scan time: {average_scan_time:.3f} seconds")
    
    if average_scan_time <= 0.5:
        print("✓ Model scan performance meets requirement (≤ 0.5 seconds)")
    else:
        print("✗ Model scan performance exceeds requirement (> 0.5 seconds)")
    
    return average_scan_time


def test_path_update_performance():
    """Test path update performance"""
    print("\nTesting path update performance...")
    
    # Get state manager instance
    state_mgr = get_state_manager()
    
    # Save original path
    original_path = state_mgr.get_paths()["llama_cpp_path"]
    
    try:
        # Test path update
        start_time = time.time()
        
        # Update to a temporary path
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = state_mgr.set_llama_cpp_path(temp_dir)
            update_time = time.time() - start_time
            
            print(f"Path update time: {update_time:.3f} seconds")
            
            if update_time <= 0.5:
                print("✓ Path update performance meets requirement (≤ 0.5 seconds)")
            else:
                print("✗ Path update performance exceeds requirement (> 0.5 seconds)")
    finally:
        # Reset to original path
        state_mgr.set_llama_cpp_path(original_path)
    
    return update_time


if __name__ == "__main__":
    print("Starting performance tests...\n")
    
    startup_time = test_startup_time()
    memory_usage = test_memory_usage()
    scan_performance = test_model_scan_performance()
    path_update_performance = test_path_update_performance()
    
    print("\n=== Performance Test Results ===")
    print(f"Startup time: {startup_time:.3f} seconds")
    print(f"Memory usage: {memory_usage:.2f} MB")
    print(f"Average model scan time: {scan_performance:.3f} seconds")
    print(f"Path update time: {path_update_performance:.3f} seconds")
    
    # Check if all requirements are met
    all_passed = (
        startup_time <= 3 and
        memory_usage <= 500 and
        scan_performance <= 0.5 and
        path_update_performance <= 0.5
    )
    
    if all_passed:
        print("\n✓ All performance requirements met!")
    else:
        print("\n✗ Some performance requirements not met!")
    
    print("\n✓ Performance tests completed!")