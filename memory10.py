from gtts import gTTS
import os
import pygame
import json
import speech_recognition as sr
from openai import OpenAI
pygame.init()
pygame.mixer.init()


recognizer = sr.Recognizer()
client = OpenAI()

class UserProfileManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.profiles = self.load_profiles()
        OpenAI.api_key = os.getenv("OPENAI_API_KEY")
        
    def text_to_speech(self, text):
        tts = gTTS(text=text, lang='en')

        output_file_path = "output.wav"
        tts.save(output_file_path)  # Save as WAV
        print(f"Text-to-speech audio saved as '{output_file_path}'.")
        self.outputsound = pygame.mixer.Sound("output.wav")
        pygame.mixer.Sound.play(self.outputsound)

    def play_wav(self, output):
        pygame.mixer.music.load(output)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

    def load_profiles(self):
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_profiles(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.profiles, file, indent=2)

    def create_profile(self, name, age, interests):
        if name not in self.profiles:
            self.profiles[name] = {'age': age, 'interests': interests}
            print(f"Profile created for {name}")
            self.save_profiles()

            # Perform TTS and save as WAV
            self.text_to_speech(f"Profile created for {name}")
        else:
            print(f"Name '{name}' already exists. Please choose a different name.")
            self.text_to_speech(f"Name '{name}' already exists. Please choose a different name.")

    def activate_profile(self, name):
        if name in self.profiles:
            profile = self.profiles[name]
            self.name = name
            self.age = profile['age']
            self.interests = profile['interests']
            print(f"Name: {name}, Age: {self.age}, Interests: {self.interests}")
            self.text_to_speech(f"Activating profile for {name}. Age: {self.age}, Interests: {self.interests}")
        else:
            print(f"Name '{name}' not found. Please enter a valid Name.")
            self.text_to_speech(f"Name '{name}' not found. Please enter a valid Name.")

    def edit_profile(self, name, field, new_value):
        if name in self.profiles:
            if field in self.profiles[name]:
                self.profiles[name][field] = new_value
                print(f"Profile updated for {name}")
                self.save_profiles()
                self.text_to_speech(f"Profile updated for {name}")

                # Perform TTS and save as WAV
                self.text_to_speech(f"Profile updated for {name}")

            else:
                print(f"Field '{field}' not found in the profile.")
                self.text_to_speech(f"Field '{field}' not found in the profile.")
        else:
            print(f"Name '{name}' not found. Please enter a valid Name.")
            self.text_to_speech(f"Name '{name}' not found. Please enter a valid Name.")

    def view_profiles(self):
        print("User Profiles:")
        for name, profile in self.profiles.items():
            print(f"Name: {name}, Age: {profile['age']}, Interests: {profile['interests']}")
            self.text_to_speech(f"Name: {name}, Age: {profile['age']}, Interests: {profile['interests']}")

    def chat(self, user_input):
        conversation_history = [{"role": "system", "content": f"You are an assistant talking to {self.name} who is {self.age} years old. They enjoy {self.interests}."}]
        # Append user input to conversation history
        conversation_history.append({"role": "user", "content": user_input})

        # Call the OpenAI API with the conversation history
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_history,
        )

        # Append the bot's response to the conversation history
        response = completion.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": response})

        return response

    def chat_with_gpt(self):
        while True:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source)
            try:
                user_input = recognizer.recognize_google(audio)
                print("You:", user_input)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                continue
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
                continue
            if user_input.lower() == "quit":
                break

            response = self.chat(user_input)
            print("ChatGPT: ", response)
    
    def get_voice_input(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.text_to_speech("Listening...")
            audio = recognizer.listen(source)
        try:
            user_input = recognizer.recognize_sphinx(audio)
            print("You said:", user_input)
            self.text_to_speech(f"You said: {user_input}")
            return user_input
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
            self.text_to_speech("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Speech Recognition service; {0}".format(e))
            self.text_to_speech(f"Could not request results from Speech Recognition service; {e}")
    

    
    

# Example usage
file_path = "user_profiles.json"
user_manager = UserProfileManager(file_path)
recognizer = sr.Recognizer()
first_time = True
activate = False

while True:
    print("\n1. Create Profile\n2. Activate Profile\n3. Edit Profile\n4. View Profiles\n5. Activate Chat\n6. Exit")
    if first_time:
        UserProfileManager.text_to_speech(UserProfileManager, f"1- create profile. 2- activate profile. 3- edit profile. 4- view profiles. 5- activate chat. 6- exit. Enter your choice:")
        first_time = False
    choice = user_manager.get_voice_input()
    
    if choice == '1':
        name = user_manager.get_voice_input()
        UserProfileManager.text_to_speech(UserProfileManager, f"Enter name:")
        age = user_manager.get_voice_input()
        UserProfileManager.text_to_speech(UserProfileManager, f"Enter Age:")
        interests = user_manager.get_voice_input()
        UserProfileManager.text_to_speech(UserProfileManager, f"Enter interests:")
        user_manager.create_profile(name, age, interests)
    elif choice == '2':
        activated = True
        name = user_manager.get_voice_input()
        UserProfileManager.text_to_speech(UserProfileManager, f"Enter name to activate:")
        user_manager.activate_profile(name)
    elif choice == '3':
        name = user_manager.get_voice_input()
        UserProfileManager.text_to_speech(UserProfileManager, f"Enter name:")
        field = user_manager.get_voice_input()
        UserProfileManager.text_to_speech(UserProfileManager, f"Enter field to edit, (age or interests)")
        new_value = user_manager.get_voice_input()
        UserProfileManager.text_to_speech(UserProfileManager, f"Enter new value for {field}:")
        user_manager.edit_profile(name, field, new_value)
    elif choice == '4':
        user_manager.view_profiles()
    elif choice == '5':
        if not activate:
            activate = True
            name = user_manager.get_voice_input()
            UserProfileManager.text_to_speech(UserProfileManager, f"Enter name to activate:")
            user_manager.activate_profile(name)    
        else:
            user_manager.chat_with_gpt()
            
    elif choice == '6':
        print("Exiting the program. Goodbye!")
        UserProfileManager.text_to_speech(UserProfileManager, f"Exiting the program. Goodbye!")
        import time
        time.sleep(1.5)
        break
    else:
        print("Invalid choice. Please enter a valid option.")
        UserProfileManager.text_to_speech(UserProfileManager, f"Invalid choice. Please enter a valid option.")
