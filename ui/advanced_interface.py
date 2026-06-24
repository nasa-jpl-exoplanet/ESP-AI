"""
Advanced interface for EXCALIBUR data filtering with natural language.
Replaces the traditional filter dropdowns with a natural language query system.
"""

import gradio as gr
import pandas as pd
from typing import List, Dict, Any, Tuple

from ai.query_translator import generate_code, execute_query
from data.load_excalibur_data import load_excalibur_data

EXCALIBUR_OUTPUT_PATH = "/Users/enguyen/ESP-AI"

def _get_sample_data_with_more_rows():
    """Return expanded sample EXCALIBUR data for better demonstration"""
    return {
        "rows": [
            # HST observations
            {"run_id": 1, "target": "55 Cnc", "task": "transit", "alg": "whitelight", "sv": "HST-WFC3-IR-G141-SCAN"},
            {"run_id": 1, "target": "GJ 436", "task": "transit", "alg": "whitelight", "sv": "HST-WFC3-IR-G141-SCAN"},
            {"run_id": 1, "target": "GJ 1132", "task": "transit", "alg": "whitelight", "sv": "HST-WFC3-IR-G141-SCAN"},
            {"run_id": 1, "target": "GJ 3053", "task": "transit", "alg": "whitelight", "sv": "HST-WFC3-IR-G141-SCAN"},
            {"run_id": 1, "target": "GJ 3470", "task": "transit", "alg": "whitelight", "sv": "HST-WFC3-IR-G141-SCAN"},
            {"run_id": 1, "target": "GJ 9827", "task": "transit", "alg": "whitelight", "sv": "HST-WFC3-IR-G141-SCAN"},
            {"run_id": 1, "target": "HAT-P-3", "task": "transit", "alg": "whitelight", "sv": "HST-WFC3-IR-G141-SCAN"},
            {"run_id": 1, "target": "HAT-P-11", "task": "transit", "alg": "whitelight", "sv": "HST-WFC3-IR-G141-SCAN"},
            {"run_id": 1, "target": "HAT-P-11", "task": "transit", "alg": "whitelight", "sv": "HST-WFC3-IR-G102-SCAN"},
            {"run_id": 2, "target": "WASP-12b", "task": "transit", "alg": "spectrum", "sv": "HST-WFC3-IR-G141-SCAN"},
            {"run_id": 2, "target": "WASP-12b", "task": "eclipse", "alg": "whitelight", "sv": "HST-WFC3-IR-G141-SCAN"},
            {"run_id": 3, "target": "GJ 436", "task": "eclipse", "alg": "whitelight", "sv": "HST-WFC3-IR-G141-SCAN"},
            {"run_id": 3, "target": "GJ 436", "task": "phasecurve", "alg": "whitelight", "sv": "HST-WFC3-IR-G141-SCAN"},
            {"run_id": 4, "target": "55 Cnc", "task": "eclipse", "alg": "spectrum", "sv": "HST-WFC3-IR-G141-SCAN"},
            
            # JWST observations
            {"run_id": 5, "target": "WASP-12b", "task": "transit", "alg": "whitelight", "sv": "JWST-NIRSpec-G395H"},
            {"run_id": 5, "target": "WASP-12b", "task": "transit", "alg": "spectrum", "sv": "JWST-NIRSpec-G395H"},
            {"run_id": 6, "target": "GJ 436", "task": "transit", "alg": "whitelight", "sv": "JWST-NIRSpec-G235H"},
            {"run_id": 6, "target": "GJ 436", "task": "eclipse", "alg": "whitelight", "sv": "JWST-NIRSpec-G235H"},
            {"run_id": 7, "target": "55 Cnc", "task": "transit", "alg": "whitelight", "sv": "JWST-NIRCam-F444W"},
            {"run_id": 7, "target": "55 Cnc", "task": "phasecurve", "alg": "whitelight", "sv": "JWST-NIRCam-F444W"},
            {"run_id": 8, "target": "HAT-P-11", "task": "eclipse", "alg": "whitelight", "sv": "JWST-NIRSpec-G395H"},
            {"run_id": 8, "target": "HAT-P-11", "task": "eclipse", "alg": "spectrum", "sv": "JWST-NIRSpec-G395H"},
        ],
        "calibration": {},
        "timing": {},
        "collect": {},
        "_metadata": {"source": "sample_data"}
    }

def query_and_filter(query: str, data: Dict[str, Any]) -> Tuple[List[Dict], str]:
    """
    Execute a natural language query and return filtered rows + generated code
    """
    try:
        # Generate code from natural language
        raw_code = generate_code(query)
        print(f"DEBUG - Raw generated code:\n{repr(raw_code)}\n")
        
        # Execute the query
        result = execute_query(raw_code, data)
        
        # Use the fixed code for display
        code = raw_code
        
        # Convert result to list of dicts if it's a list of rows
        if isinstance(result, list):
            rows = result
        elif isinstance(result, dict):
            rows = [result]
        else:
            rows = []
        
        return rows, code
    
    except Exception as e:
        error_msg = str(e)
        print(f"DEBUG - Error: {error_msg}")
        return [], f"Error: {error_msg}"

