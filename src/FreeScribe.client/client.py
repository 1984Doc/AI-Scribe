# Copyright (c) 2023 Braedon Hendy
# This software is released under the GNU General Public License v3.0
# Contributors: Kevin Lai

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
import ApplicationSettings_client as settings
from ContainerManager import ContainerManager
import atexit
import asyncio
from UI.MainWindow import MainWindow


# GUI Setup
root = tk.Tk()
root.title("AI Medical Scribe")

# settings window
app_settings = settings.ApplicationSettings()
app_settings.start()


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
    thread = threading.Thread(target=handle_message, args=(formatted_message,))
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
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    current_chunk = []
    silent_duration = 0
    minimum_silent_duration = int(app_settings.editable_settings["Real Time Silence Length"])
    minimum_audio_duration = int(app_settings.editable_settings["Real Time Audio Length"])
    while is_recording:
        if not is_paused:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            current_chunk.append(data)
            # Check for silence
            audio_buffer = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768
            if is_silent(audio_buffer):
                silent_duration += CHUNK / RATE
            else:
                silent_duration = 0
            # If the current_chunk has at least 5 seconds of audio and 1 second of silence at the end
            if len(current_chunk) >= minimum_audio_duration * RATE // CHUNK:
                # Check if the last 1 second of the current_chunk is silent
                last_second_data = b''.join(current_chunk[-RATE // CHUNK:])
                last_second_buffer = np.frombuffer(last_second_data, dtype=np.int16).astype(np.float32) / 32768
                if is_silent(last_second_buffer) and silent_duration >= minimum_silent_duration:
                    if app_settings.editable_settings["Real Time"]:
                        audio_queue.put(b''.join(current_chunk))
                    current_chunk = []
                    silent_duration = 0
    stream.stop_stream()
    stream.close()
    audio_queue.put(None)


def is_silent(data, threshold=float(app_settings.editable_settings["Silence cut-off"])):
    max_value = max(data)
    #print(f"Max audio value: {max_value}")
    return max_value < threshold

def realtime_text():
    global frames, is_realtimeactive
    if not is_realtimeactive:
        is_realtimeactive = True
        model_name = app_settings.editable_settings["Whisper Model"].strip()
        model = whisper.load_model(model_name)
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
                                "X-API-Key": app_settings.editable_settings["Whisper Server API Key"]
                            }

                            if str(app_settings.SSL_ENABLE) == "1" and str(app_settings.SSL_SELFCERT) == "1":
                                response = requests.post(app_settings.WHISPERAUDIO_ENDPOINT, headers=headers,files=files, verify=False)
                            else:
                                response = requests.post(app_settings.WHISPERAUDIO_ENDPOINT, headers=headers,files=files)
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
    stop_flashing()
    response_display.configure(state='normal')
    response_display.delete("1.0", tk.END)
    response_display.configure(state='disabled')

def toggle_gpt_button():
    global is_gpt_button_active
    if is_gpt_button_active:
        gpt_button.config(bg="gray85", text="KoboldCpp")
        is_gpt_button_active = False
    else:
        gpt_button.config(bg="red", text="Custom Endpoint")
        is_gpt_button_active = True

def toggle_aiscribe():
    global use_aiscribe
    use_aiscribe = not use_aiscribe
    toggle_button.config(text="AISCRIBE ON" if use_aiscribe else "AISCRIBE OFF")

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
                response = requests.post(WHISPERAUDIO_ENDPOINT, headers=headers, files=files, verify=False)
            else:
                # Send the request with the audio file and headers/authorization
                response = requests.post(WHISPERAUDIO_ENDPOINT,headers=headers, files=files)
            
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

def handle_message(formatted_message):
    if is_gpt_button_active:
        show_edit_transcription_popup(formatted_message)
    else:
        prompt = get_prompt(formatted_message)
        if str(app_settings.SSL_ENABLE) == "1" and str(app_settings.SSL_SELFCERT) == "1":
            response = requests.post(f"{app_settings.KOBOLDCPP_ENDPOINT}/api/v1/generate", json=prompt, verify=False)
        else:
            response = requests.post(f"{app_settings.KOBOLDCPP_ENDPOINT}/api/v1/generate", json=prompt)
        if response.status_code == 200:
            results = response.json()['results']
            response_text = results[0]['text']
            response_text = response_text.replace("  ", " ").strip()
            update_gui_with_response(response_text)

def display_text(text):
    response_display.configure(state='normal')
    response_display.delete("1.0", tk.END)
    response_display.insert(tk.END, f"{text}\n")
    response_display.configure(state='disabled')

def update_gui_with_response(response_text):
    global response_history, user_message
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
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        transcript_text = response_history[index][1]
        response_text = response_history[index][2]
        user_input.configure(state='normal')
        user_input.delete("1.0", tk.END)
        user_input.insert(tk.END, transcript_text)
        response_display.configure(state='normal')
        response_display.delete('1.0', tk.END)
        response_display.insert('1.0', response_text)
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
        gpt_button.grid_remove()
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
        blinking_circle_canvas.grid(row=0, column=3, pady=5)
        combobox.grid(row=1, column=0, columnspan=3, pady=5)
        root.attributes('-topmost', True)
        root.minsize(300, 100)
        current_view = "minimal"
    else:
        mic_button.config(width=10, height=2)
        pause_button.config(width=10, height=2)
        switch_view_button.config(width=10, height=2)
        user_input.grid()
        send_button.grid()
        clear_button.grid()
        toggle_button.grid()
        gpt_button.grid()
        settings_button.grid()
        upload_button.grid()
        response_display.grid()
        timestamp_listbox.grid()
        copy_user_input_button.grid()
        copy_response_display_button.grid()
        mic_button.grid(row=1, column=1, pady=5, sticky='nsew')
        pause_button.grid(row=1, column=3, pady=5, sticky='nsew')
        switch_view_button.grid(row=1, column=9, pady=5, sticky='nsew')
        blinking_circle_canvas.grid(row=1, column=10, pady=5)
        combobox.grid(row=3, column=4, columnspan=4, pady=10, padx=10, sticky='nsew')
        root.attributes('-topmost', False)
        root.minsize(900, 400)
        current_view = "full"

def copy_text(widget):
    text = widget.get("1.0", tk.END)
    pyperclip.copy(text)

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
user_input.grid(row=0, column=1, columnspan=9, padx=5, pady=15, sticky='nsew')

mic_button = tk.Button(root, text="Mic OFF", command=lambda: (threaded_toggle_recording(), threaded_realtime_text()), height=2, width=10)
mic_button.grid(row=1, column=1, pady=5, sticky='nsew')

send_button = tk.Button(root, text="AI Request", command=send_and_flash, height=2, width=10)
send_button.grid(row=1, column=2, pady=5, sticky='nsew')

pause_button = tk.Button(root, text="Pause", command=toggle_pause, height=2, width=10)
pause_button.grid(row=1, column=3, pady=5, sticky='nsew')

clear_button = tk.Button(root, text="Clear", command=clear_all_text_fields, height=2, width=10)
clear_button.grid(row=1, column=4, pady=5, sticky='nsew')

toggle_button = tk.Button(root, text="AISCRIBE ON", command=toggle_aiscribe, height=2, width=10)
toggle_button.grid(row=1, column=5, pady=5, sticky='nsew')

gpt_button = tk.Button(root, text="KoboldCpp", command=toggle_gpt_button, height=2, width=13)
gpt_button.grid(row=1, column=6, pady=5, sticky='nsew')

settings_button = tk.Button(root, text="Settings", command=app_settings.open_settings_window, height=2, width=10)
settings_button.grid(row=1, column=7, pady=5, sticky='nsew')

upload_button = tk.Button(root, text="Upload File", command=upload_file, height=2, width=10)
upload_button.grid(row=1, column=8, pady=5, sticky='nsew')

switch_view_button = tk.Button(root, text="Switch View", command=toggle_view, height=2, width=10)
switch_view_button.grid(row=1, column=9, pady=5, sticky='nsew')

blinking_circle_canvas = tk.Canvas(root, width=20, height=20)
blinking_circle_canvas.grid(row=1, column=10, pady=5)
circle = blinking_circle_canvas.create_oval(5, 5, 15, 15, fill='white')

response_display = scrolledtext.ScrolledText(root, height=12, state='disabled')
response_display.grid(row=2, column=1, columnspan=9, padx=5, pady=15, sticky='nsew')

copy_user_input_button = tk.Button(root, text="Copy", command=lambda: copy_text(user_input), height=2, width=10)
copy_user_input_button.grid(row=0, column=10, pady=5, padx=5, sticky='ew')

copy_response_display_button = tk.Button(root, text="Copy", command=lambda: copy_text(response_display), height=2, width=10)
copy_response_display_button.grid(row=2, column=10, pady=5, padx=5, sticky='ew')

timestamp_listbox = tk.Listbox(root, height=30)
timestamp_listbox.grid(row=0, column=11, columnspan=2, rowspan=3, padx=5, pady=15, sticky='nsew')
timestamp_listbox.bind('<<ListboxSelect>>', show_response)

combobox = ttk.Combobox(root, values=dropdown_values, width=35, state="readonly")
combobox.current(0)
combobox.bind("<<ComboboxSelected>>", update_aiscribe_texts)
combobox.grid(row=3, column=4, columnspan=4, pady=10, padx=10, sticky='nsew')

window = MainWindow()

if window.container_manager.client is not None:
    # Footer frame
    footer_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN)
    footer_frame.grid(row=4, column=0, columnspan=14, sticky='nsew')

    # Docker status bar for llm and whisper containers
    docker_status = tk.Label(footer_frame, text="Docker Containers: ")
    docker_status.pack(side=tk.LEFT)

    # LLM Container Status
    llm_status = tk.Label(footer_frame, text="LLM Container Status:", padx=10)
    llm_status.pack(side=tk.LEFT)
    tt.Tooltip(llm_status, text="The LLM container is essential for generating responses and creating the SOAP notes. This service must be running.")

    # Red dot for LLM status
    llm_dot = tk.Label(footer_frame, text='●', fg='red')
    llm_dot.pack(side=tk.LEFT)
    tt.Tooltip(llm_dot, text="LLM Container Status: Green = Running, Red = Stopped")

    # Whisper Server Status
    whisper_status = tk.Label(footer_frame, text="Whisper Server Status:", padx=10)
    whisper_status.pack(side=tk.LEFT)
    tt.Tooltip(whisper_status, text="The whisper server is responsible for transcribing microphone input to text. This service must be running.")

    # Red dot for Whisper status
    whisper_dot = tk.Label(footer_frame, text='●', fg='red')
    whisper_dot.pack(side=tk.LEFT)
    tt.Tooltip(whisper_dot, text="Whisper Status: Green = Running, Red = Stopped")

    # start whisper container button
    start_whisper_button = tk.Button(footer_frame, text="Start Whisper", command=lambda: window.start_whisper_container(whisper_dot, app_settings))
    start_whisper_button.pack(side=tk.RIGHT)

    # start local llm container button
    start_llm_button = tk.Button(footer_frame, text="Start LLM", command= lambda: window.start_LLM_container(llm_dot, app_settings))
    start_llm_button.pack(side=tk.RIGHT)

    update_aiscribe_texts(None)

    #stop whisper container button
    stop_whisper_button = tk.Button(footer_frame, text="Stop Whisper", command=lambda: window.stop_whisper_container(whisper_dot, app_settings))
    stop_whisper_button.pack(side=tk.RIGHT)

    #stop llm container button
    stop_llm_button = tk.Button(footer_frame, text="Stop LLM", command=lambda: window.stop_LLM_container(llm_dot, app_settings))
    stop_llm_button.pack(side=tk.RIGHT)

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

    main_window = MainWindow()

    if main_window.container_manager is not None and app_settings.editable_settings["Auto Shutdown Containers on Exit"] is True:
        main_window.container_manager.stop_container(app_settings.editable_settings["LLM Container Name"])
        main_window.container_manager.stop_container(app_settings.editable_settings["LLM Caddy Container Name"])
        main_window.container_manager.stop_container(app_settings.editable_settings["Whisper Container Name"])
        main_window.container_manager.stop_container(app_settings.editable_settings["Whisper Caddy Container Name"])

atexit.register(on_exit)