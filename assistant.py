import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import os
import platform
import psutil  # For system information
import tkinter as tk  # GUI
from tkinter import scrolledtext  # GUI
import threading  # GUI
import re  # Visit directly to the website when user said the domain name
import pygame
from pygame import mixer  # For inbuilt music player
import tempfile

# Initialize speech engine and music playback
engine = pyttsx3.init()
pygame.mixer.init()

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Adjust speech rate and volume
engine.setProperty('rate', 160)  # Adjust speech rate (words per minute)
engine.setProperty('volume', 1.0)  # Adjust volume (0.0 to 1.0)

root = tk.Tk()  # to run the GUI
# GUI for assistant commanding
root.title("Olivia - AI Assistant")
root.geometry("950x600")
root.configure(bg='black')

# Add a label for the title
title_label = tk.Label(root, text="Olivia - Your AI Assistant", font=("Helvetica", 16, "bold"), fg='white', bg='black')
title_label.pack(pady=10)

text_display = scrolledtext.ScrolledText(root, height=25, width=100, font=("Helvetica", 12), wrap=tk.WORD, bg='black',
                                        fg='red')
text_display.pack(pady=10)
text_display.config(state=tk.DISABLED)  # read-only activate

# Function to insert text with a specific color
def insert_text(text, color):
    text_display.config(state=tk.NORMAL)  # Enable the text display to insert text
    text_display.insert(tk.END, text, color)
    text_display.see(tk.END)
    text_display.config(state=tk.DISABLED)  # read-only


# Tag configurations for text colors
text_display.tag_configure("user", foreground="blue")
text_display.tag_configure("assistant", foreground="green")
text_display.tag_configure("listening", foreground="white")


# Function to speak out text and display it on GUI
def speak(text, silent=False):
    if not silent:
        insert_text(f"Olivia: {text}\n\n", "assistant")
        root.update_idletasks()  # Update the GUI to reflect changes immediately
        engine.say(text)
        engine.runAndWait()


# Function to recognize speech using Google Speech Recognition
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)  # Adjust for ambient noise for 1 second
        insert_text("Listening...\n", "listening")  # Display listening process on GUI
        root.update_idletasks()  # Update the GUI to reflect changes immediately
        try:
            audio = r.listen(source, phrase_time_limit=5)  # Listen with a phrase time limit of 5 seconds
            statement = r.recognize_google(audio, language='en-in')
            print(f"User said: {statement}\n")
            insert_text(f"User: {statement}\n\n", "user")
            root.update_idletasks()  # Update the GUI to reflect changes immediately
        except sr.RequestError:
            speak("Sorry, I am having trouble connecting to the internet.", silent=True)
            return "None"
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.", silent=True)
            return "None"
        except sr.WaitTimeoutError:
            speak("Listening timed out. Please try again.", silent=True)
            return "None"
        except Exception as e:
            print(e)
            speak("Sorry, I couldn't process that. Please try again.", silent=True)
            return "None"
        return statement.lower()


# Function to get the current date and time
def get_datetime():
    now = datetime.datetime.now()
    date = now.strftime("%A, %B %d, %Y")
    time = now.strftime("%I:%M %p")
    return date, time


# Function to get computer specifications
def get_computer_specs():
    specs = platform.uname()
    system = f"You are using {specs.system}"
    node = f"Node name: {specs.node}"
    release = f"Release: {specs.release}"
    version = f"Version: {specs.version}"
    machine = f"Machine: {specs.machine}"
    processor = f"Processor: {specs.processor}"

    # Additional system information (RAM, GPU, STORAGE)
    memory = f"RAM: {psutil.virtual_memory().total / (1024 ** 3):.2f} GB"

    try:
        gpu = [x.name for x in psutil.sensors_gpu()]
        gpu_info = f"GPU: {', '.join(gpu)}"
    except Exception as e:
        gpu_info = "GPU: Not available"

    partitions = psutil.disk_partitions()
    storage_info = []
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            storage_info.append(f"{partition.device} - Total: {partition_usage.total / (1024 ** 3):.2f} GB")
        except Exception as e:
            continue

    storage = "Storage: " + ", ".join(storage_info)

    return f"{system}. {node}. {release}. {version}. {machine}. {processor}. {memory}. {gpu_info}. {storage}."


# Name of Olivia
def name_olivia():
    speak("My name is Olivia")


# Function to identify Olivia
def identify_olivia():
    speak("I am Olivia, your personal AI assistant. I can perform the following tasks: provide the current time and date, fetch computer specifications, search the web on Google, and play music from YouTube. However, I cannot set alarms at the moment.")


# Function to list capabilities
def list_capabilities():
    speak("I can perform the following tasks: provide the current time and date, fetch computer specifications, search the web on Google, and play music from YouTube. However, I cannot set alarms at the moment.")


