#!/usr/bin/env python3
from state_manager import scan_models

models = scan_models()
print(f"Found {len(models)} models")
for model in models[:3]:
    print(f"  - {model['name']} ({model['size_formatted']})")
