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
import tkinter.messagebox as messagebox

# Add these near the top of your script
editable_settings = {
    "use_story": False,
    "use_memory": False,
    "use_authors_note": False, 
    "use_world_info": False,
    "max_context_length": 2048,
    "max_length": 360,
    "rep_pen": 1.1,  
    "rep_pen_range": 2048,
    "rep_pen_slope": 0.7,
    "temperature": 0,
    "tfs": 0.97,
    "top_a": 0.8,
    "top_k": 30,
    "top_p": 0.4,
    "typical": 0.19,
    "sampler_order": [6, 0, 1, 3, 4, 2, 5],
    "singleline": False,
    "frmttriminc": False,
    "frmtrmblln": False
}

# Function to build the full URL from IP
def build_url(ip, port):
    return f"http://{ip}:{port}"

# Function to save settings to a file
def save_settings_to_file(koboldcpp_ip, whisperaudio_ip):
    settings = {
        "koboldcpp_ip": koboldcpp_ip,
        "whisperaudio_ip": whisperaudio_ip,
        "editable_settings": editable_settings
    }
    with open('settings.txt', 'w') as file:
        json.dump(settings, file)
        
def load_settings_from_file():
    try:
        with open('settings.txt', 'r') as file:
            try:
                settings = json.load(file)
            except json.JSONDecodeError:
                return "192.168.1.195", "192.168.1.195"  # Default values if JSON is invalid

            koboldcpp_ip = settings.get("koboldcpp_ip", "192.168.1.195")
            whisperaudio_ip = settings.get("whisperaudio_ip", "192.168.1.195")
            loaded_editable_settings = settings.get("editable_settings", {})
            for key, value in loaded_editable_settings.items():
                if key in editable_settings:
                    editable_settings[key] = value
            return koboldcpp_ip, whisperaudio_ip
    except FileNotFoundError:
        # Return default values if file not found
        return "192.168.1.195", "192.168.1.195"
        
def load_aiscribe_from_file():
    try:
        with open('aiscribe.txt', 'r') as f:
            content = f.read().strip()
            return content if content else None
    except FileNotFoundError:
        return None

def load_aiscribe2_from_file():
    try:
        with open('aiscribe2.txt', 'r') as f:
            content = f.read().strip()
            return content if content else None
    except FileNotFoundError:
        return None

# Load settings at the start
KOBOLDCPP_IP, WHISPERAUDIO_IP = load_settings_from_file()
KOBOLDCPP = build_url(KOBOLDCPP_IP, "5001")
WHISPERAUDIO = build_url(WHISPERAUDIO_IP, "8000/whisperaudio")

# Other constants and global variables
username = "user"
botname = "Assistant"
num_lines_to_keep = 20
DEFAULT_AISCRIBE = "AI, please transform the following conversation into a concise SOAP note. Do not invent or assume any medical data, vital signs, or lab values. Base the note strictly on the information provided in the conversation. Ensure that the SOAP note is structured appropriately with Subjective, Objective, Assessment, and Plan sections. Here's the conversation:"
DEFAULT_AISCRIBE2 = "Remember, the Subjective section should reflect the patient's perspective and complaints as mentioned in the conversation. The Objective section should only include observable or measurable data from the conversation. The Assessment should be a summary of your understanding and potential diagnoses, considering the conversation's content. The Plan should outline the proposed management or follow-up required, strictly based on the dialogue provided"
AISCRIBE = load_aiscribe_from_file() or DEFAULT_AISCRIBE
AISCRIBE2 = load_aiscribe2_from_file() or DEFAULT_AISCRIBE2
uploaded_file_path = None

# Function to get prompt for KoboldAI Generation
def get_prompt(text):
    # Check and parse 'sampler_order' if it's a string
    sampler_order = editable_settings["sampler_order"]
    if isinstance(sampler_order, str):
        sampler_order = json.loads(sampler_order)
    return {
        "prompt": f"{text}\n",
        "use_story": editable_settings["use_story"],
        "use_memory": editable_settings["use_memory"],
        "use_authors_note": editable_settings["use_authors_note"],
        "use_world_info": editable_settings["use_world_info"],
        "max_context_length": int(editable_settings["max_context_length"]),
        "max_length": int(editable_settings["max_length"]),
        "rep_pen": float(editable_settings["rep_pen"]),
        "rep_pen_range": int(editable_settings["rep_pen_range"]),
        "rep_pen_slope": float(editable_settings["rep_pen_slope"]),
        "temperature": float(editable_settings["temperature"]),
        "tfs": float(editable_settings["tfs"]),
        "top_a": float(editable_settings["top_a"]),
        "top_k": int(editable_settings["top_k"]),
        "top_p": float(editable_settings["top_p"]),
        "typical": float(editable_settings["typical"]),
        "sampler_order": sampler_order,
        "singleline": editable_settings["singleline"],
        "frmttriminc": editable_settings["frmttriminc"],
        "frmtrmblln": editable_settings["frmtrmblln"]
    }

def threaded_handle_message(user_message):
    thread = threading.Thread(target=handle_message, args=(user_message,))
    thread.start()

def threaded_send_audio_to_server():
    thread = threading.Thread(target=send_audio_to_server)
    thread.start()

def handle_message(user_message):
    prompt = get_prompt(user_message)
    response = requests.post(f"{KOBOLDCPP}/api/v1/generate", json=prompt)
    if response.status_code == 200:
        results = response.json()['results']
        response_text = results[0]['text']
        response_text = response_text.replace("  ", " ").strip() 
        update_gui_with_response(response_text)

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

