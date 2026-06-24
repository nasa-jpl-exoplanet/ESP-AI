#!/usr/bin/env python3
"""
Extract EXCALIBUR run metadata from Dawgie PostgreSQL backup file.
Creates a JSON file with all run information for the natural language query system.
"""

import re
import json

def parse_copy_data(backup_file, table_name):
    """Extract data from COPY statements in PostgreSQL backup"""
    data = []
    in_copy = False
    
    with open(backup_file, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            
            # Start of COPY block
            if line.startswith(f'COPY public.{table_name}'):
                in_copy = True
                continue
            
            # End of COPY block
            if in_copy and line == '\\.':
                in_copy = False
                continue
            
            # Parse data lines
            if in_copy and line.strip():
                # Split by tab (PostgreSQL COPY format)
                fields = line.split('\t')
                data.append(fields)
    
    return data

def main():
    backup_file = '/Users/enguyen/ESP-AI/ops.00.sql'
    output_file = '/Users/enguyen/ESP-AI/excalibur_runs.json'
    
    print("Extracting EXCALIBUR data from Dawgie backup...")
    print(f"Input: {backup_file}")
    print(f"Output: {output_file}\n")
    
    # Extract all tables
    print("Extracting tables...")
    targets = parse_copy_data(backup_file, 'target')
    tasks = parse_copy_data(backup_file, 'task')
    algorithms = parse_copy_data(backup_file, 'algorithm')
    statevectors = parse_copy_data(backup_file, 'statevector')
    values = parse_copy_data(backup_file, 'value')
    primes = parse_copy_data(backup_file, 'prime')
    
    print(f"  Targets: {len(targets)}")
    print(f"  Tasks: {len(tasks)}")
    print(f"  Algorithms: {len(algorithms)}")
    print(f"  State Vectors: {len(statevectors)}")
    print(f"  Values: {len(values)}")
    print(f"  Prime entries: {len(primes)}")
    
    # Build lookup dictionaries
    target_map = {row[0]: row[1] for row in targets}
    task_map = {row[0]: row[1] for row in tasks}
    alg_map = {row[0]: row[1] for row in algorithms}
    sv_map = {row[0]: row[1] for row in statevectors}
    value_map = {row[0]: row[1] for row in values}
    
    # Build rows from prime table
    print("\nBuilding run metadata...")
    rows = []
    
    for prime in primes:
        if len(prime) < 7:
            continue
            
        pk, run_id, task_id, tn_id, alg_id, sv_id, val_id = prime[:7]
        blob_name = prime[7] if len(prime) > 7 else None
        
        row = {
            "run_id": int(run_id) if run_id else None,
            "target": target_map.get(tn_id, ""),
            "task": task_map.get(task_id, ""),
            "alg": alg_map.get(alg_id, ""),
            "sv": sv_map.get(sv_id, ""),
            "value": value_map.get(val_id, ""),
            "blob_name": blob_name
        }
        rows.append(row)
    
    # Create output data structure
    data = {
        "rows": rows,
        "calibration": {},
        "timing": {},
        "collect": {},
        "_metadata": {
            "source": "dawgie_backup",
            "backup_file": backup_file,
            "total_runs": len(rows)
        }
    }
    
    # Save to JSON
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nExtracted {len(rows)} runs")
    print(f"Saved to: {output_file}")
    
    # Show sample
    print("\nSample rows:")
    for row in rows[:5]:
        blob = f" (blob: {row['blob_name']})" if row.get('blob_name') else ""
        print(f"  Run {row['run_id']}: {row['target']} - {row['task']}/{row['alg']} - {row['sv']}{blob}")

if __name__ == "__main__":
    main()
