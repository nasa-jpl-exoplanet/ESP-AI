# Utility Scripts

This directory contains utility scripts for data processing and setup.

## Scripts

### `extract_excalibur_from_backup.py`
Extracts EXCALIBUR run metadata from Dawgie PostgreSQL backup files.

**Usage:**
```bash
python scripts/extract_excalibur_from_backup.py
```

**Input:** `ops.00.sql` or `ops.00.bck` (Dawgie database backup)  
**Output:** `excalibur_runs.json` (14M+ runs in JSON format)

**What it does:**
- Parses PostgreSQL COPY statements from backup
- Extracts 6 tables: target, task, algorithm, statevector, value, prime
- Joins data to create denormalized run records
- Outputs JSON with all run metadata

### `convert_to_pickle.py`
Converts JSON data to pickle format for faster loading (2x speedup).

**Usage:**
```bash
python scripts/convert_to_pickle.py
```

**Input:** `excalibur_runs.json`  
**Output:** `excalibur_runs.pkl`

**Performance:**
- JSON loading: ~33 seconds
- Pickle loading: ~18 seconds
- **Speedup: 1.9x faster**

The data loader automatically uses `.pkl` if available, falling back to `.json`.
