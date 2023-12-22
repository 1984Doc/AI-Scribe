# Copyright (c) 2023 Braedon Hendy
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import tkinter as tk
from tkinter import scrolledtext, ttk
import requests
import pyperclip
import wave
import threading
import numpy as np
import base64
import json
import pyaudio 


# Function to build the full URL from IP
def build_url(ip, port):
    return f"http://{ip}:{port}"

# Function to save settings to a file
def save_settings_to_file(koboldcpp_ip, whisperaudio_ip):
    with open('settings.txt', 'w') as file:
        file.write(f"{koboldcpp_ip}\n{whisperaudio_ip}")

# Function to load settings from a file
def load_settings_from_file():
    try:
        with open('settings.txt', 'r') as file:
            lines = file.readlines()
            return lines[0].strip(), lines[1].strip()
    except FileNotFoundError:
        # Return default values if file not found
        return "192.168.1.195", "192.168.1.195"

# Load settings at the start
KOBOLDCPP_IP, WHISPERAUDIO_IP = load_settings_from_file()
KOBOLDCPP = build_url(KOBOLDCPP_IP, "5001")
WHISPERAUDIO = build_url(WHISPERAUDIO_IP, "8000/whisperaudio")

# Other constants and global variables
username = "user"
botname = "Assistant"
num_lines_to_keep = 20
AISCRIBE = "The following is a real conversation between a patient and their doctor. As a doctor, write this as a SOAP formatted medical note with sections for Subjective, Objective, Assessment, and Plan.  Put a blank line between each section. Be detailed and thorough.  Only use information that is present in the conversation and only present vitals that are stated.\n\n  Desired format:\n\n   Subjective: <List all subjective findings as per a medical SOAP note. Include everything reported by the patient in detail.>\n\n  Objective:  <Objective findings as per a medical SOAP note, including such as any physical exam findings, measurements, and vitals.>\n\n  Assessment: <Detail the assessment of the patient by the doctor.>\n\n  Plan: <Plan for treatment and next steps to be taken by the doctor and patient.>\n\n"
global conversation_history

# Function to split the text
def split_text(text):
    parts = re.split(r'\n[a-zA-Z]', text)
    return parts

# Function to get prompt for KoboldAI Generation
def get_prompt(conversation_history, username, text): # For KoboldAI Generation
    return {
        "prompt": conversation_history + f"{username}: {text}\n{botname}:",
        "use_story": False,
        "use_memory": True,
        "use_authors_note": True,  # Enabled to guide AI for focused responses
        "use_world_info": False,
        "max_context_length": 2048,  # Large enough to retain relevant context
        "max_length": 360, #prev 240
        "rep_pen": 1.2,  # Slightly increased repetition penalty
        "rep_pen_range": 2048,
        "rep_pen_slope": 0.7,
        "temperature": 0.6,  # Lowered for more predictable responses
        "tfs": 0.97,
        "top_a": 0.8,
        "top_k": 30,  # Adjusted for controlled diversity
        "top_p": 0.4,  # Lowered for more focused responses
        "typical": 0.19,
        "sampler_order": [6, 0, 1, 3, 4, 2, 5],
        "singleline": False,
        "frmttriminc": False,
        "frmtrmblln": False
    }
# Load existing conversation history from file
with open(f'conv_history_{botname}_terminal.txt', 'a+') as file:
    file.seek(0)
    conversation_history = file.read()

# Function to handle message
def handle_message(user_message):
    global conversation_history
    # Reset conversation history for each new chat
    conversation_history = ""

    prompt = get_prompt(conversation_history, username, user_message)
    response = requests.post(f"{KOBOLDCPP}/api/v1/generate", json=prompt)
    if response.status_code == 200:
        results = response.json()['results']
        response_text = results[0]['text']
        response_text = response_text.replace("  ", " ").strip()  # Removing the split_text function
        update_gui_with_response(response_text)
# GUI Functions
def send_and_receive():
    user_message = user_input.get("1.0", tk.END).strip()
    clear_response_display()
    formatted_message = f'{AISCRIBE}{user_message}'
    handle_message(formatted_message)
    user_input.delete("1.0", tk.END)
    
def clear_response_display():
    response_display.configure(state='normal')
    response_display.delete("1.0", tk.END)
    response_display.configure(state='disabled')
    

def update_gui_with_response(response_text):
    response_display.configure(state='normal')
    response_display.insert(tk.END, f"{botname}: {response_text}\n")
    response_display.configure(state='disabled')
    pyperclip.copy(response_text)
    
def audio_gui_with_response(response_text):
    user_input.configure(state='normal')
    user_input.insert(tk.END, f"{botname}: {response_text}\n")
    user_input.configure(state='disabled')
    pyperclip.copy(response_text)
    
    
    
# Function to toggle the background color of the microphone button
def toggle_mic_button_color():
    current_color = mic_button.cget("bg")
    new_color = "red" if current_color != "red" else "SystemButtonFace"  # Default button color
    mic_button.config(bg=new_color)
    
# Global variable to control recording state
is_recording = False
audio_data = []

# Global variables for PyAudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5

p = pyaudio.PyAudio()  # Creating an instance of PyAudio

# Other global variables
is_recording = False
frames = []

# Toggle switch variable
use_aiscribe = True  # Default state of the toggle

