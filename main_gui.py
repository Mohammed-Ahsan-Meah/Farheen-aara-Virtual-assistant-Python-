import tkinter as tk
from tkinter import scrolledtext
import webbrowser
import os
import datetime
import random
import logging
import pyttsx3
import speech_recognition as sr
import json
from threading import Thread
import time
import pygame
import sys

# ------------------------ Setup ------------------------
logging.basicConfig(filename="VA_log.txt", level=logging.INFO,
                    format="%(asctime)s - %(message)s")

engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 150)

if getattr(sys, 'frozen', False):
    MEDIA_PATH = os.path.join(sys._MEIPASS, "media")
else:
    MEDIA_PATH = os.path.join(os.getcwd(), "media")

MEMORY_FILE = "va_memory.json"
current_music = None
pygame.mixer.init()

# ------------------------ Memory ------------------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"name": None, "mood": None, "last_command": None,
            "favorite_songs": [], "favorite_websites": [],
            "jokes": [], "tasks": []}

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

memory = load_memory()

# ------------------------ Apps & Websites ------------------------
apps = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "wordpad": "write.exe",
    "command prompt": "cmd.exe",
    "file explorer": "explorer.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "vlc": r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "spotify": r"C:\Users\HP\AppData\Roaming\Spotify\Spotify.exe",
    "zoom": r"C:\Users\HP\AppData\Roaming\Zoom\bin\Zoom.exe",
    "telegram": r"C:\Users\HP\AppData\Roaming\Telegram Desktop\Telegram.exe"
}

websites = {
    "youtube": "https://www.youtube.com",
    "youtube music": "https://music.youtube.com",
    "facebook": "https://www.facebook.com",
    "google": "https://www.google.com",
    "chat gpt": "https://chat.openai.com",
    "radio": "https://www.internet-radio.com",
    "instagram": "https://www.instagram.com",
    "twitter": "https://twitter.com",
    "linkedin": "https://www.linkedin.com",
    "netflix": "https://www.netflix.com",
    "amazon": "https://www.amazon.com",
    "flipkart": "https://www.flipkart.com",
    "spotify": "https://open.spotify.com",
    "reddit": "https://www.reddit.com",
    "pinterest": "https://www.pinterest.com",
    "wikipedia": "https://www.wikipedia.org"
}

# ------------------------ Predefined Responses ------------------------
responses = {
    "greetings": ["Hello! How are you today?", "Hi there! Hope you’re having a great day!", "Hey! What’s up?"],
    "farewells": ["Goodbye! See you later!", "Bye! Take care!", "See you soon!"],
    "how_are_you": ["I’m doing great! How about you?", "Feeling awesome today!", "I’m fine, thanks!"],
    "jokes": [
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the math book look sad? Because it had too many problems!"
    ],
    "default": ["I’m not sure about that. Can you try asking differently?", "Hmm… I don’t know, but I’m learning!"]
}

def get_response(category="default"):
    if category in responses:
        return random.choice(responses[category])
    return random.choice(responses["default"])

# ------------------------ Speak Functions ------------------------
def speak(text):
    output_text.configure(state="normal")
    output_text.insert(tk.END, f"VA: {text}\n")
    output_text.see(tk.END)
    output_text.configure(state="disabled")
    engine.say(text)
    engine.runAndWait()

def speak_async(text):
    Thread(target=lambda: speak(text)).start()

# ------------------------ Button Sound ------------------------
def play_button_sound():
    click_file = os.path.join(MEDIA_PATH, "click.mp3")
    if os.path.exists(click_file):
        pygame.mixer.Sound(click_file).play()

# ------------------------ Background Music ------------------------
bg_music_playing = True
def play_background_music():
    bg_file = os.path.join(MEDIA_PATH, "Futuristic Technology Background Music.wav")
    if os.path.exists(bg_file):
        pygame.mixer.music.load(bg_file)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)
    else:
        speak_async("Background music file not found.")

def toggle_background_music():
    global bg_music_playing
    play_button_sound()
    if bg_music_playing:
        pygame.mixer.music.pause()
        bg_music_playing = False
        bg_music_button.config(text="Background Music ON")
        speak_async("Background music paused.")
    else:
        pygame.mixer.music.unpause()
        bg_music_playing = True
        bg_music_button.config(text="Background Music OFF")
        speak_async("Background music resumed.")

# ------------------------ Logging ------------------------
def log_command(command):
    memory["last_command"] = command
    save_memory()
    logging.info(command)

# ------------------------ Personality ------------------------
personality = {"friendly":0.7, "sarcastic":0.2, "emotional":0.1}
def pick_personality():
    r = random.random()
    if r < personality["friendly"]: return "friendly"
    elif r < personality["friendly"] + personality["sarcastic"]: return "sarcastic"
    else: return "emotional"

