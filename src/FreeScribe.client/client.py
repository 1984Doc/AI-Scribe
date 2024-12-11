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

import os
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
import tkinter.messagebox as messagebox
import datetime
import whisper # python package is named openai-whisper
import scrubadub
import re
import speech_recognition as sr # python package is named speechrecognition
import time
import queue
import atexit
from UI.MainWindowUI import MainWindowUI
from UI.SettingsWindow import SettingsWindow, SettingsKeys
from UI.Widgets.CustomTextBox import CustomTextBox
from UI.LoadingWindow import LoadingWindow
from UI.Widgets.MicrophoneSelector import MicrophoneState
from Model import  ModelManager
from utils.ip_utils import is_private_ip
from utils.file_utils import get_file_path, get_resource_path
import ctypes
import sys
from UI.DebugWindow import DualOutput
import traceback
import sys
from utils.utils import window_has_running_instance, bring_to_front, close_mutex

dual = DualOutput()
sys.stdout = dual
sys.stderr = dual

APP_NAME = 'AI Medical Scribe'  # Application name

# check if another instance of the application is already running.
# if false, create a new instance of the application
# if true, exit the current instance
if not window_has_running_instance():
    root = tk.Tk()
    root.title(APP_NAME)
else:
    bring_to_front(APP_NAME)
    sys.exit(0)

# Register the close_mutex function to be called on exit
atexit.register(close_mutex)

# settings logic
app_settings = SettingsWindow()

#  create our ui elements and settings config
window = MainWindowUI(root, app_settings)

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

# Application flags
is_audio_processing_realtime_canceled = threading.Event()
is_audio_processing_whole_canceled = threading.Event()

# Constants
DEFAULT_BUTTON_COLOUR = "SystemButtonFace"

#Thread tracking variables
REALTIME_TRANSCRIBE_THREAD_ID = None
GENERATION_THREAD_ID = None

# Global instance of whisper model
stt_local_model = None


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
    return thread

def threaded_handle_message(formatted_message):
    thread = threading.Thread(target=show_edit_transcription_popup, args=(formatted_message,))
    thread.start()
    return thread

def threaded_send_audio_to_server():
    thread = threading.Thread(target=send_audio_to_server)
    thread.start()
    return thread


def toggle_pause():
    global is_paused
    is_paused = not is_paused

    if is_paused:
        if current_view == "full":
            pause_button.config(text="Resume", bg="red")
        elif current_view == "minimal":
            pause_button.config(text="▶️", bg="red")
    else:
        if current_view == "full":
            pause_button.config(text="Pause", bg=DEFAULT_BUTTON_COLOUR)
        elif current_view == "minimal":
            pause_button.config(text="⏸️", bg=DEFAULT_BUTTON_COLOUR)
    
SILENCE_WARNING_LENGTH = 10 # seconds, warn the user after 10s of no input something might be wrong

def record_audio():
    global is_paused, frames, audio_queue

    try:
        stream = p.open(
            format=FORMAT, 
            channels=1, 
            rate=RATE, 
            input=True,
            frames_per_buffer=CHUNK, 
            input_device_index=int(MicrophoneState.SELECTED_MICROPHONE_INDEX))
    except (OSError, IOError) as e:
        messagebox.showerror("Audio Error", f"Please check your microphone settings under whisper settings. Error opening audio stream: {e}")
        return

    
    current_chunk = []
    silent_duration = 0
    silent_warning_duration = 0
    record_duration = 0
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
                silent_warning_duration += CHUNK / RATE
            else:
                current_chunk.append(data)
                silent_duration = 0
                silent_warning_duration = 0
            
            record_duration += CHUNK / RATE

            # Check if we need to warn if silence is long than warn time
            check_silence_warning(silent_warning_duration)

            # If the current_chunk has at least 5 seconds of audio and 1 second of silence at the end
            if record_duration >= minimum_audio_duration and silent_duration >= minimum_silent_duration:
                if app_settings.editable_settings["Real Time"] and current_chunk:
                    audio_queue.put(b''.join(current_chunk))
                current_chunk = []
                silent_duration = 0
                record_duration = 0

    # Send any remaining audio chunk when recording stops
    if current_chunk:
        audio_queue.put(b''.join(current_chunk))

    stream.stop_stream()
    stream.close()
    audio_queue.put(None)

    # If the warning bar is displayed, remove it
    if window.warning_bar is not None:
        window.destroy_warning_bar()

def check_silence_warning(silence_duration):
    """Check if silence warning should be displayed."""

    # Check if we need to warn if silence is long than warn time
    if silence_duration >= SILENCE_WARNING_LENGTH:
        
        # If the warning bar is not already displayed, create it
        if window.warning_bar is None:
            window.create_warning_bar("No audio input detected for 10 seconds. Please check your microphone input device in whisper settings and adjust your microphone cutoff level in advanced settings.")
    else:
        # If the warning bar is displayed, remove it
        if window.warning_bar is not None:
            window.destroy_warning_bar()

