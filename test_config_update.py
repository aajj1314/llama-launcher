#!/usr/bin/env python3
"""
Test script to verify config update functionality
"""

import requests
import json

BASE_URL = "http://localhost:8087"

def test_config_update():
    """Test config update functionality"""
    print("Testing config update functionality...")
    
    # Get current state
    print("\n1. Getting current state...")
    response = requests.get(f"{BASE_URL}/api/state")
    if response.status_code == 200:
        current_state = response.json()
        print(f"Current state: {json.dumps(current_state, indent=2)}")
    else:
        print(f"Failed to get state: {response.status_code}")
        return
    
    # Test 1: Update port
    print("\n2. Testing port update...")
    new_port = 8088 if current_state.get('port') != 8088 else 8089
    payload = {
        "port": new_port
    }
    response = requests.post(f"{BASE_URL}/api/config", json=payload)
    if response.status_code == 200:
        result = response.json()
        print(f"Update result: {json.dumps(result, indent=2)}")
        if result.get('success'):
            print(f"✓ Port updated to {new_port}")
        else:
            print(f"✗ Port update failed: {result.get('error')}")
    else:
        print(f"Failed to update port: {response.status_code}")
    
    # Test 2: Update running mode
    print("\n3. Testing running mode update...")
    current_mode = current_state.get('current_mode', 1)
    new_mode = (current_mode + 1) % 3
    payload = {
        "mode": new_mode
    }
    response = requests.post(f"{BASE_URL}/api/config", json=payload)
    if response.status_code == 200:
        result = response.json()
        print(f"Update result: {json.dumps(result, indent=2)}")
        if result.get('success'):
            print(f"✓ Running mode updated to {new_mode}")
        else:
            print(f"✗ Running mode update failed: {result.get('error')}")
    else:
        print(f"Failed to update running mode: {response.status_code}")
    
    # Test 3: Update multiple parameters
    print("\n4. Testing multiple parameter update...")
    payload = {
        "ctx_idx": 1,
        "ngl_idx": 1,
        "timeout": 60,
        "log_level": "DEBUG"
    }
    response = requests.post(f"{BASE_URL}/api/config", json=payload)
    if response.status_code == 200:
        result = response.json()
        print(f"Update result: {json.dumps(result, indent=2)}")
        if result.get('success'):
            print("✓ Multiple parameters updated successfully")
        else:
            print(f"✗ Multiple parameters update failed: {result.get('error')}")
    else:
        print(f"Failed to update multiple parameters: {response.status_code}")
    
    # Get final state
    print("\n5. Getting final state...")
    response = requests.get(f"{BASE_URL}/api/state")
    if response.status_code == 200:
        final_state = response.json()
        print(f"Final state: {json.dumps(final_state, indent=2)}")
    else:
        print(f"Failed to get final state: {response.status_code}")

if __name__ == "__main__":
    test_config_update()