# ------------------------ Greetings ------------------------
def greetings():
    hour = datetime.datetime.now().hour
    name = memory.get("name") or "friend"
    if hour<12: greet = f"Good morning, {name}! 🌞"
    elif hour<=16: greet = f"Good afternoon, {name}! 🌤"
    else: greet = f"Good evening, {name}! 🌙"
    speak_async(greet)

def verbose_greeting(command):
    name = memory.get("name") or "friend"
    p = pick_personality()
    if "hi" in command.lower() or "hello" in command.lower():
        if p == "friendly":
            speak_async(f"Hey {name}! 🌞 It’s great to see you! How’s your day?")
        elif p == "sarcastic":
            speak_async(f"Oh, it’s you again, {name} 🙄. Ready to chat?")
        else:
            speak_async(f"Hi {name}! 😊 How are you feeling today?")
        return True
    return False

# ------------------------ Date & Time ------------------------
def show_datetime():
    dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    speak_async(f"Current date and time is {dt_str}")

# ------------------------ Calculator ------------------------
def calculate_expression(expr):
    try:
        result = eval(expr)
        speak_async(f"The result is {result}")
    except:
        speak_async("I cannot calculate that. Check your expression.")

# ------------------------ Open Programs/Websites ------------------------
def open_program_or_website(target):
    target_lower = target.lower()
    if target_lower.startswith("search"):
        query = target_lower.replace("search","").strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            speak_async(f"Searching Google for: {query}")
        else:
            speak_async("Please tell me what to search for.")
        return
    if target_lower in websites:
        webbrowser.open(websites[target_lower])
        if target_lower not in memory["favorite_websites"]:
            memory["favorite_websites"].append(target_lower)
            save_memory()
        speak_async(f"Opening {target_lower}")
    elif target_lower in apps:
        try:
            os.startfile(apps[target_lower])
            speak_async(f"Launching {target_lower}")
        except:
            speak_async(f"Cannot open {target_lower}")
    else:
        speak_async("Program or website not found.")

# ------------------------ Music ------------------------
def play_music():
    global current_music
    music_file = os.path.join(MEDIA_PATH, "music.mp3")
    if os.path.exists(music_file):
        current_music = music_file
        os.startfile(music_file)
        if music_file not in memory["favorite_songs"]:
            memory["favorite_songs"].append(music_file)
            save_memory()
        speak_async("Playing music! 🎵")
    else:
        speak_async("Music file not found!")

def stop_music():
    global current_music
    if current_music:
        os.system("taskkill /im wmplayer.exe /f")
        speak_async("Music stopped.")
        current_music = None
    else:
        speak_async("No music playing currently.")

def volume_up():
    current_volume = pygame.mixer.music.get_volume()
    pygame.mixer.music.set_volume(min(current_volume + 0.1, 1.0))
    speak_async(f"Volume increased to {int(pygame.mixer.music.get_volume()*100)}%")

def volume_down():
    current_volume = pygame.mixer.music.get_volume()
    pygame.mixer.music.set_volume(max(current_volume - 0.1, 0.0))
    speak_async(f"Volume decreased to {int(pygame.mixer.music.get_volume()*100)}%")

# ------------------------ Jokes ------------------------
def tell_joke():
    if memory["jokes"]:
        joke = random.choice(memory["jokes"])
        speak_async(f"Here's a joke: {joke}")
    else:
        speak_async("I don't know any jokes yet. Teach me one!")

def teach_joke(joke):
    if joke:
        memory["jokes"].append(joke)
        save_memory()
        speak_async("Joke added! 😄")
    else:
        speak_async("Please tell me the joke.")

# ------------------------ Tasks ------------------------
def add_task(time_str,message):
    memory["tasks"].append({"time":time_str,"message":message})
    save_memory()
    speak_async(f"Task added: '{message}' at {time_str}")

def remove_task(index):
    if 0<=index<len(memory["tasks"]):
        task = memory["tasks"].pop(index)
        save_memory()
        speak_async(f"Removed task: '{task['message']}' scheduled at {task['time']}")
    else: speak_async("Invalid task number.")

def list_tasks():
    if memory["tasks"]:
        task_list = "Scheduled tasks:\n"
        for i, task in enumerate(memory["tasks"]):
            task_list += f"{i+1}. {task['time']} - {task['message']}\n"
        speak_async(task_list)
    else:
        speak_async("No tasks scheduled.")

def check_tasks():
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        for task in memory.get("tasks",[]):
            if task["time"] == now:
                speak_async(f"Reminder! {task['message']} ⏰")
        time.sleep(60)

