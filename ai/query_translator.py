import ollama
import ast
import re

from ai.prompts import SYSTEM_PROMPT

def is_safe_expression(code):
    """Validate that code is a safe expression (no imports, function defs, etc.)"""
    try:
        # Try parsing as expression first (safest)
        tree = ast.parse(code, mode='eval')
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, 
                               ast.AsyncFunctionDef, ast.ClassDef)):
                return False
        return True
    except SyntaxError as e:
        # If it fails as expression, try as statement (allows simple assignments)
        try:
            tree = ast.parse(code, mode='exec')
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, 
                                   ast.AsyncFunctionDef, ast.ClassDef)):
                    return False
            return True
        except SyntaxError:
            # Log the actual syntax error for debugging
            print(f"Syntax error in code validation: {e}")
            print(f"Code: {code}")
            return False

def generate_code(question):
    """Generate Python code from natural language question"""
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]
    )
    code = response["message"]["content"].strip()
    
    # Remove markdown code block markers if present
    if code.startswith('```'):
        # Extract code from markdown block
        lines = code.split('\n')
        code_lines = []
        in_block = False
        for line in lines:
            if line.strip().startswith('```'):
                in_block = not in_block
            elif in_block:
                code_lines.append(line)
        if code_lines:
            code = '\n'.join(code_lines).strip()
    
    # Fix common mistakes the LLM makes
    original_code = code
    
    # STEP 0: Fix missing variable in list comprehension: [for r in ...] -> [r for r in ...]
    code = re.sub(r'\[\s*for\s+(\w+)\s+in\s+', r'[\1 for \1 in ', code)
    
    # STEP 1: Replace data.get("rows",[]) with data["rows"] - use regex for flexibility
    code = re.sub(r'data\.get\s*\(\s*["\']rows["\']\s*,\s*\[\s*\]\s*\)', 'data["rows"]', code)
    code = re.sub(r'data\.get\s*\(\s*["\']rows["\']\s*\)', 'data["rows"]', code)
    
    # STEP 2: Fix common typos
    code = code.replace('"just"', '"jwst"')  # Common LLM typo
    code = code.replace("'just'", "'jwst'")
    
    # STEP 3: Fix white_light -> whitelight
    code = code.replace('white_light', 'whitelight')
    code = code.replace('white-light', 'whitelight')
    code = code.replace('White_light', 'whitelight')
    code = code.replace('White-light', 'whitelight')
    
    # STEP 3: Fix instrument/telescope field mistakes
    # If checking alg=="jwst" or alg=="hst", fix to check sv field instead
    # Match: r.get("alg") == "jwst" (with any spacing)
    code = re.sub(r'r\.get\s*\(\s*["\']alg["\']\s*\)\s*==\s*["\']jwst["\']', '"jwst" in r.get("sv","").lower()', code, flags=re.IGNORECASE)
    code = re.sub(r'r\.get\s*\(\s*["\']alg["\']\s*\)\s*==\s*["\']hst["\']', '"hst" in r.get("sv","").lower()', code, flags=re.IGNORECASE)
    
    # Fix sv=="JWST" or sv=="HST" - should use substring match instead
    code = re.sub(r'r\.get\s*\(\s*["\']sv["\']\s*\)\s*==\s*["\']jwst["\']', '"jwst" in r.get("sv","").lower()', code, flags=re.IGNORECASE)
    code = re.sub(r'r\.get\s*\(\s*["\']sv["\']\s*\)\s*==\s*["\']hst["\']', '"hst" in r.get("sv","").lower()', code, flags=re.IGNORECASE)
    
    # Fix sv.lower()=="jwst" or sv.lower()=="hst" - should use substring match
    # Handle various formats: r.get("sv").lower(), r.get("sv","").lower(), r.get("sv",**).lower()
    code = re.sub(r'r\.get\s*\(\s*["\']sv["\']\s*(?:,\s*[^)]+)?\)\s*\.lower\s*\(\s*\)\s*==\s*["\']jwst["\']', '"jwst" in r.get("sv","").lower()', code, flags=re.IGNORECASE)
    code = re.sub(r'r\.get\s*\(\s*["\']sv["\']\s*(?:,\s*[^)]+)?\)\s*\.lower\s*\(\s*\)\s*==\s*["\']hst["\']', '"hst" in r.get("sv","").lower()', code, flags=re.IGNORECASE)
    
    if code != original_code:
        print(f"CODE FIXED:")
        print(f"  Before: {original_code}")
        print(f"  After:  {code}")
    
    return code

def execute_query(code, data):
    """Safely execute generated code against data"""
    if not is_safe_expression(code):
        raise ValueError(f"Generated code contains unsafe operations:\n{code}")
    
    # Allow safe built-in functions
    safe_builtins = {
        "len": len,
        "sum": sum,
        "list": list,
        "set": set,
        "dict": dict,
        "sorted": sorted,
        "min": min,
        "max": max,
        "any": any,
        "all": all,
        "enumerate": enumerate,
        "zip": zip,
        "range": range,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
    }
    
    try:
        # Try as expression first
        try:
            return eval(code, {"__builtins__": safe_builtins}, {"data": data})
        except SyntaxError:
            # If expression fails, try as statement
            namespace = {"data": data}
            exec(code, {"__builtins__": safe_builtins}, namespace)
            # Return the last assigned variable or None
            for key in reversed(list(namespace.keys())):
                if key != "data":
                    return namespace[key]
            return None
    except Exception as e:
        raise RuntimeError(f"Error executing query: {e}")