#!/usr/bin/env python3
"""
Test script for llama.cpp path configuration
"""

import os
import tempfile
import shutil
from state_manager import get_state_manager, scan_models


def test_path_config():
    """Test llama.cpp path configuration"""
    print("Testing llama.cpp path configuration...")
    
    # Get state manager instance
    state_mgr = get_state_manager()
    
    # Save original path
    original_path = state_mgr.get_paths()["llama_cpp_path"]
    print(f"Original path: {original_path}")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create necessary subdirectories
        os.makedirs(os.path.join(temp_dir, "models"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "build", "bin"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "logs"), exist_ok=True)
        
        # Test setting new path
        print(f"Setting new path: {temp_dir}")
        paths = state_mgr.set_llama_cpp_path(temp_dir)
        
        # Verify path was updated
        new_paths = state_mgr.get_paths()
        print(f"New path: {new_paths['llama_cpp_path']}")
        
        if new_paths['llama_cpp_path'] == temp_dir:
            print("✓ Path updated successfully")
        else:
            print("✗ Path update failed")
            return False
        
        # Test model scanning with new path
        models = scan_models()
        print(f"Scanned {len(models)} models in new path")
        
        # Test resetting to original path
        print(f"Resetting to original path: {original_path}")
        state_mgr.set_llama_cpp_path(original_path)
        
        # Verify path was reset
        reset_paths = state_mgr.get_paths()
        print(f"Reset path: {reset_paths['llama_cpp_path']}")
        
        if reset_paths['llama_cpp_path'] == original_path:
            print("✓ Path reset successfully")
        else:
            print("✗ Path reset failed")
            return False
    
    print("✓ All path configuration tests passed!")
    return True


if __name__ == "__main__":
    test_path_config()