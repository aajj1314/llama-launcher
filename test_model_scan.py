#!/usr/bin/env python3
import time
from state_manager import scan_models

start = time.time()
models = scan_models()
end = time.time()
print(f"Scanned {len(models)} models in {end - start:.4f} seconds")
for model in models[:3]:
    print(f"  - {model['name']} ({model['size_formatted']})")
