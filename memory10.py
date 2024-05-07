from gtts import gTTS
import os
import pygame
import json
from openai import OpenAI
import speech_recognition as sr
import io
import re
import time
import threading
import inflect
from pynput import keyboard
import string
from num2words import num2words
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.utils import get_stop_words
from text2digits import text2digits

pygame.init()
pygame.mixer.init()
pygame.mixer.get_init()

client = OpenAI()

class UserProfileManager:
    def summarize(text, word_count=15):
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LexRankSummarizer()
        summarizer.stop_words = get_stop_words("english")
        summary = summarizer(parser.document, word_count)
        return " ".join([str(sentence) for sentence in summary])
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.profiles = self.load_profiles()
        OpenAI.api_key = os.getenv("OPENAI_API_KEY")
        self.recognizer = sr.Recognizer()
        self.skip_current_tts = False  # Renamed from skip_tts
        self.t2d = text2digits.Text2Digits()

        # Set up keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
    def on_press(self, key):
        if key == keyboard.KeyCode.from_char('s'):
            self.skip_current_tts = True  # Updated to use skip_current_tts
            print("Skipping current TTS output...")
        else:
            self.skip_current_tts = False  # Updated to use skip_current_tts

    def text_to_speech(self, text):
        if not self.skip_current_tts:
            # Convert numbers to words using num2words
            text = re.sub(r'\b(\d+)\b', lambda m: num2words(int(m.group(0))), text)

            tts = gTTS(text=text, lang='en')
            output_file_path = "output.wav"  # Set the output file path
            audio_data = io.BytesIO()
            tts.write_to_fp(audio_data)
            audio_data.seek(0)
            try:
                pygame.mixer.music.load(audio_data)
            except pygame.error as e:
                if "unsupported audio format" in str(e):
                    print("Unsupported audio format. Skipping TTS output...")
                else:
                    raise e
            else:
                print(f"Text-to-speech audio saved as '{output_file_path}'.")

                def play_tts():
                    try:
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            if self.skip_current_tts:
                                pygame.mixer.music.stop()
                                print("Current TTS output skipped.")
                                break
                    except pygame.error as e:
                        if "unsupported audio format" in str(e):
                            print("Unsupported audio format. Skipping TTS output...")
                        else:
                            raise e

                # Start the TTS playback in a separate thread
                tts_thread = threading.Thread(target=play_tts)
                tts_thread.start()

                # Print the TTS output while the TTS is playing
                for char in text:
                    if self.skip_current_tts:
                        break
                    print(char, end='', flush=True)
                    time.sleep(0.1)  # Adjust the sleep time to control the speed of printing

                # Wait for the TTS thread to finish
                tts_thread.join()
                self.skip_current_tts = False

    def speech_to_text(self):
        with sr.Microphone() as source:
            audio = self.recognizer.listen(source)

        try:
            text = self.recognizer.recognize_google(audio)
            text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())  # Remove punctuation and special characters
            text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
            print(f"Hmm, I heard you say: {text}")
            return text
        except sr.UnknownValueError:
            print("I'm sorry, I didn't catch that. Can you repeat?")
            self.text_to_speech("Sorry, I couldn't understand you.")
            return None
        except sr.RequestError as e:
            print(f"Oops, I couldn't connect to the speech recognition service; {e}")
            self.text_to_speech(f"Sorry, I couldn't connect to the speech recognition service; {e}")
            return None
        
    def play_wav(self, output):
        try:
            pygame.mixer.music.load(output)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
        except pygame.error as e:
            if "unsupported audio format" in str(e):
                print("Unsupported audio format. Skipping WAV playback...")
            else:
                raise e

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
        # Convert number words to digits in the age
        age = self.t2d.convert(age)

        # Remove any non-digit characters from the age``
        age = ''.join(char for char in age if char.isdigit())

        if name not in self.profiles:
            self.profiles[name] = {'age': age, 'interests': interests}
            print(f"Profile created for {name}")
            self.save_profiles()

            # Perform TTS and save as WAV
            self.text_to_speech(f"Great, I've created a new profile for {name}. "
                                "Is there anything else you'd like to do?")
        else:
            print(f"Sorry, a profile with the name '{name}' already exists. "
                "Would you like to try again with a different name?")
    
    def words_to_number(self, text):
        word_to_number = {
            'zero': '0',
            'one': '1',
            'two': '2',
            'three': '3',
            'four': '4',
            'five': '5',
            'six': '6',
            'seven': '7',
            'eight': '8',
            'nine': '9',
            'ten': '10',
            # Add more mappings as needed
        }
        words = text.split()
        numbers = []
        for word in words:
            if word.lower() in word_to_number:
                numbers.append(word_to_number[word.lower()])
            else:
                numbers.append(word)
        return ' '.join(numbers)



    def activate_profile(self, name):
        for profile_name in self.profiles:
            if profile_name.lower() == name.lower():
                profile = self.profiles[profile_name]
                self.name = profile_name
                self.age = profile['age']
                self.interests = profile['interests']
                print(f"{profile_name}'s profile has been activated!")
                self.text_to_speech(f"{profile_name}'s profile has been activated!")
                return True
        print(f"{name}'s profile does not exist. Please enter a valid Name.")
        self.text_to_speech(f"{name}'s profile does not exist. Please enter a valid Name.")
        return False


    def edit_profile(self, name, field, new_value):
        for profile_name in self.profiles:
            if profile_name.lower() == name.lower():
                if field in self.profiles[profile_name]:
                    self.profiles[profile_name][field] = new_value
                    print(f"{profile_name}'s profile has been updated!")
                    self.save_profiles()
                    self.text_to_speech(f"{profile_name}'s profile has been updated!")

                    # Perform TTS and save as WAV
                    self.text_to_speech(f"{profile_name}'s profile has been updated!")

                    return True
                else:
                    print(f"{field} is not a valid field in {profile_name}'s profile.")
                    self.text_to_speech(f"{field} is not a valid field in {profile_name}'s profile.")
                    return False
        print(f"{name}'s profile does not exist. Please enter a valid Name.")
        self.text_to_speech(f"{name}'s profile does not exist. Please enter a valid Name.")
        return False

    def view_profiles(self):
        print("User Profiles:")
        for profile_name in self.profiles:
            profile = self.profiles[profile_name]
            print(f"Name: {profile_name}, Age: {profile['age']}, Interests: {profile['interests']}")
            self.text_to_speech(f"Name: {profile_name}, Age: {profile['age']}, Interests: {profile['interests']}")

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
            user_input = self.speech_to_text()
            if user_input.lower() == "quit" or user_input.lower() == "exit":
                break

            response = self.chat(user_input)
            print("ChatGPT: ", response)
    
    