# Function to search on Google
def search_google(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open_new(url)
    speak(f"Here are the search results for {query} on Google.", silent=False)


# Global variable to track music playing status
music_playing = False
# GUI to show play music
music_status_label = tk.Label(root, text="", font=("Helvetica", 12), fg='green', bg='black')
music_status_label.pack(pady=10)


def play_music_inbuilt(song_name):
    global music_playing
    try:
        speak(f"Searching for {song_name} in local music library.", silent=False)

        # Path
        music_directory = r"C:\Users\Pc\Music"

        # Check
        music_files = [f for f in os.listdir(music_directory) if f.endswith(".mp3")]

        # Search for the song name in the list of music files
        found = False
        for music_file in music_files:
            if song_name.lower() in music_file.lower():
                music_path = os.path.join(music_directory, music_file)
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play()
                music_playing = True
                speak(f"Playing {music_file} in the inbuilt music player.", silent=False)
                music_status_label.config(text="Music is now playing")
                found = True
                break

        if not found:
            speak(f"Sorry, I couldn't find {song_name} in your music library.", silent=False)
    except Exception as e:
        speak("Sorry, I couldn't play the music. Please try again later.", silent=False)
        print(str(e))


# Function to visit website
def visit_website(url):
    webbrowser.open_new(url)
    speak(f"Opening {url}.", silent=False)


# Function to open help_me.txt file
def open_help_file():
    try:
        help_file_path = r"assets/help_me.txt"  # Change this to the actual file path
        os.startfile(help_file_path)
        speak("Opening help file.", silent=False)
    except Exception as e:
        speak("Sorry, I couldn't open the help file. Please check the file path.", silent=False)
        print(str(e))


# Function to respond to time-specific greetings
def respond_to_greeting(greeting):
    if "morning" in greeting:
        speak("Good morning! Have a lovely day.", silent=False)
    elif "afternoon" in greeting:
        speak("Good afternoon! How can I assist you?", silent=False)
    elif "evening" in greeting:
        speak("Good evening! I hope you had a great day.", silent=False)
    elif "night" in greeting:
        speak("Good night! Sweet dreams.", silent=False)
    elif "how are you" in greeting:
        speak("I'm fine.", silent=False)
    elif "thank you" in greeting or "thanks" in greeting:
        speak("You're welcome sir", silent=False)
    elif "nice to meet you" in greeting:
        speak("Nice to meet you too!", silent=False)


# Assistant listener
def assistant_listener():
    global music_playing
    active = True

    while True:
        if active:
            statement = get_audio()

            if "stop music" in statement:
                pygame.mixer.music.stop()
                music_playing = False
                music_status_label.config(text="")
                speak("Music stopped.", silent=False)
                continue

            if "pause" in statement or "pause music" in statement:
                pygame.mixer.music.pause()
                music_status_label.config(text="Music paused")
                speak("Music paused.", silent=music_playing)
                continue

            if "resume" in statement or "resume music" in statement:
                pygame.mixer.music.unpause()
                music_status_label.config(text="Music playing")
                speak("Music resumed.", silent=False)
                continue

            if statement == "none":
                continue

            if "goodbye" in statement or "ok bye" in statement:
                speak("Goodbye! Have a nice day.", silent=False)
                active = False
                root.quit()
                return

            if "exit olivia" in statement or "exit" in statement:
                speak("Exiting. Goodbye sir!", silent=False)
                root.quit()
                return

            if "hey olivia" in statement:
                speak("Yes sir, how can I help you?", silent=music_playing)
                active = True
                continue

            if "play music" in statement or "play song" in statement or "listen song" in statement:
                speak("What song would you like to play?", silent=music_playing)
                song_name = get_audio().lower()
                if song_name == "none":
                    continue
                play_music_inbuilt(song_name)

            if "time" in statement:
                _, time = get_datetime()
                speak(f"The current time is {time}.", silent=music_playing)

            elif "date" in statement:
                date, _ = get_datetime()
                speak(f"Today is {date}.", silent=music_playing)

            elif "computer specification" in statement or "computer specs" in statement:
                specs = get_computer_specs()
                speak(specs, silent=music_playing)

            elif "search on google" in statement:
                query = statement.replace("search on google", "").strip()
                search_google(query)
                continue

            elif "set an alarm" in statement or "alarm" in statement:
                speak("Now in that version I can't set alarm for time. Look for future upgrades", silent=music_playing)
            elif "search" in statement:
                query = statement.replace("search", "").strip()
                search_google(query)
                continue

            elif "your name" in statement or "introduce yourself" in statement:
                name_olivia()

            elif "identify" in statement or "who are you" in statement:
                identify_olivia()

            elif "what can you do" in statement or "what do you do" in statement:
                list_capabilities()

            elif "help me" in statement or "help me olivia" in statement:
                open_help_file()

            elif re.match(r"www\.\w+\.\w+", statement):
                visit_website(statement)

            elif any(greet_word in statement for greet_word in
                     ["good morning", "good afternoon", "good evening", "good night", "how are you", "thank",
                      "nice to meet you"]):
                respond_to_greeting(statement)

            else:
                # speak("I'm sorry, Can you please repeat?", silent=music_playing)
                # insert_text("I'm sorry, Can you please repeat?\n", "assistant")
                None
        else:
            statement = get_audio()
            if "hey olivia" in statement or "olivia" in statement:
                speak("Yes sir, how can I help you?", silent=music_playing)
                active = True


# Function to introduce Olivia
def Olivia_Assistant():
    speak("Hello, I am Olivia, your personal assistant.")
    speak("How can I assist you today?")
    assistant_listener()


assistant_thread = threading.Thread(target=Olivia_Assistant)
assistant_thread.daemon = True
assistant_thread.start()

# Start the GUI main loop
root.mainloop()
