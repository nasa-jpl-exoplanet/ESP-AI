# data/load_excalibur_data.py

import json
import os
import glob
import pickle
from pathlib import Path

def latest_json(path, pattern):
    """Find latest JSON file matching pattern"""
    files = sorted(
        glob.glob(os.path.join(path, "**", pattern), recursive=True),
        key=os.path.getmtime
    )
    return files[-1] if files else None

def load_json(path):
    """Load JSON file safely"""
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def load_pickle(path):
    """Load pickle file safely"""
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception:
        return {}

def discover_excalibur_data(base_path):
    """
    Discover EXCALIBUR data from Dawgie database structure.
    EXCALIBUR uses Dawgie which stores data in pickle files.
    """
    data = {
        "collect": {},
        "timing": {},
        "calibration": {},
        "rows": [],
        "_metadata": {
            "source": "excalibur_dawgie",
            "path": base_path,
        }
    }
    
    if not os.path.exists(base_path):
        return data
    
    # Look for Dawgie database structure
    # Typical structure: base_path/db/[task_name]/[version]/[target]/[alg]/
    db_path = os.path.join(base_path, "db")
    
    if os.path.exists(db_path):
        # Scan for task outputs
        for task_dir in os.listdir(db_path):
            task_path = os.path.join(db_path, task_dir)
            if not os.path.isdir(task_path):
                continue
            
            # data.collect, data.timing, data.calibration are key tasks
            if task_dir.startswith("data.collect"):
                data["collect"][task_dir] = _load_task_data(task_path)
            elif task_dir.startswith("data.timing"):
                data["timing"][task_dir] = _load_task_data(task_path)
            elif task_dir.startswith("data.calibration"):
                data["calibration"][task_dir] = _load_task_data(task_path)
    
    # Also check for JSON exports
    collect_json = latest_json(base_path, "data.collect*.json")
    if collect_json:
        data["collect"].update(load_json(collect_json))
    
    timing_json = latest_json(base_path, "data.timing*.json")
    if timing_json:
        data["timing"].update(load_json(timing_json))
    
    calibration_json = latest_json(base_path, "data.calibration*.json")
    if calibration_json:
        data["calibration"].update(load_json(calibration_json))
    
    rows_json = latest_json(base_path, "data.rows*.json")
    if rows_json:
        rows_data = load_json(rows_json)
        if isinstance(rows_data, list):
            data["rows"] = rows_data
        elif isinstance(rows_data, dict) and "rows" in rows_data:
            data["rows"] = rows_data["rows"]
    
    return data

def _load_task_data(task_path):
    """Load data from a Dawgie task directory"""
    task_data = {}
    
    try:
        for version_dir in os.listdir(task_path):
            version_path = os.path.join(task_path, version_dir)
            if not os.path.isdir(version_path):
                continue
            
            for target_dir in os.listdir(version_path):
                target_path = os.path.join(version_path, target_dir)
                if not os.path.isdir(target_path):
                    continue
                
                # Look for pickle files or data files
                for item in os.listdir(target_path):
                    if item.endswith(".pkl"):
                        pkl_path = os.path.join(target_path, item)
                        task_data[f"{target_dir}/{item}"] = load_pickle(pkl_path)
    except Exception:
        pass
    
    return task_data

def load_excalibur_data(base_path):
    """
    Load EXCALIBUR data from either:
    1. Dawgie database (preferred)
    2. JSON exports (fallback)
    """
    return discover_excalibur_data(base_path)