def toggle_mic_button_color():
    current_color = mic_button.cget("bg")
    new_color = "red" if current_color != "red" else "SystemButtonFace"  # Default button color
    mic_button.config(bg=new_color)
    
# Global variable to control recording state
is_recording = False
audio_data = []
frames = []
is_paused = False
use_aiscribe = True 

# Global variables for PyAudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5

p = pyaudio.PyAudio()  # Creating an instance of PyAudio

def toggle_pause():
    global is_paused
    is_paused = not is_paused

    if is_paused:
        pause_button.config(text="Resume", bg="red")
    else:
        pause_button.config(text="Pause", bg="SystemButtonFace")

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
        toggle_mic_button_color()         
       
def clear_all_text_fields():
    user_input.configure(state='normal') 
    user_input.delete("1.0", tk.END)
    stop_flashing()
    response_display.configure(state='normal')
    response_display.delete("1.0", tk.END)
    response_display.configure(state='disabled')

# Toggle AISCRIBE constant function
def toggle_aiscribe():
    global use_aiscribe
    use_aiscribe = not use_aiscribe
    toggle_button.config(text="AISCRIBE: ON" if use_aiscribe else "AISCRIBE: OFF")

def save_settings(koboldcpp_ip, whisperaudio_ip, aiscribe_text, aiscribe2_text, settings_window):
    global KOBOLDCPP, WHISPERAUDIO, KOBOLDCPP_IP, WHISPERAUDIO_IP, editable_settings, AISCRIBE, AISCRIBE2
    KOBOLDCPP_IP = koboldcpp_ip
    WHISPERAUDIO_IP = whisperaudio_ip
    KOBOLDCPP = build_url(KOBOLDCPP_IP, "5001")
    WHISPERAUDIO = build_url(WHISPERAUDIO_IP, "8000/whisperaudio")
    save_settings_to_file(KOBOLDCPP_IP, WHISPERAUDIO_IP)  # Save to file
    for setting, entry in editable_settings_entries.items():
        value = entry.get()
        # Convert to the appropriate type (e.g., int, float, list)
        # For example, for integers:
        if setting in ["max_context_length", "max_length", "rep_pen_range", "top_k"]:
            value = int(value)
        # Add similar conditions for other data types
        editable_settings[setting] = value 
    AISCRIBE = aiscribe_text
    AISCRIBE2 = aiscribe2_text
    with open('aiscribe.txt', 'w') as f:
        f.write(AISCRIBE)
    with open('aiscribe2.txt', 'w') as f:
        f.write(AISCRIBE2)

    settings_window.destroy() 

# New dictionary for entry widgets
editable_settings_entries = {}

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
    
    row_index = 2
    for setting, value in editable_settings.items():
        tk.Label(settings_window, text=f"{setting}:").grid(row=row_index, column=0, sticky='nw')
        entry = tk.Entry(settings_window, width=50)
        entry.insert(0, str(value))
        entry.grid(row=row_index, column=1, sticky='nw')
        editable_settings_entries[setting] = entry
        row_index += 1

    # AISCRIBE text box
    tk.Label(settings_window, text="Context Before Conversation").grid(row=0, column=2, sticky='nw', padx=(10,0))
    aiscribe_textbox = tk.Text(settings_window, width=50, height=15)
    aiscribe_textbox.insert('1.0', AISCRIBE)
    aiscribe_textbox.grid(row=1, column=2, rowspan=10, sticky='nw', padx=(10,0))

    # AISCRIBE2 text box
    tk.Label(settings_window, text="Context After Conversation").grid(row=11, column=2, sticky='nw', padx=(10,0))
    aiscribe2_textbox = tk.Text(settings_window, width=50, height=15)
    aiscribe2_textbox.insert('1.0', AISCRIBE2)
    aiscribe2_textbox.grid(row=12, column=2, rowspan=10, sticky='nw', padx=(10,0))

    # Save, Close, and Default buttons under the left column
    save_button = tk.Button(settings_window, text="Save", width=15, command=lambda: save_settings(koboldcpp_ip_entry.get(), whisperaudio_ip_entry.get(), aiscribe_textbox.get("1.0", tk.END), aiscribe2_textbox.get("1.0", tk.END), settings_window))
    save_button.grid(row=row_index, column=0, padx=5, pady=5)

    close_button = tk.Button(settings_window, text="Close", width=15, command=settings_window.destroy)
    close_button.grid(row=row_index + 1, column=0, padx=5, pady=5)

    default_button = tk.Button(settings_window, text="Default", width=15, command=clear_settings_file)
    default_button.grid(row=row_index + 2, column=0, padx=5, pady=5)
    
def upload_file():
    global uploaded_file_path
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if file_path:
        uploaded_file_path = file_path
        threaded_send_audio_to_server()  # Add this line to process the file immediately

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
        
def clear_settings_file():
    try:
        open('settings.txt', 'w').close()  # This opens the files and immediately closes it, clearing its contents.
        open('aiscribe.txt', 'w').close()
        open('aiscribe2.txt', 'w').close()
        messagebox.showinfo("Settings Reset", "Settings have been reset. Please restart.")
        print("Settings file cleared.")
    except Exception as e:
        print(f"Error clearing settings files: {e}")

# GUI Setup
root = tk.Tk()
root.title("AI Medical Scribe")

user_input = scrolledtext.ScrolledText(root, height=15)
user_input.grid(row=0, column=0, columnspan=8, padx=5, pady=5)

mic_button = tk.Button(root, text="Microphone", command=toggle_recording, height=2, width=15)
mic_button.grid(row=1, column=0, pady=5)

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
