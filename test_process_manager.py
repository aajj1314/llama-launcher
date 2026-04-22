#!/usr/bin/env python3
"""
Test script for process management
"""

import os
import tempfile
import time
from process_manager import validate_binary
from state_manager import get_state_manager


def test_validate_binary():
    """Test validate_binary function"""
    print("Testing validate_binary function...")
    
    # Test all modes
    for mode in [0, 1, 2]:
        result = validate_binary(mode)
        print(f"Mode {mode}: {result}")
    
    # Test invalid mode
    result = validate_binary(999)
    print(f"Invalid mode 999: {result}")
    
    print("✓ validate_binary test completed")


def test_process_management():
    """Test process management"""
    print("\nTesting process management...")
    
    # Get state manager instance
    state_mgr = get_state_manager()
    
    # Test clearing process
    print("Testing clear_process...")
    state_mgr.clear_process()
    print("✓ clear_process test completed")


def test_state_manager_process():
    """Test state manager process management"""
    print("\nTesting state manager process management...")
    
    # Get state manager instance
    state_mgr = get_state_manager()
    
    # Test getting process status
    print("Testing process status...")
    is_running = state_mgr.state.is_running
    print(f"Is process running: {is_running}")
    
    # Test getting process PID
    print("Testing process PID...")
    pid = state_mgr.state.process_pid
    print(f"Process PID: {pid}")
    
    print("✓ State manager process test completed")


if __name__ == "__main__":
    test_validate_binary()
    test_process_management()
    test_state_manager_process()
    print("\n✓ All process management tests completed!")