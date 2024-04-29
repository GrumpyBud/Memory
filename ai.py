import speech_recognition as sr

# Create a Recognizer instance
r = sr.Recognizer()

# Function to take voice input
def voice_input():
    # Initialize the microphone
    with sr.Microphone() as source:
        print("Speak now...")
        # Listen for audio input
        audio = r.listen(source)

    try:
        # Use Google Speech Recognition API to recognize speech
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")
    except sr.RequestError as e:
        print(f"Speech recognition service error: {e}")

# Example usage
response = voice_input()
if response:
    print(f"You said: {response}")