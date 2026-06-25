"""
EXCALIBUR Chatbot Interface
A conversational AI assistant that can chat and query the EXCALIBUR database.
"""

import gradio as gr
from typing import List, Tuple
import ollama
import random

from ai.query_translator import generate_code, execute_query
from data.load_excalibur_data import load_excalibur_data

EXCALIBUR_OUTPUT_PATH = "/Users/enguyen/ESP-AI"

# Load data once at startup
print("Loading EXCALIBUR data...")
EXCALIBUR_DATA = load_excalibur_data(EXCALIBUR_OUTPUT_PATH)
print(f"✓ Loaded {len(EXCALIBUR_DATA.get('rows', []))} runs")

# Store user preferences (nickname, etc.)
USER_PREFERENCES = {}

SYSTEM_PROMPT = """You are a helpful and friendly AI assistant for the EXCALIBUR exoplanet spectroscopy pipeline.

You can help users in two ways:
1. Have natural, casual conversations - respond to greetings, questions about how you're doing, compliments, jokes, etc. Also be able toanswer general questions about EXCALIBUR, exoplanets, and data analysis
2. Query the EXCALIBUR database when users ask about specific runs, targets, or observations

Your personality:
- Friendly, enthusiastic, and conversational
- Passionate about exoplanets and space science
- Use emojis occasionally (🔭 🌟 🚀 😊 🤖)
- Remember context from the conversation
- Be genuine and not overly formal

When users greet you, ask how you are, give compliments, or chat casually, respond naturally and engagingly.
When users want data, help them query the 14M+ EXCALIBUR observations.

Be helpful, concise, and personable!"""

def is_database_query(message: str) -> bool:
    """Determine if the message is a database query or general conversation"""
    query_keywords = [
        'show', 'find', 'get', 'list', 'search', 'query', 'filter',
        'jwst', 'hst', 'transit', 'eclipse', 'whitelight', 'spectrum',
        'target', 'observation', 'run', 'data', 'all', 'how many'
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in query_keywords)

def format_results_as_text(rows: List[dict], limit: int = 10) -> str:
    """Format query results as readable text"""
    if not rows:
        return "No results found."
    
    total = len(rows)
    display_rows = rows[:limit]
    
    result = f"Found {total} result{'s' if total != 1 else ''}:\n\n"
    
    for i, row in enumerate(display_rows, 1):
        result += f"{i}. **{row.get('target', 'Unknown')}** - Run {row.get('run_id', '?')}\n"
        result += f"   Task: {row.get('task', '?')} | Algorithm: {row.get('alg', '?')}\n"
        result += f"   Instrument: {row.get('sv', '?')}\n\n"
    
    if total > limit:
        result += f"... and {total - limit} more results"
    
    return result

def chat_with_excalibur(message: str, history: List[Tuple[str, str]]) -> str:
    """Process user message and return response"""
    
    # Get user's nickname if set
    nickname = USER_PREFERENCES.get('nickname', '')
    greeting_name = f" {nickname}" if nickname else ""
    
    try:
        # Check for nickname setting FIRST (before database query check)
        message_lower = message.lower()
        if 'call me' in message_lower:
            import re
            match = re.search(r'call me ([\w]+)', message_lower)
            if match:
                nickname = match.group(1).capitalize()
                USER_PREFERENCES['nickname'] = nickname
                return f"Got it! I'll call you {nickname} from now on. 😊 How can I help you today?"
        
        # Check if this is a database query
        if is_database_query(message):
            try:
                # Generate and execute query
                code = generate_code(message)
                result = execute_query(code, EXCALIBUR_DATA)
                
                # Format results
                if isinstance(result, list):
                    rows = result
                elif isinstance(result, int):
                    return f"Result: {result}"
                else:
                    rows = []
                
                # Create response
                response = format_results_as_text(rows)
                
                # Add the generated query for transparency
                response += f"\n\n---\n*Query: `{code}`*"
                
                return response
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                return f"I tried to query the database but encountered an error:\n\n```\n{error_details}\n```\n\nCould you rephrase your question?"
        
        else:
            # General conversation - use LLM for natural responses
            # Build nickname context if set
            if USER_PREFERENCES.get('nickname'):
                nickname_context = f"\n\nNote: The user's name is {USER_PREFERENCES['nickname']}. Use their name occasionally in responses."
            else:
                nickname_context = ""
            
            # Use LLM for all conversational responses
            try:
                # Build conversation history for context
                system_prompt = SYSTEM_PROMPT + nickname_context
                messages = [{"role": "system", "content": system_prompt}]
                
                for user_msg, assistant_msg in history:
                    messages.append({"role": "user", "content": user_msg})
                    messages.append({"role": "assistant", "content": assistant_msg})
                
                messages.append({"role": "user", "content": message})
                
                # Try llama3.2 first, fall back to codellama if not available
                try:
                    response = ollama.chat(
                        model="llama3.2",
                        messages=messages
                    )
                except Exception as model_error:
                    if "not found" in str(model_error):
                        # Fall back to codellama
                        response = ollama.chat(
                            model="codellama",
                            messages=messages
                        )
                    else:
                        raise
                
                return response["message"]["content"]
                
            except Exception as e:
                return f"""I'm having trouble connecting to my conversation system right now. 

I can still help you query the EXCALIBUR database! Try asking:
- "Show me all JWST transit observations"
- "Find HST data for GJ 436"
- "How many whitelight runs are there?"

(Error: {str(e)})"""
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"""Something went wrong! Here's the error:

```
{error_details}
```

Please try again or rephrase your message."""

