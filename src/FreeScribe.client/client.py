"""
This software is released under the AGPL-3.0 license
Copyright (c) 2023-2024 Braedon Hendy

Further updates and packaging added in 2024 through the ClinicianFOCUS initiative, 
a collaboration with Dr. Braedon Hendy and Conestoga College Institute of Applied 
Learning and Technology as part of the CNERG+ applied research project, 
Unburdening Primary Healthcare: An Open-Source AI Clinician Partner Platform". 
Prof. Michael Yingbull (PI), Dr. Braedon Hendy (Partner), 
and Research Students - Software Developer Alex Simko, Pemba Sherpa (F24), and Naitik Patel.

"""

import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog
import Tooltip as tt
import requests
import pyperclip
import wave
import threading
import numpy as np
import base64
import json
import pyaudio
import tkinter.messagebox as messagebox
import datetime
import functools
import os
import whisper # python package is named openai-whisper
from openai import OpenAI
import scrubadub
import re
import speech_recognition as sr # python package is named speechrecognition
import time
import queue
from ContainerManager import ContainerManager
import atexit
import asyncio
from UI.MainWindow import MainWindow
from UI.MainWindowUI import MainWindowUI
from UI.SettingsWindowUI import SettingsWindowUI
from UI.SettingsWindow import SettingsWindow

# GUI Setup
root = tk.Tk()
root.title("AI Medical Scribe")

# settings logic
app_settings = SettingsWindow()
app_settings.start()

#  create our ui elements and settings config
window = MainWindowUI(root, app_settings)
settings_window = SettingsWindowUI(app_settings, window)
app_settings.set_main_window(window)

if app_settings.editable_settings["Use Docker Status Bar"]:
    window.create_docker_status_bar()

NOTE_CREATION = "Note Creation...Please Wait"

user_message = []
response_history = []
current_view = "full"
username = "user"
botname = "Assistant"
num_lines_to_keep = 20
uploaded_file_path = None
is_recording = False
is_realtimeactive = False
audio_data = []
frames = []
is_paused = False
is_flashing = False
use_aiscribe = True
is_gpt_button_active = False
p = pyaudio.PyAudio()
audio_queue = queue.Queue()
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000


def get_prompt(formatted_message):

    sampler_order = app_settings.editable_settings["sampler_order"]
    if isinstance(sampler_order, str):
        sampler_order = json.loads(sampler_order)
    return {
        "prompt": f"{formatted_message}\n",
        "use_story": app_settings.editable_settings["use_story"],
        "use_memory": app_settings.editable_settings["use_memory"],
        "use_authors_note": app_settings.editable_settings["use_authors_note"],
        "use_world_info": app_settings.editable_settings["use_world_info"],
        "max_context_length": int(app_settings.editable_settings["max_context_length"]),
        "max_length": int(app_settings.editable_settings["max_length"]),
        "rep_pen": float(app_settings.editable_settings["rep_pen"]),
        "rep_pen_range": int(app_settings.editable_settings["rep_pen_range"]),
        "rep_pen_slope": float(app_settings.editable_settings["rep_pen_slope"]),
        "temperature": float(app_settings.editable_settings["temperature"]),
        "tfs": float(app_settings.editable_settings["tfs"]),
        "top_a": float(app_settings.editable_settings["top_a"]),
        "top_k": int(app_settings.editable_settings["top_k"]),
        "top_p": float(app_settings.editable_settings["top_p"]),
        "typical": float(app_settings.editable_settings["typical"]),
        "sampler_order": sampler_order,
        "singleline": app_settings.editable_settings["singleline"],
        "frmttriminc": app_settings.editable_settings["frmttriminc"],
        "frmtrmblln": app_settings.editable_settings["frmtrmblln"]
    }

def threaded_toggle_recording():
    thread = threading.Thread(target=toggle_recording)
    thread.start()

def threaded_realtime_text():
    thread = threading.Thread(target=realtime_text)
    thread.start()

