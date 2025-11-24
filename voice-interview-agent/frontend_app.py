import gradio as gr
import os
import time
from dotenv import load_dotenv

import speech_recognition as sr
recognizer = sr.Recognizer()

from agents.interview_agent import InterviewAgent
from agents.evaluation_agent import generate_feedback
from tools.knowledge_base import get_interview_question
from tools.knowledge_base import QUESTION_BANK 

import pyttsx3 

load_dotenv()

def frontend_speak(text):
    """Initializes engine, speaks text, and disposes engine to prevent locking."""
    print(f"Agent Speaking: {text}")
    try:
        local_engine = pyttsx3.init()
        local_engine.setProperty('rate', 160)
        local_engine.setProperty('volume', 1.0)
        
        text_to_speak = text
        if text.startswith("Interviewer: "):
            text_to_speak = text[len("Interviewer: "):]
        
        local_engine.say(text_to_speak)
        local_engine.runAndWait() 
        
        local_engine.stop()
        local_engine.startLoop(False) 
        local_engine.endLoop()
        time.sleep(0.3) 
        
    except Exception as e:
        print(f"[TTS Error in Frontend]: Could not speak text: {e}")
        pass

STATE = {}
HISTORY = []

def initialize_session(role: str):
    """Initializes the Interview Agent and starts the conversation."""
    global STATE, HISTORY
    
    STATE = {}
    HISTORY = []
    
    if not os.getenv("OPENAI_API_KEY"):
        return "FATAL ERROR: API Key not found. Please set it in your .env file.", ""
    
    if not role.strip():
        return "Please select a job role to start the interview.", ""

    role_announcement = f"I am initializing your mock interview for a {role} role."
    frontend_speak(role_announcement)

    try:
        agent = InterviewAgent(role=role)
        STATE['agent'] = agent
        STATE['role'] = role
        
        first_q = get_interview_question.invoke(role)
        agent.start_interview(first_q)
        
        full_question_string = f"Interviewer: {first_q}"
        frontend_speak(full_question_string)
        
        HISTORY.append(full_question_string) 
        
        return f"Interview Started. Question: {first_q}", "" 
    
    except Exception as e:
        print(f"Initialization Error: {e}")
        return f"ERROR: Failed to initialize Agent. Error: {e}", ""

def handle_stop_interview():
    """Triggers feedback generation and clears the state."""
    global STATE, HISTORY
    
    if 'agent' not in STATE:
        return "ERROR: Interview not started.", ""

    frontend_speak("Thank you for your time. The interview is concluded. I am generating your feedback report now.")
    
    agent = STATE['agent']
    role = STATE['role']
    full_history = agent.get_full_history()
    
    report_text = generate_feedback_report(role, full_history)
    
    STATE = {}
    HISTORY = []
    
    return "Interview Concluded. See detailed report below.", report_text

def generate_feedback_report(role: str, full_history):
    """Generates the feedback report and returns the display text in a CLEAN, NON-MARKDOWN FORMAT."""
    
    feedback_object = generate_feedback(role, full_history)
    
    report_text = f"--- INTERVIEW CONCLUDED FOR {role.upper()} ---\n\n"
    report_text += "Overall Assessment:\n"
    report_text += f"{feedback_object.overall_assessment}\n"
    
    actionable_improvements = []
    
    for section in feedback_object.sections:
        report_text += "\n"
        report_text += f"*** {section.area} (Score: {section.score_out_of_5}/5) ***\n"
        report_text += f"Summary: {section.summary}\n"
        
        actionable_improvements.append({
            'area': section.area,
            'improvements': section.areas_for_improvement
        })
    
    report_text += "\n----------------------------------------\n"
    report_text += "ACTIONABLE IMPROVEMENT PLAN:\n"
    
    for item in actionable_improvements:
        report_text += f"\n>> {item['area']} <<\n"
        report_text += "Actionable Steps:\n"
        report_text += "\n".join([f"  - {step}" for step in item['improvements']])
        report_text += "\n"
    
    return report_text