def create_chatbot_interface():
    """Create the Gradio chatbot interface"""
    
    with gr.Blocks(title="EXCALIBUR Chatbot") as interface:
        gr.Markdown("# 🤖 EXCALIBUR Chatbot Assistant")
        gr.Markdown("""
        Chat with the EXCALIBUR assistant! You can:
        - Have a conversation (try saying "hello" or "what can you do?")
        - Query the database (try "show me all JWST transit runs")
        - Ask questions about exoplanets and data analysis
        """)
        
        chatbot = gr.Chatbot(
            height=500,
            label="Chat with EXCALIBUR",
            show_label=True
        )
        
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Type your message here... (e.g., 'Hello!' or 'Show me all JWST data')",
                label="Message",
                scale=4
            )
            submit = gr.Button("Send", scale=1, variant="primary")
        
        with gr.Row():
            clear = gr.Button("Clear Chat")
        
        gr.Markdown("### Example queries:")
        with gr.Row():
            gr.Examples(
                examples=[
                    "Hello!",
                    "What can you do?",
                    "Show me all JWST transit observations",
                    "Find HST data for GJ 436",
                    "List all eclipse observations",
                ],
                inputs=msg,
                label="Try these:"
            )
        
        gr.Markdown(f"*Database: {len(EXCALIBUR_DATA.get('rows', []))} runs loaded*")
        
        def respond(message, chat_history):
            if not message.strip():
                return "", chat_history
            
            # Convert Gradio messages format to list of tuples for our function
            history_list = []
            if chat_history:
                for item in chat_history:
                    if isinstance(item, dict):
                        # Gradio 6.0 messages format
                        if item.get('role') == 'user':
                            user_msg = item.get('content', '')
                            # Find the next assistant message
                            continue
                    elif isinstance(item, (list, tuple)) and len(item) == 2:
                        history_list.append((item[0], item[1]))
            
            bot_response = chat_with_excalibur(message, history_list)
            
            # Return in Gradio 6.0 messages format with avatars
            if chat_history is None:
                chat_history = []
            
            # Check if custom avatar exists
            import os
            avatar_path = "/Users/enguyen/ESP-AI/assets/excalibur_logo.png"
            bot_avatar = avatar_path if os.path.exists(avatar_path) else None
            
            chat_history.append({
                "role": "user", 
                "content": message
            })
            
            assistant_msg = {
                "role": "assistant", 
                "content": bot_response
            }
            
            # Add avatar metadata if available
            if bot_avatar:
                assistant_msg["metadata"] = {"avatar": bot_avatar}
            
            chat_history.append(assistant_msg)
            
            return "", chat_history
        
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        submit.click(respond, [msg, chatbot], [msg, chatbot])
        clear.click(lambda: None, None, chatbot, queue=False)
    
    return interface

if __name__ == "__main__":
    interface = create_chatbot_interface()
    interface.launch(server_name="0.0.0.0", server_port=7861)