# Example usage
file_path = "user_profiles.json"
user_manager = UserProfileManager(file_path)
first_time = True
activate = False
choice = True
while True:
    if first_time == True:
        user_manager.text_to_speech("1. Create Profile\n2. Activate Profile\n3. Edit Profile\n4. View Profiles\n5. Exit")
        user_manager.text_to_speech("Please pick an option by speaking:")
        first_time = False
    elif first_time == False:
        user_manager.text_to_speech("Please pick one of the options.")
    choice = user_manager.speech_to_text()

    if choice is None:
        user_manager.text_to_speech("None were picked")
        continue

    choice = choice.lower()

    if "1" in choice or "one" in choice or "create" in choice or "number one" in choice:
        print("Okay, I'll create a new profile. Please tell me the name, age, and interests for the profile.")
        user_manager.text_to_speech("What is the name of the new profile?")
        name = user_manager.speech_to_text()
        if name is None:
            break
        user_manager.text_to_speech("What is the age of the new profile?")
        age = user_manager.speech_to_text()
        if age is None:
            continue
        user_manager.text_to_speech("What are the interests of the new profile?")
        interests = user_manager.speech_to_text()
        if interests is None:
            continue
        user_manager.create_profile(name, age, interests)
    elif "2" in choice or "two" in choice or "activate" in choice or "number two" in choice:
        activated = True
        user_manager.text_to_speech("What is the name of the profile you want to activate?")
        name = user_manager.speech_to_text()
        if name is None:
            continue
        user_manager.text_to_speech(f"Activating profile for {name}.")
        user_manager.activate_profile(name)
        user_manager.chat_with_gpt()
    elif "3" in choice or "three" in choice or "edit" in choice or "number three" in choice:
        user_manager.text_to_speech("What is the name of the profile you want to edit?")
        name = user_manager.speech_to_text()
        if name is None:
            continue
        user_manager.text_to_speech("Which field of the profile would you like to edit, (age or interests)?")
        field = user_manager.speech_to_text()
        if field is None:
            continue
        user_manager.text_to_speech(f"What is the new value for {field}?")
        new_value = user_manager.speech_to_text()
        if new_value is None:
            continue
        user_manager.edit_profile(name, field, new_value)
    elif "4" in choice or "four" in choice or "view" in choice or "number four" in choice:
        user_manager.view_profiles()
    elif "5" in choice or "five" in choice or "exit" in choice or "number five" in choice:
        user_manager.text_to_speech("Exiting the program. Goodbye!")
        import time
        time.sleep(1.5)
        break
    else:
        user_manager.text_to_speech("Invalid choice. Please enter a valid option.")



