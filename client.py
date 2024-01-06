# Copyright (c) 2023 Braedon Hendy
# This software is released under the GNU General Public License v3.0

import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog
import requests
import pyperclip
import wave
import threading
import numpy as np
import base64
import json
import pyaudio 
import threading


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
AISCRIBE = "AI, please transform the following conversation into a concise SOAP note. Do not invent or assume any medical data, vital signs, or lab values. Base the note strictly on the information provided in the conversation. Ensure that the SOAP note is structured appropriately with Subjective, Objective, Assessment, and Plan sections. Here's the conversation:"
AISCRIBE2 = "Remember, the Subjective section should reflect the patient's perspective and complaints as mentioned in the conversation. The Objective section should only include observable or measurable data from the conversation. The Assessment should be a summary of your understanding and potential diagnoses, considering the conversation's content. The Plan should outline the proposed management or follow-up required, strictly based on the dialogue provided"
uploaded_file_path = None

# Function to get prompt for KoboldAI Generation
def get_prompt(text): # For KoboldAI Generation
    return {
        "prompt": f"{text}\n",
        "use_story": False, #Needs to be set in KoboldAI webUI
        "use_memory": False, #Needs to be set in KoboldAI webUI
        "use_authors_note": False, #Needs to be set in KoboldAI webUI
        "use_world_info": False, #Needs to be set in KoboldAI webUI
        "max_context_length": 2048,
        "max_length": 320,
        "rep_pen": 1.0,
        "rep_pen_range": 2048,
        "rep_pen_slope": 0.7,
        "temperature": 0.1,
        "tfs": 0.97,
        "top_a": 0.8,
        "top_k": 0,
        "top_p": 0.5,
        "typical": 0.19,
        "sampler_order": [6,0,1,3,4,2,5], 
        "singleline": False,
        "sampler_seed": 69420, # Use specific seed for text generation?
        "sampler_full_determinism": False, # Always give same output with same settings?
        "frmttriminc": False, #Trim incomplete sentences
        "frmtrmblln": False, #Remove blank lines
        "stop_sequence": ["\n\n\n\n\n"]
    }

def threaded_handle_message(user_message):
    thread = threading.Thread(target=handle_message, args=(user_message,))
    thread.start()

def threaded_send_audio_to_server():
    thread = threading.Thread(target=send_audio_to_server)
    thread.start()

# Function to handle message
def handle_message(user_message):
    prompt = get_prompt(user_message)
    response = requests.post(f"{KOBOLDCPP}/api/v1/generate", json=prompt)
    if response.status_code == 200:
        results = response.json()['results']
        response_text = results[0]['text']
        response_text = response_text.replace("  ", " ").strip() 
        update_gui_with_response(response_text)

# Modified send_and_receive function
def send_and_receive():
    global use_aiscribe
    user_message = user_input.get("1.0", tk.END).strip()
    clear_response_display()    
    if use_aiscribe:
        formatted_message = f'{AISCRIBE} [{user_message}] {AISCRIBE2}'
    else:
        formatted_message = user_message
    threaded_handle_message(formatted_message)
    
def clear_response_display():
    response_display.configure(state='normal')
    response_display.delete("1.0", tk.END)
    response_display.configure(state='disabled') 

def update_gui_with_response(response_text):
    response_display.configure(state='normal')
    response_display.insert(tk.END, f"{response_text}\n")
    response_display.configure(state='disabled')
    pyperclip.copy(response_text)
    stop_flashing()    


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
is_paused = False

# Toggle switch variable
use_aiscribe = True  # Default state of the toggle

# Function to record audio
def toggle_pause():
    global is_paused
    is_paused = not is_paused

    if is_paused:
        pause_button.config(text="Resume", bg="red")
        # The actual pause functionality will be handled in the record_audio function
    else:
        pause_button.config(text="Pause", bg="SystemButtonFace")
        # The actual resume functionality will also be handled in the record_audio function

# Function to record audio
def record_audio():
    global is_paused, frames
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    while is_recording:
        if not is_paused:
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
        threaded_send_audio_to_server()

# Function to toggle recording
def toggle_recording():
    global is_recording, recording_thread
    if not is_recording:
        # Clear the user_input and response_display textboxes
        # This code runs only when the recording is about to start
        user_input.delete("1.0", tk.END)
        response_display.configure(state='normal')
        response_display.delete("1.0", tk.END)
        response_display.configure(state='disabled')
        is_recording = True
        recording_thread = threading.Thread(target=record_audio)
        recording_thread.start()
        toggle_mic_button_color()  # Change the button color to indicate recording
        start_flashing()
    else:
        is_recording = False
        if recording_thread.is_alive():
            recording_thread.join()  # Ensure the recording thread is terminated
        save_audio()
        toggle_mic_button_color()  # Reset the button color       
       
