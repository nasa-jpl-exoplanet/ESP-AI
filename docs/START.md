# Start Here

## Quick Start

```bash
python main_advanced.py
```

Then visit: `http://127.0.0.1:7860`

## What You Get

A natural language query processor that replaces filter dropdowns.

Type queries like:
- "All transit whitelight runs"
- "Eclipse observations for GJ 436"
- "All spectrum runs"

Results display in a table with: Run ID, Target, Task, Alg, SV

## File Structure

```
ESP-AI/
├── main_advanced.py              # Entry point
├── requirements.txt              # Dependencies
├── README.md                      # Documentation
├── ai/
│   ├── query_translator.py       # Code generation & execution
│   └── prompts.py                # LLM system prompt
├── data/
│   └── load_excalibur_data.py    # Data loading
└── ui/
    └── advanced_interface.py     # Web interface
```

