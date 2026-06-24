#!/usr/bin/env python3
"""
EXCALIBUR Chatbot - Conversational interface with database query capabilities
Launch this to start the chatbot interface on port 7861
"""

from ui.chatbot_interface import create_chatbot_interface

if __name__ == "__main__":
    print("Starting EXCALIBUR Chatbot...")
    print("Access at: http://localhost:7861")
    
    interface = create_chatbot_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False
    )
