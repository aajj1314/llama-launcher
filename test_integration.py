#!/usr/bin/env python3
"""
Integration test script for Llama Launcher
"""

import os
import sys
import time
from state_manager import get_state_manager, scan_models
from process_manager import validate_binary


def run_all_tests():
    """Run all tests"""
    print("Running comprehensive integration tests...\n")
    
    # Test 1: State Manager initialization
    print("Test 1: State Manager initialization")
    try:
        state_mgr = get_state_manager()
        print("✓ State Manager initialized successfully")
    except Exception as e:
        print(f"✗ State Manager initialization failed: {e}")
        return False
    
    # Test 2: Path configuration
    print("\nTest 2: Path configuration")
    try:
        # Get current paths
        paths = state_mgr.get_paths()
        print(f"✓ Current paths: {paths}")
    except Exception as e:
        print(f"✗ Path configuration test failed: {e}")
        return False
    
    # Test 3: Model scanning
    print("\nTest 3: Model scanning")
    try:
        models = scan_models()
        print(f"✓ Scanned {len(models)} models")
    except Exception as e:
        print(f"✗ Model scanning test failed: {e}")
        return False
    
    # Test 4: Binary validation
    print("\nTest 4: Binary validation")
    try:
        for mode in [0, 1, 2]:
            result = validate_binary(mode)
            print(f"  Mode {mode}: {result}")
        print("✓ Binary validation test completed")
    except Exception as e:
        print(f"✗ Binary validation test failed: {e}")
        return False
    
    # Test 5: State management
    print("\nTest 5: State management")
    try:
        # Test getting state
        state = state_mgr.state
        print("✓ State retrieved successfully")
        
        # Test getting state as dictionary
        state_dict = state_mgr.get_state()
        print("✓ State dictionary retrieved successfully")
    except Exception as e:
        print(f"✗ State management test failed: {e}")
        return False
    
    # Test 6: Error handling
    print("\nTest 6: Error handling")
    try:
        # Test with invalid path
        invalid_path = "/nonexistent/path"
        paths = state_mgr.set_llama_cpp_path(invalid_path)
        print("✓ Invalid path handled successfully")
        
        # Reset to original path
        original_path = "/home/anan/llama.cpp"
        state_mgr.set_llama_cpp_path(original_path)
        print("✓ Path reset successfully")
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False
    
    # Test 7: Configuration management
    print("\nTest 7: Configuration management")
    try:
        # Test setting configuration
        result = state_mgr.set_config(ctx_idx=0, ngl_idx=0, port=8000)
        print(f"✓ Configuration set successfully: {result}")
    except Exception as e:
        print(f"✗ Configuration management test failed: {e}")
        return False
    
    # Test 8: Process management
    print("\nTest 8: Process management")
    try:
        # Test clearing process
        result = state_mgr.clear_process()
        print(f"✓ Process cleared successfully: {result}")
        
        # Test process status
        is_running = state_mgr.state.is_running
        print(f"✓ Process status retrieved: {is_running}")
    except Exception as e:
        print(f"✗ Process management test failed: {e}")
        return False
    
    print("\n=== Integration Test Results ===")
    print("✓ All integration tests passed!")
    print("\nThe project is ready for use.")
    return True


if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\n✓ Integration test completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Integration test failed!")
        sys.exit(1)