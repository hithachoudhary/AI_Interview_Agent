import speech_recognition as sr
import pyttsx3
import time

#Globally initializing it
r = sr.Recognizer()

def speak(text):
    if not text.startswith("Interviewer: "):
        print(f"Interviewer: {text}")
    else:
        print(text)
        
    try:
        local_engine = pyttsx3.init()
        local_engine.setProperty('rate', 160)
        local_engine.setProperty('volume', 1.0)
        
        local_engine.say(text)
        local_engine.runAndWait()
        
        local_engine.stop()
        local_engine.startLoop(False)
        local_engine.endLoop()
        
        time.sleep(0.3)
        
    except Exception as e:
        print(f"[TTS Error]: Could not speak text: {e}")
        pass

#S2T conversion
def listen_for_input():
    with sr.Microphone() as source:
        r.energy_threshold = 4000
        r.pause_threshold = 1.5

        print("Listening...")
        
        try:
            audio = r.listen(source, phrase_time_limit=15)
            user_text = r.recognize_google(audio)
            print(f"User (Spoken): {user_text}")
            return user_text
            
        except sr.UnknownValueError:
            speak("Sorry, I did not catch that. Please speak clearly.")
            return ""
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return ""
        except Exception as e:
            print(f"STT Error: {e}")
            speak("An audio error occurred.")
            return ""
        
if __name__ == "__main__":
    print("--- Starting Audio Handler Test ---")
    speak("Hello, I am your voice agent. Please say something after the beep.")
    
    text = listen_for_input()
    if text:
        speak(f"You said: {text}")
    
    #Testing to see if audio works
    speak("Testing silent input. Please stay silent now.")
    silent_text = listen_for_input()
    if not silent_text:
        speak("Test successful: Silence detected and handled.")
        
    print("--- Audio Handler Test Complete ---")
