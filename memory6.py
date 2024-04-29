from gtts import gTTS
from pydub import AudioSegment
import json
import os

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

    def create_profile(self, username, age, email):
        if username not in self.profiles:
            self.profiles[username] = {'age': age, 'email': email}
            print(f"Profile created for {username}")
            self.save_profiles()

            # Perform TTS and save as WAV
            self.text_to_speech(f"Profile created for {username}")
        else:
            print(f"Username '{username}' already exists. Please choose a different username.")

    def edit_profile(self, username, field, new_value):
        if username in self.profiles:
            if field in self.profiles[username]:
                self.profiles[username][field] = new_value
                print(f"Profile updated for {username}")
                self.save_profiles()

                # Perform TTS and save as WAV
                self.text_to_speech(f"Profile updated for {username}")
            else:
                print(f"Field '{field}' not found in the profile.")
        else:
            print(f"Username '{username}' not found. Please enter a valid username.")

    def view_profiles(self):
        print("User Profiles:")
        for username, profile in self.profiles.items():
            print(f"Username: {username}, Age: {profile['age']}, Email: {profile['email']}")

    def text_to_speech(self, text):
        # Use gTTS for text-to-speech
        tts = gTTS(text=text, lang='en')
        
        # Create output folder if it doesn't exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        output_file_path = os.path.join(self.output_folder, "output.wav")
        tts.save(output_file_path)  # Save as WAV
        print(f"Text-to-speech audio saved as '{output_file_path}'.")

# Example usage
file_path = "user_profiles.json"
user_manager = UserProfileManager(file_path)

while True:
    print("\n1. Create Profile\n2. Edit Profile\n3. View Profiles\n4. Exit")
    choice = input("Enter your choice: ")

    if choice == '1':
        username = input("Enter username: ")
        age = input("Enter age: ")
        email = input("Enter email: ")
        user_manager.create_profile(username, age, email)
    elif choice == '2':
        username = input("Enter username: ")
        field = input("Enter field to edit (age or email): ")
        new_value = input(f"Enter new value for {field}: ")
        user_manager.edit_profile(username, field, new_value)
    elif choice == '3':
        user_manager.view_profiles()
    elif choice == '4':
        print("Exiting the program. Goodbye!")
        break
    else:
        print("Invalid choice. Please enter a valid option.")