# Function to record audio
def record_audio():
    global frames, is_recording
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []

    while is_recording:  # Keep recording as long as is_recording is True
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()

# Function to save audio and send to server
def save_audio():
    global frames
    if frames:
        with wave.open('recording.wav', 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        frames = []  # Clear recorded data
        send_audio_to_server()

# Function to toggle recording
def toggle_recording():
    global is_recording, recording_thread
    if not is_recording:
        is_recording = True
        recording_thread = threading.Thread(target=record_audio)
        recording_thread.start()
        toggle_mic_button_color()  # Change the button color to indicate recording
    else:
        is_recording = False
        if recording_thread.is_alive():
            recording_thread.join()  # Ensure the recording thread is terminated
        save_audio()
        toggle_mic_button_color()  # Reset the button color
        
def send_audio_to_server():
    with open('recording.wav', 'rb') as f:
        files = {'audio': f}
        response = requests.post(WHISPERAUDIO, files=files)
    if response.status_code == 200:
        transcribed_text = response.json()['text']
        audio_gui_with_response(transcribed_text)  # Updated this line
        
def clear_all_text_fields():
    user_input.configure(state='normal')  # Ensure the widget is editable
    user_input.delete("1.0", tk.END)
    # user_input.configure(state='disabled')  # Comment out or remove this line

    response_display.configure(state='normal')
    response_display.delete("1.0", tk.END)
    response_display.configure(state='disabled')

# Toggle AISCRIBE constant function
def toggle_aiscribe():
    global use_aiscribe
    use_aiscribe = not use_aiscribe
    toggle_button.config(text="AISCRIBE: ON" if use_aiscribe else "AISCRIBE: OFF")

# Modified send_and_receive function
def send_and_receive():
    global use_aiscribe
    user_message = user_input.get("1.0", tk.END).strip()
    clear_response_display()
    if use_aiscribe:
        formatted_message = f'{AISCRIBE}{user_message}'
    else:
        formatted_message = user_message
    handle_message(formatted_message)
    user_input.delete("1.0", tk.END)

# Modified save_settings function with window close functionality
def save_settings(koboldcpp_ip, whisperaudio_ip, settings_window):
    global KOBOLDCPP, WHISPERAUDIO, KOBOLDCPP_IP, WHISPERAUDIO_IP
    KOBOLDCPP_IP = koboldcpp_ip
    WHISPERAUDIO_IP = whisperaudio_ip
    KOBOLDCPP = build_url(KOBOLDCPP_IP, "5001")
    WHISPERAUDIO = build_url(WHISPERAUDIO_IP, "8000/whisperaudio")
    save_settings_to_file(KOBOLDCPP_IP, WHISPERAUDIO_IP)  # Save to file
    settings_window.destroy()  # Close the settings window

# Function to open the settings window
def open_settings_window():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")

    # KOBOLDCPP IP input
    tk.Label(settings_window, text="KOBOLDCPP IP:").grid(row=0, column=0)
    koboldcpp_ip_entry = tk.Entry(settings_window, width=50)
    koboldcpp_ip_entry.insert(0, KOBOLDCPP_IP)
    koboldcpp_ip_entry.grid(row=0, column=1)

    # WHISPERAUDIO IP input
    tk.Label(settings_window, text="WHISPERAUDIO IP:").grid(row=1, column=0)
    whisperaudio_ip_entry = tk.Entry(settings_window, width=50)
    whisperaudio_ip_entry.insert(0, WHISPERAUDIO_IP)
    whisperaudio_ip_entry.grid(row=1, column=1)

    # Save button with modified command to include window close
    save_button = tk.Button(settings_window, text="Save",
                            command=lambda: save_settings(koboldcpp_ip_entry.get(), whisperaudio_ip_entry.get(), settings_window))
    save_button.grid(row=2, column=0, columnspan=2)

# GUI Setup
root = tk.Tk()
root.title("AI Medical Scribe")

# User input textbox
user_input = scrolledtext.ScrolledText(root, height=15)
user_input.grid(row=0, column=0, columnspan=5, padx=10, pady=5)

# Microphone button
mic_button = tk.Button(root, text="Microphone", command=toggle_recording, height=2, width=20)
mic_button.grid(row=1, column=0, pady=5)

# Send button
send_button = tk.Button(root, text="Send", command=send_and_receive, height=2, width=20)
send_button.grid(row=1, column=1, pady=5)

clear_button = tk.Button(root, text="Clear", command=clear_all_text_fields, height=2, width=20)
clear_button.grid(row=1, column=2, pady=5)

toggle_button = tk.Button(root, text="AISCRIBE: ON", command=toggle_aiscribe, height=2, width=20)
toggle_button.grid(row=1, column=3, pady=5)

settings_button = tk.Button(root, text="Settings", command=open_settings_window, height=2, width=20)
settings_button.grid(row=1, column=4, pady=5)  # Adjust the grid position as needed

# Bind Alt+P to send_and_receive function
root.bind('<Alt-p>', lambda event: send_and_receive())

# Bind Alt+R to toggle_recording function
root.bind('<Alt-r>', lambda event: mic_button.invoke())

# Response display textbox
response_display = scrolledtext.ScrolledText(root, height=15, state='disabled')
response_display.grid(row=2, column=0, columnspan=5, padx=10, pady=5)

root.mainloop()

p.terminate()
