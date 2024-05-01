from gtts import gTTS
import os
import pygame
import json
from openai import OpenAI
import speech_recognition as sr
import io

pygame.init()
pygame.mixer.init

client = OpenAI()

class UserProfileManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.profiles = self.load_profiles()
        OpenAI.api_key = os.getenv("OPENAI_API_KEY")
        self.recognizer = sr.Recognizer()
        
    def text_to_speech(self, text):
        tts = gTTS(text=text, lang='en')
        with io.BytesIO() as f:
            tts.write_to_fp(f)
            f.seek(0)
            pygame.mixer.music.load(f)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
        
    def speech_to_text(self):
        with sr.Microphone() as source:
            print("Speak now...")
            audio = self.recognizer.listen(source)

        try:
            text = self.recognizer.recognize_whisper_api(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand your speech.")
            self.text_to_speech("Sorry, I could not understand your speech.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from the speech recognition service; {e}")
            self.text_to_speech(f"Could not request results from the speech recognition service; {e}")
            return None

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
            user_input = input("You: ")
            if user_input.lower() == "quit":
                break

            response = self.chat(user_input)
            print("ChatGPT: ", response)
    
    

# Example usage
file_path = "user_profiles.json"
user_manager = UserProfileManager(file_path)
first_time = True
activate = False

while True:
    print("\n1. Create Profile\n2. Activate Profile\n3. Edit Profile\n4. View Profiles\n5. Activate Chat\n6. Exit")
    if first_time:
        user_manager.text_to_speech("1- create profile. 2- activate profile. 3- edit profile. 4- view profiles. 5- activate chat. 6- exit. Speak your choice:")
        first_time = False
    choice = user_manager.speech_to_text()

    if choice is None:
        print("none were picked")
        continue

    if choice.lower() == "1" or "one" or "create":
        print("speak your name")
        user_manager.text_to_speech("Speak your name:")
        name = user_manager.speech_to_text()
        if name is None:
            continue
        print("speak your age")
        user_manager.text_to_speech("Speak your age:")
        age = user_manager.speech_to_text()
        if age is None:
            continue
        print("speak your interests")
        user_manager.text_to_speech("Speak your interests:")
        interests = user_manager.speech_to_text()
        if interests is None:
            continue
        user_manager.create_profile(name, age, interests)
        print(name, age, interests)
    elif choice == '2':
        activated = True
        name = input("Enter name to activate: ")
        UserProfileManager.text_to_speech(UserProfileManager, f"Enter name to activate:")
        user_manager.activate_profile(name)
    elif choice == '3':
        name = input("Enter name: ")
        UserProfileManager.text_to_speech(UserProfileManager, f"Enter name:")
        field = input("Enter field to edit (age or interests): ")
        UserProfileManager.text_to_speech(UserProfileManager, f"Enter field to edit, (age or interests)")
        new_value = input(f"Enter new value for {field}: ")
        UserProfileManager.text_to_speech(UserProfileManager, f"Enter new value for {field}:")
        user_manager.edit_profile(name, field, new_value)
    elif choice == '4':
        user_manager.view_profiles()
    elif choice == '5':
        if not activate:
            activate = True
            name = input("Enter name to activate: ")
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