#!/usr/bin/env python3
"""
Test script for error handling
"""

import os
import tempfile
from state_manager import get_state_manager, scan_models
from process_manager import validate_binary, run_cli, run_server, run_embedding


def test_invalid_llama_cpp_path():
    """Test error handling for invalid llama.cpp path"""
    print("Testing invalid llama.cpp path...")
    
    # Get state manager instance
    state_mgr = get_state_manager()
    
    # Save original path
    original_path = state_mgr.get_paths()["llama_cpp_path"]
    
    try:
        # Test with non-existent path
        invalid_path = "/nonexistent/path/to/llama.cpp"
        print(f"Testing with invalid path: {invalid_path}")
        paths = state_mgr.set_llama_cpp_path(invalid_path)
        print(f"Path update result: {paths}")
        
        # Test model scanning with invalid path
        print("Testing model scanning with invalid path...")
        models = scan_models()
        print(f"Scanned {len(models)} models with invalid path")
        
        # Test validate_binary with invalid path
        print("Testing validate_binary with invalid path...")
        for mode in [0, 1, 2]:
            result = validate_binary(mode)
            print(f"Mode {mode}: {result}")
        
        print("✓ Invalid llama.cpp path test completed")
    finally:
        # Reset to original path
        state_mgr.set_llama_cpp_path(original_path)
        print(f"Reset to original path: {original_path}")


def test_invalid_model_path():
    """Test error handling for invalid model path"""
    print("\nTesting invalid model path...")
    
    # Test run_cli with invalid model path
    print("Testing run_cli with invalid model path...")
    proc = run_cli("/nonexistent/path/to/model.gguf", 4096, 0)
    print(f"run_cli result: {proc}")
    
    # Test run_server with invalid model path
    print("Testing run_server with invalid model path...")
    proc, log_file = run_server("/nonexistent/path/to/model.gguf", 4096, 0, 8000)
    print(f"run_server result: {proc}, log_file: {log_file}")
    
    # Test run_embedding with invalid model path
    print("Testing run_embedding with invalid model path...")
    proc = run_embedding("/nonexistent/path/to/model.gguf", 0)
    print(f"run_embedding result: {proc}")
    
    print("✓ Invalid model path test completed")


def test_boundary_cases():
    """Test error handling for boundary cases"""
    print("\nTesting boundary cases...")
    
    # Get state manager instance
    state_mgr = get_state_manager()
    
    # Test set_process with invalid values
    print("Testing set_process with invalid values...")
    result = state_mgr.set_process(True, "invalid_pid", "invalid_process")
    print(f"set_process with invalid values result: {result}")
    
    # Test set_config with invalid values
    print("Testing set_config with invalid values...")
    result = state_mgr.set_config(ctx_idx=-1, ngl_idx=-1, port=99999, timeout=-1, log_level="INVALID_LEVEL")
    print(f"set_config with invalid values result: {result}")
    
    # Test scan_models with None path
    print("Testing scan_models with None path...")
    models = scan_models(None)
    print(f"scan_models with None path result: {len(models)} models")
    
    # Test validate_binary with invalid mode
    print("Testing validate_binary with invalid mode...")
    result = validate_binary(999)
    print(f"validate_binary with invalid mode result: {result}")
    
    print("✓ Boundary cases test completed")


if __name__ == "__main__":
    test_invalid_llama_cpp_path()
    test_invalid_model_path()
    test_boundary_cases()
    print("\n✓ All error handling tests completed!")