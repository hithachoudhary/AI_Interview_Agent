# 🤖 AI Interview Practice Partner (Voice Agent)  
This project implements a conversational AI agent designed to conduct realistic mock job interviews and provide structured, objective feedback on a user\'s performance. The agent operates in a Speech-to-Speech (S2S) mode,
prioritizing natural conversation and intelligent agentic behavior, as
required by the assignment.

## Features  
• Speech-to-Speech interviewing (STT + conversational LLM + TTS)  
• Multi-agent architecture (Interviewer Agent + Evaluation Agent)  
• Role-based question retrieval (mini-RAG from structured JSON)  
• Context-aware follow-up questions using window memory  
• Structured performance report generated via Pydantic schema  
• Handles all user personas (Confused, Chatty, Efficient, Edge Case)  


## Setup Instructions  
### 1. Follow these steps to get the project running on your local machine.
  1. Prerequisites:  
  •You musthave Python 3.8+ installed.  
  •API Key: An OpenAI API Key is required for the LLM core.    
  •System Dependencies (Windows/Linux): Due to the use of the PyAudio library for microphone access, you may need to install system
dependencies if the pip install fails:  
      ->Windows: You may need the Visual C++ Build Tools for Python.  
      ->Linux (Debian/Ubuntu): Install portaudio: sudo apt-get install portaudio19-dev.
  
2. Project Installation: Navigate to the project root directory in your terminal.  
•Create and activate a virtual environment (essential)
   python -m venv venv
   source venv/bin/activate on Linux
   .\\venv\\Scripts\\activate on Windows

# 2. Install Python dependencies    
pip install -r requirements.txt  

# 3. API  
•Configuration: Create a file named .env in the project\'s root
directory.  
•Paste your OpenAI key into the file: OPENAI_API_KEY=\"sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\" 

# 4. Running the Agent  
•The agent is launched via the Gradio frontend application.  
Launch the web interface (http://127.0.0.1:7860)  
  python frontend_app.py 
  