def is_silent(data, threshold=0.01):
    """Check if audio chunk is silent"""
    data_array = np.array(data)
    max_value = max(abs(data_array))
    return max_value < threshold

def realtime_text():
    global frames, is_realtimeactive, audio_queue
    # Incase the user starts a new recording while this one the older thread is finishing.
    # This is a local flag to prevent the processing of the current audio chunk 
    # if the global flag is reset on new recording
    local_cancel_flag = False 
    if not is_realtimeactive:
        is_realtimeactive = True

        while True:
            #  break if canceled
            if is_audio_processing_realtime_canceled.is_set():
                local_cancel_flag = True
                break

            audio_data = audio_queue.get()
            if audio_data is None:
                break
            if app_settings.editable_settings["Real Time"] == True:
                print("Real Time Audio to Text")
                audio_buffer = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768
                if not is_silent(audio_buffer):
                    if app_settings.editable_settings[SettingsKeys.LOCAL_WHISPER.value] == True:
                        print("Local Real Time Whisper")
                        if stt_local_model is None:
                            update_gui("Local Whisper model not loaded. Please check your settings.")
                            break

                        result = stt_local_model.transcribe(audio_buffer, fp16=False)
                        if not local_cancel_flag and not is_audio_processing_realtime_canceled.is_set():
                            update_gui(result['text'])
                    else:
                        print("Remote Real Time Whisper")
                        if frames:
                            with wave.open(get_resource_path("realtime.wav"), 'wb') as wf:
                                wf.setnchannels(CHANNELS)
                                wf.setsampwidth(p.get_sample_size(FORMAT))
                                wf.setframerate(RATE)
                                wf.writeframes(b''.join(frames))
                            frames = []
                        file_to_send = get_resource_path("realtime.wav")
                        with open(file_to_send, 'rb') as f:
                            files = {'audio': f}

                            headers = {
                                "Authorization": "Bearer "+app_settings.editable_settings[SettingsKeys.WHISPER_SERVER_API_KEY.value]
                            }

                            try:
                                verify = not app_settings.editable_settings["S2T Server Self-Signed Certificates"]
                                response = requests.post(app_settings.editable_settings[SettingsKeys.WHISPER_ENDPOINT.value], headers=headers,files=files, verify=verify)
                                if response.status_code == 200:
                                    text = response.json()['text']
                                    if not local_cancel_flag and not is_audio_processing_realtime_canceled.is_set():
                                        update_gui(text)
                                else:
                                    update_gui(f"Error (HTTP Status {response.status_code}): {response.text}")
                            except Exception as e:
                                update_gui(f"Error: {e}")
                            finally:
                                #Task done clean up file
                                if os.path.exists(file_to_send):
                                    f.close()
                                    os.remove(file_to_send)
                audio_queue.task_done()
    else:
        is_realtimeactive = False

def update_gui(text):
    user_input.scrolled_text.insert(tk.END, text + '\n')
    user_input.scrolled_text.see(tk.END)