Thread(target=check_tasks,daemon=True).start()

# ------------------------ Shutdown Timer ------------------------
def shutdown_on_gui():
    try:
        minutes = int(shutdown_entry.get())
        os.system(f"shutdown /s /t {minutes*60}")
        speak_async(f"PC will shutdown in {minutes} minutes.")
    except:
        speak_async("Enter a valid number for minutes.")

def shutdown_off_gui():
    os.system("shutdown /a")
    speak_async("Shutdown canceled.")

# ------------------------ Command Handling ------------------------
def handle_command(command):
    log_command(command)
    cmd = command.lower()

    if verbose_greeting(command):
        return

    if "how are you" in cmd:
        speak_async(get_response("how_are_you"))
        return
    elif "joke" in cmd:
        tell_joke()
        return
    elif "bye" in cmd or "exit" in cmd:
        speak_async(get_response("farewells"))
        root.destroy()
        return
    elif "hi" in cmd or "hello" in cmd:
        speak_async(get_response("greetings"))
        return
    elif "play music" in cmd:
        play_music()
        return
    elif "stop music" in cmd:
        stop_music()
        return
    elif "calculate" in cmd:
        calculate_expression(cmd.replace("calculate","").strip())
        return
    elif "open" in cmd or "launch" in cmd:
        open_program_or_website(cmd.replace("open","").replace("launch","").strip())
        return
    elif "time" in cmd or "date" in cmd:
        show_datetime()
        return
    else:
        speak_async(get_response("default"))

# ------------------------ Input / Voice ------------------------
def process_input():
    command = user_input.get(); user_input.set("")
    output_text.configure(state="normal")
    output_text.insert(tk.END,f"You: {command}\n")
    output_text.see(tk.END)
    output_text.configure(state="disabled")
    Thread(target=handle_command,args=(command,)).start()

def listen_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        output_text.configure(state="normal")
        output_text.insert(tk.END,"Listening...\n")
        output_text.see(tk.END)
        output_text.configure(state="disabled")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source,timeout=5)
            command = r.recognize_google(audio)
            user_input.set(command)
            process_input()
        except sr.WaitTimeoutError:
            speak_async("I didn't hear anything.")
        except sr.UnknownValueError:
            speak_async("Sorry, I could not understand.")
        except sr.RequestError:
            speak_async("Could not request results; check internet connection.")

# ------------------------ GUI ------------------------
root = tk.Tk()
root.title("Virtual Assistant")
root.geometry("750x650")  # Fit all buttons neatly

# Output area
output_text = scrolledtext.ScrolledText(root, state="disabled", wrap=tk.WORD)
output_text.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

# User input
user_input = tk.StringVar()
input_entry = tk.Entry(root, textvariable=user_input)
input_entry.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
input_entry.bind("<Return>", lambda e: process_input())

send_button = tk.Button(root, text="Send", command=process_input)
send_button.grid(row=1, column=3, padx=5, pady=5)

voice_button = tk.Button(root, text="🎤 Speak", command=listen_command)
voice_button.grid(row=1, column=4, padx=5, pady=5)

# Music controls
play_music_button = tk.Button(root, text="Play Music", command=play_music)
play_music_button.grid(row=2, column=0, padx=5, pady=5)

stop_music_button = tk.Button(root, text="Stop Music", command=stop_music)
stop_music_button.grid(row=2, column=1, padx=5, pady=5)

bg_music_button = tk.Button(root, text="Background Music OFF", command=toggle_background_music)
bg_music_button.grid(row=2, column=2, padx=5, pady=5)

vol_up_button = tk.Button(root, text="Volume +", command=volume_up)
vol_up_button.grid(row=2, column=3, padx=5, pady=5)

vol_down_button = tk.Button(root, text="Volume -", command=volume_down)
vol_down_button.grid(row=2, column=4, padx=5, pady=5)

# Shutdown controls
shutdown_entry = tk.Entry(root, width=10)
shutdown_entry.grid(row=3, column=0, padx=5, pady=5)
shutdown_entry.insert(0, "1")  # default 1 minute

shutdown_on_button = tk.Button(root, text="Shutdown ON", command=shutdown_on_gui)
shutdown_on_button.grid(row=3, column=1, padx=5, pady=5)

shutdown_off_button = tk.Button(root, text="Shutdown OFF", command=shutdown_off_gui)
shutdown_off_button.grid(row=3, column=2, padx=5, pady=5)

# Make grid expand properly
for i in range(5):
    root.grid_columnconfigure(i, weight=1)
root.grid_rowconfigure(0, weight=1)

# Start background music & greeting
root.after(100, play_background_music)
greetings()
root.mainloop()