def threaded_handle_message(formatted_message):
    thread = threading.Thread(target=show_edit_transcription_popup, args=(formatted_message,))
    thread.start()

def threaded_send_audio_to_server():
    thread = threading.Thread(target=send_audio_to_server)
    thread.start()



def toggle_pause():
    global is_paused
    is_paused = not is_paused

    if is_paused:
        pause_button.config(text="Resume", bg="red")
    else:
        pause_button.config(text="Pause", bg="gray85")

def record_audio():
    global is_paused, frames, audio_queue
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=1)
    current_chunk = []
    silent_duration = 0
    minimum_silent_duration = int(app_settings.editable_settings["Real Time Silence Length"])
    minimum_audio_duration = int(app_settings.editable_settings["Real Time Audio Length"])
    while is_recording:
        if not is_paused:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            # Check for silence
            audio_buffer = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768
            if is_silent(audio_buffer, app_settings.editable_settings["Silence cut-off"]):
                silent_duration += CHUNK / RATE
            else:
                current_chunk.append(data)
                silent_duration = 0
            # If the current_chunk has at least 5 seconds of audio and 1 second of silence at the end
            if len(current_chunk) >= minimum_audio_duration * RATE // CHUNK:
                # Check if the last 1 second of the current_chunk is silent
                last_second_data = b''.join(current_chunk[-RATE // CHUNK:])
                last_second_buffer = np.frombuffer(last_second_data, dtype=np.int16).astype(np.float32) / 32768
                if app_settings.editable_settings["Real Time"]:
                    audio_queue.put(b''.join(current_chunk))
                current_chunk = []
                silent_duration = 0
    stream.stop_stream()
    stream.close()
    audio_queue.put(None)


def is_silent(data, threshold=0.01):
    """Check if audio chunk is silent"""
    data_array = np.array(data)
    max_value = max(abs(data_array))
    return max_value < threshold

def realtime_text():
    global frames, is_realtimeactive, audio_queue
    if not is_realtimeactive:
        is_realtimeactive = True
        model = None
        if app_settings.editable_settings["Real Time"]:
            try:
                model_name = app_settings.editable_settings["Whisper Model"].strip()
                model = whisper.load_model(model_name)
            except Exception as e:
                messagebox.showerror("Model Error", f"Error loading model: {e}")
                
        while True:
            audio_data = audio_queue.get()
            if audio_data is None:
                break
            if app_settings.editable_settings["Real Time"] == True:
                print("Real Time Audio to Text")
                audio_buffer = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768
                if not is_silent(audio_buffer):
                    if app_settings.editable_settings["Local Whisper"] == True:
                        print("Local Real Time Whisper")
                        result = model.transcribe(audio_buffer, fp16=False)
                        update_gui(result['text'])
                    else:
                        print("Remote Real Time Whisper")
                        if frames:
                            with wave.open('realtime.wav', 'wb') as wf:
                                wf.setnchannels(CHANNELS)
                                wf.setsampwidth(p.get_sample_size(FORMAT))
                                wf.setframerate(RATE)
                                wf.writeframes(b''.join(frames))
                            frames = []
                        file_to_send = 'realtime.wav'
                        with open(file_to_send, 'rb') as f:
                            files = {'audio': f}

                            headers = {
                                "Authorization": "Bearer "+app_settings.editable_settings["Whisper Server API Key"]
                            }

                            if str(app_settings.SSL_ENABLE) == "1" and str(app_settings.SSL_SELFCERT) == "1":
                                response = requests.post(app_settings.editable_settings["Whisper Endpoint"], headers=headers,files=files, verify=False)
                            else:
                                response = requests.post(app_settings.editable_settings["Whisper Endpoint"], headers=headers,files=files)
                            if response.status_code == 200:
                                text = response.json()['text']
                                update_gui(text)
                audio_queue.task_done()
    else:
        is_realtimeactive = False

def update_gui(text):
    user_input.insert(tk.END, text + '\n')
    user_input.see(tk.END)

def save_audio():
    global frames
    if frames:
        with wave.open('recording.wav', 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        frames = []  # Clear recorded data
        if app_settings.editable_settings["Real Time"] == True:
            send_and_receive()
        else:
            threaded_send_audio_to_server()

def toggle_recording():
    global is_recording, recording_thread
    if not is_recording:
        user_input.configure(state='normal')
        user_input.delete("1.0", tk.END)
        if not app_settings.editable_settings["Real Time"]:
            user_input.insert(tk.END, "Recording")
        response_display.configure(state='normal')
        response_display.delete("1.0", tk.END)
        response_display.configure(fg='black')
        response_display.configure(state='disabled')
        is_recording = True
        recording_thread = threading.Thread(target=record_audio)
        recording_thread.start()
        mic_button.config(bg="red", text="Mic ON")
        start_flashing()
    else:
        is_recording = False
        if recording_thread.is_alive():
            recording_thread.join()  # Ensure the recording thread is terminated
        save_audio()
        mic_button.config(bg="gray85", text="Mic OFF")

def clear_all_text_fields():
    user_input.configure(state='normal')
    user_input.delete("1.0", tk.END)
    user_input.focus_set()
    root.focus_set()
    stop_flashing()
    response_display.configure(state='normal')
    response_display.delete("1.0", tk.END)
    response_display.insert(tk.END, "Medical Note")
    response_display.config(fg='grey')
    response_display.configure(state='disabled')

def toggle_aiscribe():
    global use_aiscribe
    use_aiscribe = not use_aiscribe
    toggle_button.config(text="AI Scribe\nON" if use_aiscribe else "AI Scribe\nOFF")

def send_audio_to_server():
    """
    Sends an audio file to either a local or remote Whisper server for transcription.

    Global Variables:
    ----------------
    uploaded_file_path : str
        The path to the uploaded audio file. If `None`, the function defaults to
        'recording.wav'.

    Parameters:
    -----------
    None

    Returns:
    --------
    None

    Raises:
    -------
    ValueError
        If the `app_settings.editable_settings["Local Whisper"]` flag is not a boolean.
    FileNotFoundError
        If the specified audio file does not exist.
    requests.exceptions.RequestException
        If there is an issue with the HTTP request to the remote server.
    """

    global uploaded_file_path

    # Check if Local Whisper is enabled in the editable settings
    if app_settings.editable_settings["Local Whisper"] == True:
        # Inform the user that Local Whisper is being used for transcription
        print("Using Local Whisper for transcription.")

        # Configure the user input widget to be editable and clear its content
        user_input.configure(state='normal')
        user_input.delete("1.0", tk.END)

        # Display a message indicating that audio to text processing is in progress
        user_input.insert(tk.END, "Audio to Text Processing...Please Wait")

        # Load the specified Whisper model
        model_name = app_settings.editable_settings["Whisper Model"].strip()
        model = whisper.load_model(model_name)

        # Determine the file to send for transcription
        file_to_send = uploaded_file_path if uploaded_file_path else 'recording.wav'
        uploaded_file_path = None

        # Transcribe the audio file using the loaded model
        result = model.transcribe(file_to_send)
        transcribed_text = result["text"]

        # Update the user input widget with the transcribed text
        user_input.configure(state='normal')
        user_input.delete("1.0", tk.END)
        user_input.insert(tk.END, transcribed_text)

        # Send the transcribed text and receive a response
        send_and_receive()
    else:
        # Inform the user that Remote Whisper is being used for transcription
        print("Using Remote Whisper for transcription.")

        # Configure the user input widget to be editable and clear its content
        user_input.configure(state='normal')
        user_input.delete("1.0", tk.END)

        # Display a message indicating that audio to text processing is in progress
        user_input.insert(tk.END, "Audio to Text Processing...Please Wait")

        # Determine the file to send for transcription
        if uploaded_file_path:
            file_to_send = uploaded_file_path
            uploaded_file_path = None
        else:
            file_to_send = 'recording.wav'

        # Open the audio file in binary mode
        with open(file_to_send, 'rb') as f:
            files = {'audio': f}

            # Add the Bearer token to the headers for authentication
            headers = {
                "Authorization": f"Bearer {app_settings.editable_settings['Whisper Server API Key']}"
            }

            # Check for SSL and self-signed certificate settings
            if str(app_settings.SSL_ENABLE) == "1" and str(app_settings.SSL_SELFCERT) == "1":
                # Send the request without verifying the SSL certificate
                response = requests.post(app_settings.editable_settings["Whisper Endpoint"], headers=headers, files=files, verify=False)
            else:
                # Send the request with the audio file and headers/authorization
                response = requests.post(app_settings.editable_settings["Whisper Endpoint"], headers=headers, files=files)
            
            # On successful response (status code 200)
            if response.status_code == 200:
                # Update the UI with the transcribed text
                transcribed_text = response.json()['text']
                user_input.configure(state='normal')
                user_input.delete("1.0", tk.END)
                user_input.insert(tk.END, transcribed_text)

                # Send the transcribed text and receive a response
                send_and_receive()

def send_and_receive():
    global use_aiscribe, user_message
    user_message = user_input.get("1.0", tk.END).strip()
    display_text(NOTE_CREATION)
    if use_aiscribe:
        formatted_message = f'{AISCRIBE} [{user_message}] {AISCRIBE2}'
    else:
        formatted_message = user_message
    threaded_handle_message(formatted_message)

        

def display_text(text):
    response_display.configure(state='normal')
    response_display.delete("1.0", tk.END)
    response_display.insert(tk.END, f"{text}\n")
    response_display.configure(fg='black')
    response_display.configure(state='disabled')

IS_FIRST_LOG = True
def update_gui_with_response(response_text):
    global response_history, user_message, IS_FIRST_LOG

    if IS_FIRST_LOG:
        timestamp_listbox.delete(0, tk.END)
        timestamp_listbox.config(fg='black')
        IS_FIRST_LOG = False

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response_history.insert(0, (timestamp, user_message, response_text))

    # Update the timestamp listbox
    timestamp_listbox.delete(0, tk.END)
    for time, _, _ in response_history:
        timestamp_listbox.insert(tk.END, time)

    display_text(response_text)
    pyperclip.copy(response_text)
    stop_flashing()

def show_response(event):
    global IS_FIRST_LOG

    if IS_FIRST_LOG:
        return

    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        transcript_text = response_history[index][1]
        response_text = response_history[index][2]
        user_input.configure(state='normal')
        user_input.config(fg='black')
        user_input.delete("1.0", tk.END)
        user_input.insert(tk.END, transcript_text)
        response_display.configure(state='normal')
        response_display.delete('1.0', tk.END)
        response_display.insert('1.0', response_text)
        response_display.config(fg='black')
        response_display.configure(state='disabled')
        pyperclip.copy(response_text)

def send_text_to_chatgpt(edited_text):
    api_key = app_settings.OPENAI_API_KEY
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    payload = {
        "model": app_settings.editable_settings["Model"].strip(),
        "messages": [
            {"role": "user", "content": edited_text}
        ],
    }
    try:

        if app_settings.editable_settings["Model Endpoint"].endswith('/'):
            app_settings.editable_settings["Model Endpoint"] = app_settings.editable_settings["Model Endpoint"][:-1]

        if app_settings.API_STYLE == "OpenAI":
            response = requests.Response
            if str(app_settings.SSL_SELFCERT) == "1" and str(app_settings.SSL_ENABLE) == "1":
                response = requests.post(app_settings.editable_settings["Model Endpoint"]+"/chat/completions", headers=headers, json=payload, verify=False)
            else:
                response = requests.post(app_settings.editable_settings["Model Endpoint"]+"/chat/completions", headers=headers, json=payload)

            response.raise_for_status()
            response_data = response.json()
            response_text = (response_data['choices'][0]['message']['content'])
            update_gui_with_response(response_text)
        elif app_settings.API_STYLE == "KoboldCpp":
            prompt = get_prompt(edited_text)
            if str(app_settings.SSL_ENABLE) == "1" and str(app_settings.SSL_SELFCERT) == "1":
                response = requests.post(app_settings.editable_settings["Model Endpoint"] + "/api/v1/generate", json=prompt, verify=False)
            else:
                response = requests.post(app_settings.editable_settings["Model Endpoint"] + "/api/v1/generate", json=prompt)
            if response.status_code == 200:
                results = response.json()['results']
                response_text = results[0]['text']
                response_text = response_text.replace("  ", " ").strip()
                update_gui_with_response(response_text)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        display_text(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        display_text(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        display_text(f"Connection error occurred: {conn_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
        display_text(f"Connection error occurred: {conn_err}")


def show_edit_transcription_popup(formatted_message):
    popup = tk.Toplevel(root)
    popup.title("Scrub PHI Prior to GPT")
    text_area = scrolledtext.ScrolledText(popup, height=20, width=80)
    text_area.pack(padx=10, pady=10)

    scrubber = scrubadub.Scrubber()

    scrubbed_message = scrubadub.clean(formatted_message)

    pattern = r'\b\d{10}\b'     # Any 10 digit number, looks like OHIP
    cleaned_message = re.sub(pattern,'{{OHIP}}',scrubbed_message)
    text_area.insert(tk.END, cleaned_message)

    def on_proceed():
        edited_text = text_area.get("1.0", tk.END).strip()
        popup.destroy()
        send_text_to_chatgpt(edited_text)

    proceed_button = tk.Button(popup, text="Proceed", command=on_proceed)
    proceed_button.pack(side=tk.RIGHT, padx=10, pady=10)

    # Cancel button
    cancel_button = tk.Button(popup, text="Cancel", command=popup.destroy)
    cancel_button.pack(side=tk.LEFT, padx=10, pady=10)


def upload_file():
    global uploaded_file_path
    file_path = filedialog.askopenfilename(filetypes=(("Audio files", "*.wav *.mp3"),))
    if file_path:
        uploaded_file_path = file_path
        threaded_send_audio_to_server()  # Add this line to process the file immediately
    start_flashing()



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

def send_and_flash():
    start_flashing()
    send_and_receive()

def clear_settings_file(settings_window):
    try:
        open('settings.txt', 'w').close()  # This opens the files and immediately closes it, clearing its contents.
        open('aiscribe.txt', 'w').close()
        open('aiscribe2.txt', 'w').close()
        messagebox.showinfo("Settings Reset", "Settings have been reset. Please restart.")
        print("Settings file cleared.")
        settings_window.destroy()
    except Exception as e:
        print(f"Error clearing settings files: {e}")

def toggle_view():
    global current_view
    if current_view == "full":
        user_input.grid_remove()
        send_button.grid_remove()
        clear_button.grid_remove()
        toggle_button.grid_remove()
        settings_button.grid_remove()
        upload_button.grid_remove()
        response_display.grid_remove()
        timestamp_listbox.grid_remove()
        copy_user_input_button.grid_remove()
        copy_response_display_button.grid_remove()
        mic_button.config(width=10, height=1)
        pause_button.config(width=10, height=1)
        switch_view_button.config(width=10, height=1)
        mic_button.grid(row=0, column=0, pady=5)
        pause_button.grid(row=0, column=1, pady=5)
        switch_view_button.grid(row=0, column=2, pady=5)
        switch_view_button.config(text="Maximize View")
        blinking_circle_canvas.grid(row=0, column=3, pady=5)
        combobox.grid(row=1, column=0, columnspan=3, pady=5)
        root.attributes('-topmost', True)
        root.minsize(300, 100)
        current_view = "minimal"
        window.destroy_docker_status_bar()

    else:
        mic_button.config(width=11, height=2)
        pause_button.config(width=11, height=2)
        switch_view_button.config(width=11, height=2)
        switch_view_button.config(text="Minimize View")
        user_input.grid()
        send_button.grid()
        clear_button.grid()
        toggle_button.grid()
        settings_button.grid()
        upload_button.grid()
        response_display.grid()
        timestamp_listbox.grid()
        copy_user_input_button.grid()
        copy_response_display_button.grid()
        mic_button.grid(row=1, column=1, pady=5, sticky='nsew')
        pause_button.grid(row=1, column=3, pady=5, sticky='nsew')
        switch_view_button.grid(row=1, column=8, pady=5, sticky='nsew')
        blinking_circle_canvas.grid(row=1, column=9, pady=5)
        combobox.grid(row=3, column=4, columnspan=4, pady=10, padx=10, sticky='nsew')
        root.attributes('-topmost', False)
        root.minsize(900, 400)
        current_view = "full"
        window.create_docker_status_bar()

def copy_text(widget):
    text = widget.get("1.0", tk.END)
    pyperclip.copy(text)

def add_placeholder(event, text_widget, placeholder_text="Text box"):
    if text_widget.get("1.0", "end-1c") == "":
        text_widget.insert("1.0", placeholder_text)
        text_widget.config(fg='grey')

def remove_placeholder(event, text_widget, placeholder_text="Text box"):
    if text_widget.get("1.0", "end-1c") == placeholder_text:
        text_widget.delete("1.0", "end")
        text_widget.config(fg='black')

def get_dropdown_values_and_mapping():
    options = []
    mapping = {}
    try:
        with open('options.txt', 'r') as file:
            content = file.read().strip()
        templates = content.split('\n\n')
        for template in templates:
            lines = template.split('\n')
            if len(lines) == 3:
                title, aiscribe, aiscribe2 = lines
                options.append(title)
                mapping[title] = (aiscribe, aiscribe2)
    except FileNotFoundError:
        print("options.txt not found, using default values.")
        # Fallback default options if file not found
        options = ["Settings Template"]
        mapping["Settings Template"] = (app_settings.AISCRIBE, app_settings.AISCRIBE2)
    return options, mapping

dropdown_values, option_mapping = get_dropdown_values_and_mapping()

def update_aiscribe_texts(event):
    global AISCRIBE, AISCRIBE2
    selected_option = combobox.get()
    if selected_option in option_mapping:
        AISCRIBE, AISCRIBE2 = option_mapping[selected_option]

# Configure grid weights for scalability
root.grid_columnconfigure(0, weight=1, minsize= 10)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, weight=1)
root.grid_columnconfigure(5, weight=1)
root.grid_columnconfigure(6, weight=1)
root.grid_columnconfigure(7, weight=1)
root.grid_columnconfigure(8, weight=1)
root.grid_columnconfigure(9, weight=1)
root.grid_columnconfigure(10, weight=1)
root.grid_columnconfigure(11, weight=1)
root.grid_columnconfigure(12, weight=1)
root.grid_columnconfigure(13, weight=1, minsize=10)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=0)
root.grid_rowconfigure(4, weight=0)


user_input = scrolledtext.ScrolledText(root, height=12)
user_input.grid(row=0, column=1, columnspan=8, padx=5, pady=15, sticky='nsew')


# Insert placeholder text
user_input.insert("1.0", "Transcript of Conversation")
user_input.config(fg='grey')

# Bind events to remove or add the placeholder with arguments
user_input.bind("<FocusIn>", lambda event: remove_placeholder(event, user_input, "Transcript of Conversation"))
user_input.bind("<FocusOut>", lambda event: add_placeholder(event, user_input, "Transcript of Conversation"))

mic_button = tk.Button(root, text="Mic OFF", command=lambda: (threaded_toggle_recording(), threaded_realtime_text()), height=2, width=11)
mic_button.grid(row=1, column=1, pady=5, sticky='nsew')

send_button = tk.Button(root, text="AI Request", command=send_and_flash, height=2, width=11)
send_button.grid(row=1, column=2, pady=5, sticky='nsew')

pause_button = tk.Button(root, text="Pause", command=toggle_pause, height=2, width=11)
pause_button.grid(row=1, column=3, pady=5, sticky='nsew')

clear_button = tk.Button(root, text="Clear", command=clear_all_text_fields, height=2, width=11)
clear_button.grid(row=1, column=4, pady=5, sticky='nsew')

toggle_button = tk.Button(root, text="AI Scribe\nON", command=toggle_aiscribe, height=2, width=11)
toggle_button.grid(row=1, column=5, pady=5, sticky='nsew')

settings_button = tk.Button(root, text="Settings", command= settings_window.open_settings_window, height=2, width=11)
settings_button.grid(row=1, column=6, pady=5, sticky='nsew')

upload_button = tk.Button(root, text="Upload\nRecording", command=upload_file, height=2, width=11)
upload_button.grid(row=1, column=7, pady=5, sticky='nsew')

switch_view_button = tk.Button(root, text="Minimize View", command=toggle_view, height=2, width=11)
switch_view_button.grid(row=1, column=8, pady=5, sticky='nsew')

blinking_circle_canvas = tk.Canvas(root, width=20, height=20)
blinking_circle_canvas.grid(row=1, column=9, pady=5)
circle = blinking_circle_canvas.create_oval(5, 5, 15, 15, fill='white')

response_display = scrolledtext.ScrolledText(root, height=12, state='disabled')
response_display.grid(row=2, column=1, columnspan=8, padx=5, pady=15, sticky='nsew')

# Insert placeholder text
response_display.configure(state='normal')
response_display.insert("1.0", "Medical Note")
response_display.config(fg='grey')
response_display.configure(state='disabled')

copy_user_input_button = tk.Button(root, text="Copy", command=lambda: copy_text(user_input), height=2, width=10)
copy_user_input_button.grid(row=0, column=9, pady=5, padx=5, sticky='ew')

copy_response_display_button = tk.Button(root, text="Copy", command=lambda: copy_text(response_display), height=2, width=10)
copy_response_display_button.grid(row=2, column=9, pady=5, padx=5, sticky='ew')

timestamp_listbox = tk.Listbox(root, height=30)
timestamp_listbox.grid(row=0, column=10, columnspan=2, rowspan=3, padx=5, pady=15, sticky='nsew')
timestamp_listbox.bind('<<ListboxSelect>>', show_response)
timestamp_listbox.insert(tk.END, "Medical Note History")
timestamp_listbox.config(fg='grey')

combobox = ttk.Combobox(root, values=dropdown_values, width=35, state="readonly")
combobox.current(0)
combobox.bind("<<ComboboxSelected>>", update_aiscribe_texts)
combobox.grid(row=3, column=4, columnspan=4, pady=10, padx=10, sticky='nsew')

update_aiscribe_texts(None)


# Bind Alt+P to send_and_receive function
root.bind('<Alt-p>', lambda event: pause_button.invoke())

# Bind Alt+R to toggle_recording function
root.bind('<Alt-r>', lambda event: mic_button.invoke())

#set min size
root.minsize(900, 400)

root.mainloop()

p.terminate()

def on_exit():
    # Create a pop up that says yes or no with tkinter messagebox to option to close the docker containers

    global window

    main_window = window.logic

    if main_window.container_manager is not None and app_settings.editable_settings["Auto Shutdown Containers on Exit"] is True:
        main_window.container_manager.stop_container(app_settings.editable_settings["LLM Container Name"])
        main_window.container_manager.stop_container(app_settings.editable_settings["LLM Caddy Container Name"])
        main_window.container_manager.stop_container(app_settings.editable_settings["Whisper Container Name"])
        main_window.container_manager.stop_container(app_settings.editable_settings["Whisper Caddy Container Name"])

atexit.register(on_exit)