import os
from dotenv import load_dotenv
from agents.interview_agent import InterviewAgent
from agents.evaluation_agent import generate_feedback
from tools.knowledge_base import get_interview_question
from tools.audio_handler import listen_for_input, speak 

load_dotenv()

def run_agent():
    if not os.getenv("OPENAI_API_KEY"):
        print("FATAL ERROR: OPENAI_API_KEY not found. Please set it in your .env file.")
        return

    speak("Interview Practice Partner Initializing.")

    #User should selet job role
    while True:
        speak("What job role are you practicing for?")
        job_role = listen_for_input().strip()
        
        if len(job_role.split()) < 2:
            speak("I didn't catch that clearly. Please state the full job title clearly, like 'Software Engineer'.")
            continue
            
        if job_role:
            speak(f"Starting your mock interview for a {job_role} role.")
            break
        else:
            speak("Please tell me the job title you want to practice for.")

    try:
        interview_agent = InterviewAgent(role=job_role)
    except Exception as e:
        print(f"Error initializing LLM client: {e}")
        speak("I failed to connect to the AI service. Please check your API key.")
        return

    first_q = get_interview_question.invoke(job_role)
    speak(first_q)

    #Main function (Interview Loop)
    while True:
        user_input = listen_for_input()
        if not user_input:
            continue
        
        if user_input.upper() in ["STOP", "END INTERVIEW", "FINISH"]:
            speak("Thank you. The interview is concluded. Generating your feedback report.")
            break
        
        try:
            ai_response = interview_agent.get_response(user_input)
            speak(ai_response)
        except Exception as e:
            print(f"LLM Error during response: {e}")
            speak("A communication error occurred. Trying to continue.")

    print("\nGenerating Structured Feedback Report...")
    full_history = interview_agent.get_full_history()

    try:
        feedback_report = generate_feedback(job_role, full_history)

        print("\nInterview Feedback Report")
        print(f"Overall Assessment: {feedback_report.overall_assessment}")
        
        for section in feedback_report.sections:
            print(f"\n{section.area} (Score: {section.score_out_of_5}/5)")
            print(f"Summary: {section.summary}")
            print("Areas for Improvement:")
            for item in section.areas_for_improvement:
                print(f"* {item}")
                
    except Exception as e:
        print(f"Error generating feedback: {e}")

if __name__ == "__main__":
    run_agent()
