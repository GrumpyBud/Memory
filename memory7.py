from gtts import gTTS
from pydub import AudioSegment
import json
from openai import OpenAI
import os

client = (OpenAI)



class UserProfileManager:
    def __init__(self, file_path, output_folder="ttsoutput"):
        self.file_path = file_path
        self.output_folder = output_folder
        self.profiles = self.load_profiles()

    def load_profiles(self):
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_profiles(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.profiles, file, indent=2)

    def create_profile(self, name, age, email):
        if name not in self.profiles:
            self.profiles[name] = {'age': age, 'email': email}
            print(f"Profile created for {name}")
            self.save_profiles()

            # Perform TTS and save as WAV
            self.text_to_speech(f"Profile created for {name}")
        else:
            print(f"Name '{name}' already exists. Please choose a different name.")

    def activate_profile(self, name):
        if name in self.profiles:
            profile_info = self.profiles[name]
            print(f"Activating profile for {name}")

            # Example: initiate conversation with ChatGPT using OpenAI API
            conversation = f"User: {name}\nAge: {profile_info['age']}\nEmail: {profile_info['email']}"
            response = self.chat_with_gpt(conversation)

            print("ChatGPT response:")
            print(response)
        else:
            print(f"Name '{name}' not found. Please enter a valid Name.")

    def edit_profile(self, name, field, new_value):
        if name in self.profiles:
            if field in self.profiles[name]:
                self.profiles[name][field] = new_value
                print(f"Profile updated for {name}")
                self.save_profiles()

                # Perform TTS and save as WAV
                self.text_to_speech(f"Profile updated for {name}")
            else:
                print(f"Field '{field}' not found in the profile.")
        else:
            print(f"Name '{name}' not found. Please enter a valid Name.")

    def view_profiles(self):
        print("User Profiles:")
        for name, profile in self.profiles.items():
            print(f"Name: {name}, Age: {profile['age']}, Email: {profile['email']}")

    def text_to_speech(self, text):
        # Use gTTS for text-to-speech
        tts = gTTS(text=text, lang='en')
        
        # Create output folder if it doesn't exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        output_file_path = os.path.join(self.output_folder, "output.wav")
        tts.save(output_file_path)  # Save as WAV
        print(f"Text-to-speech audio saved as '{output_file_path}'.")

    def chat_with_gpt(self, conversation):
        instructions = "You are a helpful assistant, having a conversation with" + conversation
        # Set up OpenAI API key
        #arleady env variable

        # Call OpenAI Chat API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": instructions},
            ]       
        )
        return response['choices'][0]['text']

# Example usage
file_path = "user_profiles.json"
user_manager = UserProfileManager(file_path)

while True:
    print("\n1. Create Profile\n2. Activate Profile\n3. Edit Profile\n4. View Profiles\n5. Exit")
    choice = input("Enter your choice: ")

    if choice == '1':
        name = input("Enter name: ")
        age = input("Enter age: ")
        email = input("Enter email: ")
        user_manager.create_profile(name, age, email)
    elif choice == '2':
        name = input("Enter name to activate: ")
        user_manager.activate_profile(name)
    elif choice == '3':
        name = input("Enter name: ")
        field = input("Enter field to edit (age or email): ")
        new_value = input(f"Enter new value for {field}: ")
        user_manager.edit_profile(name, field, new_value)
    elif choice == '4':
        user_manager.view_profiles()
    elif choice == '5':
        print("Exiting the program. Goodbye!")
        break
    else:
        print("Invalid choice. Please enter a valid option.")