def format_results_table(rows: List[Dict], page: int = 0, page_size: int = 100) -> str:
    """Convert rows to HTML table for display with pagination"""
    if not rows:
        return "<p>No results</p>"
    
    # Calculate pagination
    start_idx = page * page_size
    end_idx = start_idx + page_size
    page_rows = rows[start_idx:end_idx]
    
    # Build HTML table
    html = '<table style="border-collapse: collapse; width: 100%;">'
    html += '<tr style="background-color: #f0f0f0;">'
    html += '<th style="border: 1px solid #ddd; padding: 8px;">Run ID</th>'
    html += '<th style="border: 1px solid #ddd; padding: 8px;">Target</th>'
    html += '<th style="border: 1px solid #ddd; padding: 8px;">Task</th>'
    html += '<th style="border: 1px solid #ddd; padding: 8px;">Alg</th>'
    html += '<th style="border: 1px solid #ddd; padding: 8px;">SV</th>'
    html += '</tr>'
    
    for row in page_rows:
        html += '<tr>'
        html += f'<td style="border: 1px solid #ddd; padding: 8px;">{row.get("run_id", "")}</td>'
        html += f'<td style="border: 1px solid #ddd; padding: 8px;">{row.get("target", "")}</td>'
        html += f'<td style="border: 1px solid #ddd; padding: 8px;">{row.get("task", "")}</td>'
        html += f'<td style="border: 1px solid #ddd; padding: 8px;">{row.get("alg", "")}</td>'
        html += f'<td style="border: 1px solid #ddd; padding: 8px;">{row.get("sv", "")}</td>'
        html += '</tr>'
    
    html += '</table>'
    return html

def create_advanced_interface():
    """Create the advanced filtering interface"""
    
    # Load data once
    data = load_excalibur_data(EXCALIBUR_OUTPUT_PATH)
    if not any(v for k, v in data.items() if k != "_metadata"):
        data = _get_sample_data_with_more_rows()
    
    # Store current results and page
    current_results = {"rows": [], "page": 0, "page_size": 100}
    
    def process_query(query_text):
        """Process user query and return results"""
        rows, code = query_and_filter(query_text, data)
        
        # Store results and reset to page 0
        current_results["rows"] = rows
        current_results["page"] = 0
        
        html_table = format_results_table(rows, page=0, page_size=current_results["page_size"])
        
        # Format summary with pagination info
        total = len(rows)
        page_size = current_results["page_size"]
        showing_end = min(page_size, total)
        summary = f"**Total: {total} results** | Showing 1-{showing_end}"
        
        # Enable/disable pagination buttons
        prev_enabled = False
        next_enabled = total > page_size
        
        return html_table, code, summary, gr.update(interactive=prev_enabled), gr.update(interactive=next_enabled)
    
    def next_page():
        """Go to next page"""
        current_results["page"] += 1
        page = current_results["page"]
        rows = current_results["rows"]
        page_size = current_results["page_size"]
        
        html_table = format_results_table(rows, page=page, page_size=page_size)
        
        # Update summary
        total = len(rows)
        start = page * page_size + 1
        end = min((page + 1) * page_size, total)
        summary = f"**Total: {total} results** | Showing {start}-{end}"
        
        # Enable/disable buttons
        prev_enabled = page > 0
        next_enabled = end < total
        
        return html_table, summary, gr.update(interactive=prev_enabled), gr.update(interactive=next_enabled)
    
    def prev_page():
        """Go to previous page"""
        current_results["page"] = max(0, current_results["page"] - 1)
        page = current_results["page"]
        rows = current_results["rows"]
        page_size = current_results["page_size"]
        
        html_table = format_results_table(rows, page=page, page_size=page_size)
        
        # Update summary
        total = len(rows)
        start = page * page_size + 1
        end = min((page + 1) * page_size, total)
        summary = f"**Total: {total} results** | Showing {start}-{end}"
        
        # Enable/disable buttons
        prev_enabled = page > 0
        next_enabled = end < total
        
        return html_table, summary, gr.update(interactive=prev_enabled), gr.update(interactive=next_enabled)
    
    with gr.Blocks(title="EXCALIBUR Data Query Assistant") as demo:
        gr.Markdown("# EXCALIBUR Data Query Assistant")
        gr.Markdown("Ask questions in natural language to filter EXCALIBUR data. Example: 'All transit whitelight runs' or 'Show me eclipse observations for GJ 436'")
        
        with gr.Row():
            query_input = gr.Textbox(
                label="Query",
                placeholder="e.g., 'All transit whitelight runs' or 'Eclipse observations for WASP-12b'",
                scale=4
            )
            search_btn = gr.Button("Search", scale=1)
        
        # Results section
        summary_text = gr.Markdown("**Total: 0**")
        
        # Pagination controls
        with gr.Row():
            prev_btn = gr.Button("← Previous", scale=1, interactive=False)
            next_btn = gr.Button("Next →", scale=1, interactive=False)
        
        results_table = gr.HTML(
            value="<p>No results yet</p>"
        )
        
        # Generated code section
        with gr.Accordion("Generated Python Code", open=False):
            code_output = gr.Code(
                label="Code",
                language="python"
            )
        
        # Example queries
        gr.Markdown("### Example Queries")
        example_queries = [
            "All transit whitelight runs",
            "Eclipse observations for GJ 436",
            "All spectrum runs",
            "Observations with HST-WFC3-IR-G141-SCAN",
            "Count of transit vs eclipse observations",
        ]
        
        with gr.Row():
            for example in example_queries:
                btn = gr.Button(example, size="sm")
                btn.click(
                    fn=lambda q=example: process_query(q),
                    outputs=[results_table, code_output, summary_text, prev_btn, next_btn]
                )
        
        # Connect search button and enter key
        search_btn.click(
            fn=process_query,
            inputs=query_input,
            outputs=[results_table, code_output, summary_text, prev_btn, next_btn]
        )
        
        query_input.submit(
            fn=process_query,
            inputs=query_input,
            outputs=[results_table, code_output, summary_text, prev_btn, next_btn]
        )
        
        # Connect pagination buttons
        next_btn.click(
            fn=next_page,
            outputs=[results_table, summary_text, prev_btn, next_btn]
        )
        
        prev_btn.click(
            fn=prev_page,
            outputs=[results_table, summary_text, prev_btn, next_btn]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_advanced_interface()
    demo.launch()