def save_audio():
    global frames
    if frames:
        with wave.open(get_resource_path("recording.wav"), 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        frames = []  # Clear recorded data

        if app_settings.editable_settings["Real Time"] == True and is_audio_processing_realtime_canceled.is_set() is False:
            send_and_receive()
        elif app_settings.editable_settings["Real Time"] == False and is_audio_processing_whole_canceled.is_set() is False:
            threaded_send_audio_to_server()

def toggle_recording():
    global is_recording, recording_thread, DEFAULT_BUTTON_COLOUR, audio_queue, current_view, REALTIME_TRANSCRIBE_THREAD_ID

    # Reset the cancel flags going into a fresh recording
    if not is_recording:
        is_audio_processing_realtime_canceled.clear()
        is_audio_processing_whole_canceled.clear()

    if is_paused:
        toggle_pause()

    realtime_thread = threaded_realtime_text()

    if not is_recording:
        disable_recording_ui_elements()
        REALTIME_TRANSCRIBE_THREAD_ID = realtime_thread.ident
        user_input.scrolled_text.configure(state='normal')
        user_input.scrolled_text.delete("1.0", tk.END)
        if not app_settings.editable_settings["Real Time"]:
            user_input.scrolled_text.insert(tk.END, "Recording")
        response_display.scrolled_text.configure(state='normal')
        response_display.scrolled_text.delete("1.0", tk.END)
        response_display.scrolled_text.configure(fg='black')
        response_display.scrolled_text.configure(state='disabled')
        is_recording = True

        recording_thread = threading.Thread(target=record_audio)
        recording_thread.start()


        if current_view == "full":
            mic_button.config(bg="red", text="Stop\nRecording")
        elif current_view == "minimal":
            mic_button.config(bg="red", text="⏹️")
        
        start_flashing()
    else:
        enable_recording_ui_elements()
        is_recording = False
        if recording_thread.is_alive():
            recording_thread.join()  # Ensure the recording thread is terminated
        
        if app_settings.editable_settings["Real Time"] and not is_audio_processing_realtime_canceled.is_set():
            def cancel_realtime_processing(thread_id):
                """Cancels any ongoing audio processing.
                
                Sets the global flag to stop audio processing operations.
                """
                global REALTIME_TRANSCRIBE_THREAD_ID

                try:
                    kill_thread(thread_id)
                except Exception as e:
                    # Log the error message
                    # TODO System logger
                    print(f"An error occurred: {e}")
                finally:
                    REALTIME_TRANSCRIBE_THREAD_ID = None

                #empty the queue
                while not audio_queue.empty():
                    audio_queue.get()
                    audio_queue.task_done()

            loading_window = LoadingWindow(root, "Processing Audio", "Processing Audio. Please wait.", on_cancel=lambda: (cancel_processing(), cancel_realtime_processing(REALTIME_TRANSCRIBE_THREAD_ID)))


            timeout_timer = 0
            while audio_queue.empty() is False and timeout_timer < 180:
                # break because cancel was requested
                if is_audio_processing_realtime_canceled.is_set():
                    break
                
                timeout_timer += 0.1
                time.sleep(0.1)
            
            loading_window.destroy()

            realtime_thread.join()

        save_audio()

        if current_view == "full":
            mic_button.config(bg=DEFAULT_BUTTON_COLOUR, text="Start\nRecording")
        elif current_view == "minimal":
            mic_button.config(bg=DEFAULT_BUTTON_COLOUR, text="🎤")

def disable_recording_ui_elements():
    window.disable_settings_menu()
    user_input.scrolled_text.configure(state='disabled')
    send_button.config(state='disabled')
    toggle_button.config(state='disabled')
    upload_button.config(state='disabled')
    response_display.scrolled_text.configure(state='disabled')
    timestamp_listbox.config(state='disabled')
    clear_button.config(state='disabled')

def enable_recording_ui_elements():
    window.enable_settings_menu()
    user_input.scrolled_text.configure(state='normal')
    send_button.config(state='normal')
    toggle_button.config(state='normal')
    upload_button.config(state='normal')
    timestamp_listbox.config(state='normal')
    clear_button.config(state='normal')
    

def cancel_processing():
    """Cancels any ongoing audio processing.
    
    Sets the global flag to stop audio processing operations.
    """
    print("Processing canceled.")

    if app_settings.editable_settings["Real Time"]:
        is_audio_processing_realtime_canceled.set() # Flag to terminate processing
    else:
        is_audio_processing_whole_canceled.set()  # Flag to terminate processing

def clear_application_press():
    """Resets the application state by clearing text fields and recording status."""
    reset_recording_status()  # Reset recording-related variables
    clear_all_text_fields()  # Clear UI text areas

def reset_recording_status():
    """Resets all recording-related variables and stops any active recording.
    
    Handles cleanup of recording state by:
        - Checking if recording is active
        - Canceling any processing
        - Stopping the recording thread
    """
    global is_recording, frames, audio_queue, REALTIME_TRANSCRIBE_THREAD_ID, GENERATION_THREAD_ID
    if is_recording:  # Only reset if currently recording
        cancel_processing()  # Stop any ongoing processing
        threaded_toggle_recording()  # Stop the recording thread

    # kill the generation thread if active
    if REALTIME_TRANSCRIBE_THREAD_ID:
        # Exit the current realtime thread
        try:
            kill_thread(REALTIME_TRANSCRIBE_THREAD_ID)
        except Exception as e:
            # Log the error message
            # TODO System logger
            print(f"An error occurred: {e}")
        finally:
            REALTIME_TRANSCRIBE_THREAD_ID = None

    if GENERATION_THREAD_ID:
        try:
            kill_thread(GENERATION_THREAD_ID)
        except Exception as e:
            # Log the error message
            # TODO System logger
            print(f"An error occurred: {e}")
        finally:
            GENERATION_THREAD_ID = None

def clear_all_text_fields():
    """Clears and resets all text fields in the application UI.
    
    Performs the following:
        - Clears user input field
        - Resets focus
        - Stops any flashing effects
        - Resets response display with default text
    """
    # Enable and clear user input field
    user_input.scrolled_text.configure(state='normal')
    user_input.scrolled_text.delete("1.0", tk.END)
    
    # Reset focus to main window
    user_input.scrolled_text.focus_set()
    root.focus_set()
    
    stop_flashing()  # Stop any UI flashing effects
    
    # Reset response display with default text
    response_display.scrolled_text.configure(state='normal')
    response_display.scrolled_text.delete("1.0", tk.END)
    response_display.scrolled_text.insert(tk.END, "Medical Note")
    response_display.scrolled_text.config(fg='grey')
    response_display.scrolled_text.configure(state='disabled')

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
        If the `app_settings.editable_settings[SettingsKeys.LOCAL_WHISPER.value]` flag is not a boolean.
    FileNotFoundError
        If the specified audio file does not exist.
    requests.exceptions.RequestException
        If there is an issue with the HTTP request to the remote server.
    """

    global uploaded_file_path
    current_thread_id = threading.current_thread().ident

    def cancel_whole_audio_process(thread_id):
        global GENERATION_THREAD_ID
        
        is_audio_processing_whole_canceled.clear()

        try:
            kill_thread(thread_id)
        except Exception as e:
            # Log the error message
            #TODO Logging the message to system logger
            print(f"An error occurred: {e}")
        finally:
            GENERATION_THREAD_ID = None

    loading_window = LoadingWindow(root, "Processing Audio", "Processing Audio. Please wait.", on_cancel=lambda: (cancel_processing(), cancel_whole_audio_process(current_thread_id)))

    # Check if SettingsKeys.LOCAL_WHISPER is enabled in the editable settings
    if app_settings.editable_settings[SettingsKeys.LOCAL_WHISPER.value] == True:
        # Inform the user that SettingsKeys.LOCAL_WHISPER.value is being used for transcription
        print(f"Using {SettingsKeys.LOCAL_WHISPER.value} for transcription.")
        # Configure the user input widget to be editable and clear its content
        user_input.scrolled_text.configure(state='normal')
        user_input.scrolled_text.delete("1.0", tk.END)

        # Display a message indicating that audio to text processing is in progress
        user_input.scrolled_text.insert(tk.END, "Audio to Text Processing...Please Wait")
        try:
            # Determine the file to send for transcription
            file_to_send = uploaded_file_path or get_resource_path('recording.wav')
            delete_file = False if uploaded_file_path else True
            uploaded_file_path = None

            # Transcribe the audio file using the loaded model
            result = stt_local_model.transcribe(file_to_send)
            transcribed_text = result["text"]

            # done with file clean up
            if os.path.exists(file_to_send) and delete_file is True:
                os.remove(file_to_send)

            #check if canceled, if so do not update the UI
            if not is_audio_processing_whole_canceled.is_set():
                # Update the user input widget with the transcribed text
                user_input.scrolled_text.configure(state='normal')
                user_input.scrolled_text.delete("1.0", tk.END)
                user_input.scrolled_text.insert(tk.END, transcribed_text)

                # Send the transcribed text and receive a response
                send_and_receive()
        except Exception as e:
            # Log the error message
            # TODO: Add system eventlogger
            print(f"An error occurred: {e}")

            #log error to input window
            user_input.scrolled_text.configure(state='normal')
            user_input.scrolled_text.delete("1.0", tk.END)
            user_input.scrolled_text.insert(tk.END, f"An error occurred: {e}")
            user_input.scrolled_text.configure(state='disabled')
        finally:
            loading_window.destroy()
            
    else:
        # Inform the user that Remote Whisper is being used for transcription
        print("Using Remote Whisper for transcription.")

        # Configure the user input widget to be editable and clear its content
        user_input.scrolled_text.configure(state='normal')
        user_input.scrolled_text.delete("1.0", tk.END)

        # Display a message indicating that audio to text processing is in progress
        user_input.scrolled_text.insert(tk.END, "Audio to Text Processing...Please Wait")

        delete_file = False if uploaded_file_path else True

        # Determine the file to send for transcription
        if uploaded_file_path:
            file_to_send = uploaded_file_path
            uploaded_file_path = None
        else:
            file_to_send = get_resource_path('recording.wav')

        # Open the audio file in binary mode
        with open(file_to_send, 'rb') as f:
            files = {'audio': f}

            # Add the Bearer token to the headers for authentication
            headers = {
                "Authorization": f"Bearer {app_settings.editable_settings[SettingsKeys.WHISPER_SERVER_API_KEY.value]}"
            }

            try:
                verify = not app_settings.editable_settings["S2T Server Self-Signed Certificates"]

                # Send the request without verifying the SSL certificate
                response = requests.post(app_settings.editable_settings[SettingsKeys.WHISPER_ENDPOINT.value], headers=headers, files=files, verify=verify)

                response.raise_for_status()

                # check if canceled, if so do not update the UI
                if not is_audio_processing_whole_canceled.is_set():
                    # Update the UI with the transcribed text
                    transcribed_text = response.json()['text']
                    user_input.scrolled_text.configure(state='normal')
                    user_input.scrolled_text.delete("1.0", tk.END)
                    user_input.scrolled_text.insert(tk.END, transcribed_text)

                    # Send the transcribed text and receive a response
                    send_and_receive()
            except Exception as e:
                # log error message
                #TODO: Implment proper logging to system
                print(f"An error occurred: {e}")
                # Display an error message to the user
                user_input.scrolled_text.configure(state='normal')
                user_input.scrolled_text.delete("1.0", tk.END)
                user_input.scrolled_text.insert(tk.END, f"An error occurred: {e}")
                user_input.scrolled_text.configure(state='disabled')
            finally:
                # done with file clean up
                f.close()
                if os.path.exists(file_to_send) and delete_file:
                    os.remove(file_to_send)
                loading_window.destroy()

def kill_thread(thread_id):
    """
    Terminate a thread with a given thread ID.

    This function forcibly terminates a thread by raising a `SystemExit` exception in its context.
    **Use with caution**, as this method is not safe and can lead to unpredictable behavior, 
    including corruption of shared resources or deadlocks.

    :param thread_id: The ID of the thread to terminate.
    :type thread_id: int
    :raises ValueError: If the thread ID is invalid.
    :raises SystemError: If the operation fails due to an unexpected state.
    """
    # Call the C function `PyThreadState_SetAsyncExc` to asynchronously raise
    # an exception in the target thread's context.
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread_id),  # The thread ID to target (converted to `long`).
        ctypes.py_object(SystemExit)  # The exception to raise in the thread.
    )

    # Check the result of the function call.
    if res == 0:
        # If 0 is returned, the thread ID is invalid.
        raise ValueError(f"Invalid thread ID: {thread_id}")
    elif res > 1:
        # If more than one thread was affected, something went wrong.
        # Reset the state to prevent corrupting other threads.
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def send_and_receive():
    global use_aiscribe, user_message
    user_message = user_input.scrolled_text.get("1.0", tk.END).strip()
    display_text(NOTE_CREATION)
    threaded_handle_message(user_message)

        

def display_text(text):
    response_display.scrolled_text.configure(state='normal')
    response_display.scrolled_text.delete("1.0", tk.END)
    response_display.scrolled_text.insert(tk.END, f"{text}\n")
    response_display.scrolled_text.configure(fg='black')
    response_display.scrolled_text.configure(state='disabled')

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
        user_input.scrolled_text.configure(state='normal')
        user_input.scrolled_text.config(fg='black')
        user_input.scrolled_text.delete("1.0", tk.END)
        user_input.scrolled_text.insert(tk.END, transcript_text)
        response_display.scrolled_text.configure(state='normal')
        response_display.scrolled_text.delete('1.0', tk.END)
        response_display.scrolled_text.insert('1.0', response_text)
        response_display.scrolled_text.config(fg='black')
        response_display.scrolled_text.configure(state='disabled')
        pyperclip.copy(response_text)

def send_text_to_api(edited_text):
    headers = {
        "Authorization": f"Bearer {app_settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    payload = {}

    try:
        payload = {
            "model": app_settings.editable_settings["Model"].strip(),
            "messages": [
                {"role": "user", "content": edited_text}
            ],
            "temperature": float(app_settings.editable_settings["temperature"]),
            "top_p": float(app_settings.editable_settings["top_p"]),
            "top_k": int(app_settings.editable_settings["top_k"]),
            "tfs": float(app_settings.editable_settings["tfs"]),
        }

        if app_settings.editable_settings["best_of"]:
            payload["best_of"] = int(app_settings.editable_settings["best_of"])
            
    except ValueError as e:
        payload = {
            "model": app_settings.editable_settings["Model"].strip(),
            "messages": [
                {"role": "user", "content": edited_text}
            ],
            "temperature": 0.1,
            "top_p": 0.4,
            "top_k": 30,
            "best_of": 6,
            "tfs": 0.97,
        }

        if app_settings.editable_settings["best_of"]:
            payload["best_of"] = int(app_settings.editable_settings["best_of"])

        print(f"Error parsing settings: {e}. Using default settings.")

    try:

        if app_settings.editable_settings["Model Endpoint"].endswith('/'):
            app_settings.editable_settings["Model Endpoint"] = app_settings.editable_settings["Model Endpoint"][:-1]

        # Open API Style
        verify = not app_settings.editable_settings["AI Server Self-Signed Certificates"]
        response = requests.post(app_settings.editable_settings["Model Endpoint"]+"/chat/completions", headers=headers, json=payload, verify=verify)

        response.raise_for_status()
        response_data = response.json()
        response_text = (response_data['choices'][0]['message']['content'])
        return response_text

        #############################################################
        #                                                           #
        #                   OpenAI API Style                        #
        #           Uncomment to use API Style Selector             #
        #                                                           #
        #############################################################
        
        # if app_settings.API_STYLE == "OpenAI":                    
        # elif app_settings.API_STYLE == "KoboldCpp":
        #     prompt = get_prompt(edited_text)

        #     verify = not app_settings.editable_settings["AI Server Self-Signed Certificates"]
        #     response = requests.post(app_settings.editable_settings["Model Endpoint"] + "/api/v1/generate", json=prompt, verify=verify)

        #     if response.status_code == 200:
        #         results = response.json()['results']
        #         response_text = results[0]['text']
        #         response_text = response_text.replace("  ", " ").strip()
        #         return response_text

    except Exception as e:
        raise e

def send_text_to_localmodel(edited_text):  
    # Send prompt to local model and get response
    if ModelManager.local_model is None:
        ModelManager.setup_model(app_settings=app_settings, root=root)

        timer = 0
        while ModelManager.local_model is None and timer < 30:
            timer += 0.1
            time.sleep(0.1)
        

    return ModelManager.local_model.generate_response(
        edited_text,
        max_tokens=int(app_settings.editable_settings["max_length"]),
        temperature=float(app_settings.editable_settings["temperature"]),
        top_p=float(app_settings.editable_settings["top_p"]),
        repeat_penalty=float(app_settings.editable_settings["rep_pen"]),
    )

    


def send_text_to_chatgpt(edited_text):  
    if app_settings.editable_settings["Use Local LLM"]:
        return send_text_to_localmodel(edited_text)
    else:
        return send_text_to_api(edited_text)

def generate_note(formatted_message):
            try:
                # If note generation is on
                if use_aiscribe:
                    # If pre-processing is enabled
                    if app_settings.editable_settings["Use Pre-Processing"]:
                        #Generate Facts List
                        list_of_facts = send_text_to_chatgpt(f"{app_settings.editable_settings['Pre-Processing']} {formatted_message}")
                        
                        #Make a note from the facts
                        medical_note = send_text_to_chatgpt(f"{app_settings.AISCRIBE} {list_of_facts} {app_settings.AISCRIBE2}")

                        # If post-processing is enabled check the note over
                        if app_settings.editable_settings["Use Post-Processing"]:
                            post_processed_note = send_text_to_chatgpt(f"{app_settings.editable_settings['Post-Processing']}\nFacts:{list_of_facts}\nNotes:{medical_note}")
                            update_gui_with_response(post_processed_note)
                        else:
                            update_gui_with_response(medical_note)

                    else: # If pre-processing is not enabled thhen just generate the note
                        medical_note = send_text_to_chatgpt(f"{app_settings.AISCRIBE} {formatted_message} {app_settings.AISCRIBE2}")

                        if app_settings.editable_settings["Use Post-Processing"]:
                            post_processed_note = send_text_to_chatgpt(f"{app_settings.editable_settings['Post-Processing']}\nNotes:{medical_note}")
                            update_gui_with_response(post_processed_note)
                        else:
                            update_gui_with_response(medical_note)
                else: # do not generate note just send text directly to AI 
                    ai_response = send_text_to_chatgpt(formatted_message)
                    update_gui_with_response(ai_response)

                return True
            except Exception as e:
                #Logg
                #TODO: Implement proper logging to system event logger
                print(f"An error occurred: {e}")
                display_text(f"An error occurred: {e}")
                return False

def show_edit_transcription_popup(formatted_message):
    scrubber = scrubadub.Scrubber()

    scrubbed_message = scrubadub.clean(formatted_message)

    pattern = r'\b\d{10}\b'     # Any 10 digit number, looks like OHIP
    cleaned_message = re.sub(pattern,'{{OHIP}}',scrubbed_message)

    if (app_settings.editable_settings["Use Local LLM"] or is_private_ip(app_settings.editable_settings["Model Endpoint"])) and not app_settings.editable_settings["Show Scrub PHI"]:
        generate_note_thread(cleaned_message)
        return
    
    popup = tk.Toplevel(root)
    popup.title("Scrub PHI Prior to GPT")
    popup.iconbitmap(get_file_path('assets','logo.ico'))
    text_area = scrolledtext.ScrolledText(popup, height=20, width=80)
    text_area.pack(padx=10, pady=10)
    text_area.insert(tk.END, cleaned_message)

    def on_proceed():
        edited_text = text_area.get("1.0", tk.END).strip()
        popup.destroy()
        generate_note_thread(edited_text)        

    proceed_button = tk.Button(popup, text="Proceed", command=on_proceed)
    proceed_button.pack(side=tk.RIGHT, padx=10, pady=10)

    # Cancel button
    cancel_button = tk.Button(popup, text="Cancel", command=popup.destroy)
    cancel_button.pack(side=tk.LEFT, padx=10, pady=10)



def generate_note_thread(text: str):
    """
    Generate a note from the given text and update the GUI with the response.

    :param text: The text to generate a note from.
    :type text: str
    """
    global GENERATION_THREAD_ID

    thread = threading.Thread(target=generate_note, args=(text,))
    thread.start()

    GENERATION_THREAD_ID = thread.ident

    def cancel_note_generation(thread_id):
        """Cancels any ongoing note generation.
        
        Sets the global flag to stop note generation operations.
        """
        global GENERATION_THREAD_ID

        try:
            kill_thread(thread_id)
        except Exception as e:
            # Log the error message
            # TODO implment system logger
            print(f"An error occurred: {e}")
        finally:
            GENERATION_THREAD_ID = None

    loading_window = LoadingWindow(root, "Generating Note.", "Generating Note. Please wait.", on_cancel=lambda: cancel_note_generation(GENERATION_THREAD_ID))
    

    def check_thread_status(thread, loading_window):
        if thread.is_alive():
            root.after(500, lambda: check_thread_status(thread, loading_window))
        else:
            loading_window.destroy()

    root.after(500, lambda: check_thread_status(thread, loading_window))

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

# Initialize variables to store window geometry for switching between views
last_full_position = None
last_minimal_position = None

def toggle_view():
    """
    Toggles the user interface between a full view and a minimal view.

    Full view includes all UI components, while minimal view limits the interface
    to essential controls, reducing screen space usage. The function also manages
    window properties, button states, and binds/unbinds hover events for transparency.
    """
    
    if current_view == "full":  # Transition to minimal view
        set_minimal_view()
    
    else:  # Transition back to full view
        set_full_view()

def set_full_view():
    """
    Configures the application to display the full view interface.

    Actions performed:
    - Reconfigure button dimensions and text.
    - Show all hidden UI components.
    - Reset window attributes such as size, transparency, and 'always on top' behavior.
    - Create the Docker status bar.
    - Restore the last known full view geometry if available.

    Global Variables:
    - current_view: Tracks the current interface state ('full' or 'minimal').
    - last_minimal_position: Saves the geometry of the window when switching from minimal view.
    """
    global current_view, last_minimal_position

    # Reset button sizes and placements for full view
    mic_button.config(width=11, height=2)
    pause_button.config(width=11, height=2)
    switch_view_button.config(width=11, height=2, text="Minimize View")

    # Show all UI components
    user_input.grid()
    send_button.grid()
    clear_button.grid()
    toggle_button.grid()
    upload_button.grid()
    response_display.grid()
    timestamp_listbox.grid()
    mic_button.grid(row=1, column=1, pady=5, padx=0,sticky='nsew')
    pause_button.grid(row=1, column=2, pady=5, padx=0,sticky='nsew')
    switch_view_button.grid(row=1, column=7, pady=5, padx=0,sticky='nsew')
    blinking_circle_canvas.grid(row=1, column=8, padx=0,pady=5)

    window.toggle_menu_bar(enable=True)

    # Reconfigure button styles and text
    mic_button.config(bg="red" if is_recording else DEFAULT_BUTTON_COLOUR,
                      text="Stop\nRecording" if is_recording else "Start\nRecording")
    pause_button.config(bg="red" if is_paused else DEFAULT_BUTTON_COLOUR,
                        text="Resume" if is_paused else "Pause")

    # Unbind transparency events and reset window properties
    root.unbind('<Enter>')
    root.unbind('<Leave>')
    root.attributes('-alpha', 1.0)
    root.attributes('-topmost', False)
    root.minsize(900, 400)
    current_view = "full"

    # create docker_status bar if enabled
    if app_settings.editable_settings["Use Docker Status Bar"]:
        window.create_docker_status_bar()

    if app_settings.editable_settings["Enable Scribe Template"]:
        window.destroy_scribe_template()
        window.create_scribe_template()

    # Save minimal view geometry and restore last full view geometry
    last_minimal_position = root.geometry()
    if last_full_position is not None:
        root.geometry(last_full_position)

    # Disable to make the window an app(show taskbar icon)
    # root.attributes('-toolwindow', False)


def set_minimal_view():

    """
    Configures the application to display the minimal view interface.

    Actions performed:
    - Reconfigure button dimensions and text.
    - Hide non-essential UI components.
    - Bind transparency hover events for better focus.
    - Adjust window attributes such as size, transparency, and 'always on top' behavior.
    - Destroy and optionally recreate specific components like the Scribe template.

    Global Variables:
    - current_view: Tracks the current interface state ('full' or 'minimal').
    - last_full_position: Saves the geometry of the window when switching from full view.
    """
    global current_view, last_full_position

    # Remove all non-essential UI components
    user_input.grid_remove()
    send_button.grid_remove()
    clear_button.grid_remove()
    toggle_button.grid_remove()
    upload_button.grid_remove()
    response_display.grid_remove()
    timestamp_listbox.grid_remove()
    blinking_circle_canvas.grid_remove()

    # Configure minimal view button sizes and placements
    mic_button.config(width=2, height=1)
    pause_button.config(width=2, height=1)
    switch_view_button.config(width=2, height=1)

    mic_button.grid(row=0, column=0, pady=2, padx=2)
    pause_button.grid(row=0, column=1, pady=2, padx=2)
    switch_view_button.grid(row=0, column=2, pady=2, padx=2)

    # Update button text based on recording and pause states
    mic_button.config(text="⏹️" if is_recording else "🎤")
    pause_button.config(text="▶️" if is_paused else "⏸️")
    switch_view_button.config(text="⬆️")  # Minimal view indicator

    blinking_circle_canvas.grid(row=0, column=3, pady=2, padx=2)

    window.toggle_menu_bar(enable=False)

    # Update window properties for minimal view
    root.attributes('-topmost', True)
    root.minsize(125, 50)  # Smaller minimum size for minimal view
    current_view = "minimal"

    # Set hover transparency events
    def on_enter(e):
        if e.widget == root:  # Ensure the event is from the root window
            root.attributes('-alpha', 1.0)

    def on_leave(e):
        if e.widget == root:  # Ensure the event is from the root window
            root.attributes('-alpha', 0.70)

    root.bind('<Enter>', on_enter)
    root.bind('<Leave>', on_leave)

    # Destroy and re-create components as needed
    window.destroy_docker_status_bar()
    if app_settings.editable_settings["Enable Scribe Template"]:
        window.destroy_scribe_template()
        window.create_scribe_template(row=1, column=0, columnspan=3, pady=5)

    # Save full view geometry and restore last minimal view geometry
    last_full_position = root.geometry()
    if last_minimal_position:
        root.geometry(last_minimal_position)

    # Enable to make the window a tool window (no taskbar icon)
    # root.attributes('-toolwindow', True)

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

def load_stt_model(event=None):
    thread = threading.Thread(target=_load_stt_model_thread, daemon=True)
    thread.start()

def _load_stt_model_thread():
    global stt_local_model
    model = app_settings.editable_settings["Whisper Model"].strip()
    # Create a loading window to display the loading message
    stt_loading_window = LoadingWindow(root, "Speech to Text", "Loading Speech to Text. Please wait.")
    print(f"Loading STT model: {model}")
    try:
        # Load the specified Whisper model
        stt_local_model = whisper.load_model(model)
        print("STT model loaded successfully.")
    except Exception as e:
        # Log the error message
        print(f"An error occurred while loading STT: {e}")
        stt_local_model = None
        messagebox.showerror("Error", f"An error occurred while loading the STT model: {e}")
    finally:
        stt_loading_window.destroy()
        print("Closing STT loading window.")


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
root.grid_columnconfigure(11, weight=1, minsize=10)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=0)
root.grid_rowconfigure(4, weight=0)


window.load_main_window()

user_input = CustomTextBox(root, height=12)
user_input.grid(row=0, column=1, columnspan=8, padx=5, pady=15, sticky='nsew')


# Insert placeholder text
user_input.scrolled_text.insert("1.0", "Transcript of Conversation")
user_input.scrolled_text.config(fg='grey')

# Bind events to remove or add the placeholder with arguments
user_input.scrolled_text.bind("<FocusIn>", lambda event: remove_placeholder(event, user_input.scrolled_text, "Transcript of Conversation"))
user_input.scrolled_text.bind("<FocusOut>", lambda event: add_placeholder(event, user_input.scrolled_text, "Transcript of Conversation"))

mic_button = tk.Button(root, text="Start\nRecording", command=lambda: (threaded_toggle_recording()), height=2, width=11)
mic_button.grid(row=1, column=1, pady=5, sticky='nsew')

send_button = tk.Button(root, text="Generate Note", command=send_and_flash, height=2, width=11)
send_button.grid(row=1, column=3, pady=5, sticky='nsew')

pause_button = tk.Button(root, text="Pause", command=toggle_pause, height=2, width=11)
pause_button.grid(row=1, column=2, pady=5, sticky='nsew')

clear_button = tk.Button(root, text="Clear", command=clear_application_press, height=2, width=11)
clear_button.grid(row=1, column=4, pady=5, sticky='nsew')

toggle_button = tk.Button(root, text="AI Scribe\nON", command=toggle_aiscribe, height=2, width=11)
toggle_button.grid(row=1, column=5, pady=5, sticky='nsew')

upload_button = tk.Button(root, text="Upload\nRecording", command=upload_file, height=2, width=11)
upload_button.grid(row=1, column=6, pady=5, sticky='nsew')

switch_view_button = tk.Button(root, text="Minimize View", command=toggle_view, height=2, width=11)
switch_view_button.grid(row=1, column=7, pady=5, sticky='nsew')

blinking_circle_canvas = tk.Canvas(root, width=20, height=20)
blinking_circle_canvas.grid(row=1, column=8, pady=5)
circle = blinking_circle_canvas.create_oval(5, 5, 15, 15, fill='white')

response_display = CustomTextBox(root, height=13, state="disabled")
response_display.grid(row=2, column=1, columnspan=8, padx=5, pady=15, sticky='nsew')

# Insert placeholder text
response_display.scrolled_text.configure(state='normal')
response_display.scrolled_text.insert("1.0", "Medical Note")
response_display.scrolled_text.config(fg='grey')
response_display.scrolled_text.configure(state='disabled')

if app_settings.editable_settings["Enable Scribe Template"]:
    window.create_scribe_template()

timestamp_listbox = tk.Listbox(root, height=30)
timestamp_listbox.grid(row=0, column=9, columnspan=2, rowspan=3, padx=5, pady=15, sticky='nsew')
timestamp_listbox.bind('<<ListboxSelect>>', show_response)
timestamp_listbox.insert(tk.END, "Temporary Note History")
timestamp_listbox.config(fg='grey')

window.update_aiscribe_texts(None)
# Bind Alt+P to send_and_receive function
root.bind('<Alt-p>', lambda event: pause_button.invoke())

# Bind Alt+R to toggle_recording function
root.bind('<Alt-r>', lambda event: mic_button.invoke())

#set min size
root.minsize(900, 400)



#Wait for the UI root to be intialized then load the model. If using local llm.
if app_settings.editable_settings["Use Local LLM"]:
    root.after(100, lambda:(ModelManager.setup_model(app_settings=app_settings, root=root)))  

if app_settings.editable_settings[SettingsKeys.LOCAL_WHISPER.value]:
    # Inform the user that Local Whisper is being used for transcription
    print("Using Local Whisper for transcription.")
    root.after(100, lambda: (load_stt_model()))

root.bind("<<LoadSttModel>>", load_stt_model)

root.mainloop()

p.terminate()
