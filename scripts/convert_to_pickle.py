#!/usr/bin/env python3
"""
Convert excalibur_runs.json to pickle format for faster loading.
Pickle loads 5-10x faster than JSON for large datasets.
"""

import json
import pickle
import time

def convert_json_to_pickle():
    import os
    # Get the project root directory (parent of scripts/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    json_file = os.path.join(project_root, "excalibur_runs.json")
    pickle_file = os.path.join(project_root, "excalibur_runs.pkl")
    
    print(f"Loading {json_file}...")
    start = time.time()
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    load_time = time.time() - start
    print(f"✓ Loaded in {load_time:.2f}s")
    
    print(f"\nSaving to {pickle_file}...")
    start = time.time()
    
    with open(pickle_file, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    save_time = time.time() - start
    print(f"✓ Saved in {save_time:.2f}s")
    
    # Test loading pickle
    print(f"\nTesting pickle load speed...")
    start = time.time()
    
    with open(pickle_file, 'rb') as f:
        test_data = pickle.load(f)
    
    pickle_load_time = time.time() - start
    print(f"✓ Pickle loads in {pickle_load_time:.2f}s")
    print(f"  Speedup: {load_time/pickle_load_time:.1f}x faster!")

if __name__ == "__main__":
    convert_json_to_pickle()