def process_audio_input(audio_filepath: str):
    """Processes user's speech input from the audio file and generates the agent's response."""
    global STATE, HISTORY
    
    if 'agent' not in STATE:
        return "ERROR: Please start the interview first.", ""

    agent = STATE['agent']
    
    if audio_filepath is None:
        return "Please speak your response (audio not captured).", ""

    # 1. Transcribe the audio file
    if isinstance(audio_filepath, str):
        try:
            with sr.AudioFile(audio_filepath) as source:
                audio_data = recognizer.record(source)
                user_speech = recognizer.recognize_google(audio_data)
                user_input = user_speech.strip()
        except sr.UnknownValueError:
            user_input = ""
            user_speech = "[Could not understand audio]"
        except Exception as e:
            print(f"STT ERROR: {e}")
            user_input = ""
            user_speech = "[STT Communication Error]"
    else:
        user_input = ""
        user_speech = "[Invalid Input]"

    HISTORY.append(f"User: {user_speech}")

    # --- Handle Invalid/Silent Input ---
    if not user_input or user_input == "[Could not understand audio]":
        frontend_speak("Sorry, I didn't quite catch that. Could you please repeat your answer?")
        return "Waiting for response... Please repeat your answer.", ""

    
    # 2. Continue the coversation
    try:
        ai_response = agent.get_response(user_input)
        
        full_response_string = f"Interviewer: {ai_response}"
        frontend_speak(full_response_string)
        
        HISTORY.append(full_response_string)
        # Display the next question in the status box
        return f"Waiting for response... Question: {ai_response}", "" 
    
    except Exception as e:
        print(f"ERROR: LLM communication failed. {e}")
        return "ERROR: Communication Failure. Please restart.", ""



available_roles = [role.replace('_', ' ').title() for role in QUESTION_BANK.keys()]


with gr.Blocks(title="Eightfold AI Interview Partner") as demo: 
    
    gr.Markdown("#  AI Interview Practice Partner")
    gr.Markdown(
        "**Instructions:** Choose a role, click **'Start New Interview'**, then speak your answers into the microphone. Press **'Stop Interview'** when done."
    )
    
    # 1. Setup/Role Selection
    with gr.Row():
        role_input = gr.Dropdown(
            label="1. Choose Job Role",
            choices=available_roles,
            value=available_roles[0] if available_roles else "Software Engineer",
            scale=2
        )
        
        start_button = gr.Button("Start Interview", variant="primary", scale=1)
        stop_button = gr.Button("Stop Interview", variant="stop", scale=1) 

    # 2. Status Display (Shows current question and final assessment)
    status_output = gr.Textbox(
        label="Current Question / Status", 
        value="Ready to start.", 
        interactive=False, 
        lines=3
    )
    
    # --- 3. Audio Input and Control Row ---
    with gr.Row():
        # The microphone component (for recording, made small and compact)
        audio_input = gr.Audio(
            sources="microphone", 
            type="filepath", 
            label="Speak Your Answer",
            show_label=False,
            elem_id="audio-input-mic",
            scale=0 
        )
        # Final Report Output (Hidden during interview)
        history_output = gr.Textbox(
            label="Final Interview Feedback Report", 
            lines=20, 
            interactive=False, 
            placeholder="The final feedback report will appear here after you press 'Stop Interview'.",
            scale=4
        )
    
    
    #Start Button: Initializes the session
    start_button.click(
        fn=initialize_session, 
        inputs=[role_input], 
        outputs=[status_output, history_output],
        queue=False
    )
    
    #Stop Button: Generates the report and clears state
    stop_button.click(
        fn=handle_stop_interview, 
        inputs=[], 
        outputs=[status_output, history_output],
        queue=False
    )

    #Audio Input: Processes the recorded file path
    audio_input.change(
        fn=process_audio_input, 
        inputs=[audio_input], 
        outputs=[status_output, history_output],
        queue=True
    )

#Launching the app
if __name__ == "__main__":
    print("Launching Gradio App...")
    # NOTE: Using deprecated syntax to force theme integration
    demo.launch(share=False, theme=gr.themes.Ocean())