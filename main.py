#!/usr/bin/env python3
"""
EXCALIBUR Natural Language Interface - Main Launcher
Choose between query interface or chatbot interface
"""

import sys
import gradio as gr
from ui.advanced_interface import create_advanced_interface
from ui.chatbot_interface import create_chatbot_interface

def create_combined_interface():
    """Create a tabbed interface with both query and chatbot modes"""
    
    with gr.Blocks(title="EXCALIBUR AI Assistant", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🔭 EXCALIBUR AI Assistant")
        gr.Markdown("Natural language interface for the EXCALIBUR exoplanet spectroscopy pipeline")
        
        with gr.Tabs():
            with gr.Tab("💬 Chatbot"):
                gr.Markdown("""
                ### Conversational Assistant
                Chat naturally with the EXCALIBUR assistant. You can have a conversation 
                or ask it to query the database.
                """)
                chatbot_interface = create_chatbot_interface()
            
            with gr.Tab("🔍 Query Interface"):
                gr.Markdown("""
                ### Direct Query Interface
                Enter natural language queries to filter and search the EXCALIBUR database.
                Results are displayed in a table format.
                """)
                query_interface = create_advanced_interface()
    
    return interface

if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "chatbot":
            print("Starting EXCALIBUR Chatbot...")
            print("Access at: http://localhost:7861")
            interface = create_chatbot_interface()
            interface.launch(server_name="0.0.0.0", server_port=7861)
        
        elif mode == "query":
            print("Starting EXCALIBUR Query Interface...")
            print("Access at: http://localhost:7860")
            interface = create_advanced_interface()
            interface.launch(server_name="0.0.0.0", server_port=7860)
        
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python main.py [chatbot|query|combined]")
            sys.exit(1)
    
    else:
        # Default: combined interface
        print("Starting EXCALIBUR Combined Interface...")
        print("Access at: http://localhost:7860")
        print("\nAvailable modes:")
        print("  - Chatbot: Conversational interface")
        print("  - Query: Direct query interface")
        
        interface = create_combined_interface()
        interface.launch(server_name="0.0.0.0", server_port=7860)