def clear_all_text_fields():
    user_input.configure(state='normal')  # Ensure the widget is editable
    user_input.delete("1.0", tk.END)
    stop_flashing()
    # user_input.configure(state='disabled')  # Comment out or remove this line

    response_display.configure(state='normal')
    response_display.delete("1.0", tk.END)
    response_display.configure(state='disabled')

# Toggle AISCRIBE constant function
def toggle_aiscribe():
    global use_aiscribe
    use_aiscribe = not use_aiscribe
    toggle_button.config(text="AISCRIBE: ON" if use_aiscribe else "AISCRIBE: OFF")

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
    
def upload_file():
    global uploaded_file_path
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if file_path:
        uploaded_file_path = file_path
        threaded_send_audio_to_server()  # Add this line to process the file immediately

# Modified send_audio_to_server function
def send_audio_to_server():
    global uploaded_file_path
    if uploaded_file_path:
        file_to_send = uploaded_file_path
        uploaded_file_path = None  # Reset after using
    else:
        file_to_send = 'recording.wav'

    with open(file_to_send, 'rb') as f:
        files = {'audio': f}
        response = requests.post(WHISPERAUDIO, files=files)
        if response.status_code == 200:
            transcribed_text = response.json()['text']
            # Set the transcribed text as user input
            user_input.delete("1.0", tk.END)
            user_input.insert(tk.END, transcribed_text)
            # Call send_and_receive to process this input
            send_and_receive()

is_flashing = False

def start_flashing():
    global is_flashing
    is_flashing = True
    flash_circle()

def stop_flashing():
    global is_flashing
    is_flashing = False
    blinking_circle_canvas.itemconfig(circle, fill='white')  # Reset to default color

def flash_circle():
    if is_flashing:
        current_color = blinking_circle_canvas.itemcget(circle, 'fill')
        new_color = 'blue' if current_color != 'blue' else 'black'
        blinking_circle_canvas.itemconfig(circle, fill=new_color)
        root.after(1000, flash_circle)  # Adjust the flashing speed as needed

# GUI Setup
root = tk.Tk()
root.title("AI Medical Scribe")

user_input = scrolledtext.ScrolledText(root, height=15)
user_input.grid(row=0, column=0, columnspan=8, padx=5, pady=5)

mic_button = tk.Button(root, text="Microphone", command=toggle_recording, height=2, width=15)
mic_button.grid(row=1, column=0, pady=5)

# Send button
send_button = tk.Button(root, text="Send", command=send_and_receive, height=2, width=15)
send_button.grid(row=1, column=1, pady=5)

pause_button = tk.Button(root, text="Pause", command=toggle_pause, height=2, width=15)
pause_button.grid(row=1, column=2, pady=5)  # Adjust the grid position as needed

clear_button = tk.Button(root, text="Clear", command=clear_all_text_fields, height=2, width=15)
clear_button.grid(row=1, column=3, pady=5)

toggle_button = tk.Button(root, text="AISCRIBE: ON", command=toggle_aiscribe, height=2, width=15)
toggle_button.grid(row=1, column=4, pady=5)

settings_button = tk.Button(root, text="Settings", command=open_settings_window, height=2, width=15)
settings_button.grid(row=1, column=5, pady=5)  # Adjust the grid position as needed

upload_button = tk.Button(root, text="Upload WAV", command=upload_file, height=2, width=15)
upload_button.grid(row=1, column=6, pady=5)  # Adjust the grid position as needed

blinking_circle_canvas = tk.Canvas(root, width=20, height=20)
blinking_circle_canvas.grid(row=1, column=7, pady=5)
circle = blinking_circle_canvas.create_oval(5, 5, 15, 15, fill='white')

# Bind Alt+P to send_and_receive function
root.bind('<Alt-p>', lambda event: send_and_receive())

# Bind Alt+R to toggle_recording function
root.bind('<Alt-r>', lambda event: mic_button.invoke())

response_display = scrolledtext.ScrolledText(root, height=15, state='disabled')
response_display.grid(row=2, column=0, columnspan=8, padx=5, pady=5)

root.mainloop()

p.terminate()
