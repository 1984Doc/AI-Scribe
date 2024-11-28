import tkinter as tk
from tkinter import ttk
import pyaudio

class MicrophoneSelector:

    PYAUDIO = pyaudio.PyAudio()
    SELECTED_MICROPHONE_INDEX = 1
    SELECTED_MICROPHONE_NAME = PYAUDIO.get_device_info_by_index(SELECTED_MICROPHONE_INDEX)['name']

    def __init__(self, root, row, column, app_settings):
        self.root = root
        self.settings = app_settings

        # Create UI elements
        self.label = tk.Label(root, text="Select a Microphone:")
        self.label.grid(row=row, column=0,pady=5, sticky="w")

        self.dropdown = ttk.Combobox(root, state="readonly", width=15)
        self.dropdown.grid(row=row, pady=5, column=1)

        # Populate microphones in the dropdown
        self.update_microphones()

        # Bind selection event
        self.dropdown.bind("<<ComboboxSelected>>", self.on_mic_selected)

    def update_microphones(self):
        # Get microphone device list
        self.mic_info = []
        mic_names = []
        selected_index = -1

        for i in range(MicrophoneSelector.PYAUDIO.get_device_count()):
            device_info = MicrophoneSelector.PYAUDIO.get_device_info_by_index(i)

            if device_info['maxInputChannels'] > 0:  # Filter input devices
                if device_info['name'] == self.settings.editable_settings["Current Mic"] and selected_index == -1:
                    selected_index = device_info["index"]

                if device_info['name'] not in mic_names:
                    mic_names.append(device_info['name'])
                    self.mic_info.append({"name": device_info["name"],"index": device_info["index"], "channels": device_info['maxInputChannels'], "defaultSampleRate": device_info['defaultSampleRate']})

        # Update dropdown
        self.dropdown['values'] = self.mic_list
        if self.mic_list:
            self.dropdown.current(0)  # Set the first microphone as default
            self.update_selected_microphone(0)  # Initialize selection

            self.update_selected_microphone(0)
        else:
            self.dropdown.set("No microphones available")
            self.update_selected_microphone(-1)

    def on_mic_selected(self, event):
        selected_index = self.dropdown.get()
        for mic in self.mic_info:
            if mic["name"] == selected_index:
                self.update_selected_microphone(mic["index"])
                break

    def update_selected_microphone(self, selected_index):
        if selected_index >= 0 and selected_index < len(self.mic_info):
            selected_mic = MicrophoneSelector.PYAUDIO.get_device_info_by_index(selected_index)
            MicrophoneSelector.SELECTED_MICROPHONE_INDEX = selected_mic["index"]
            MicrophoneSelector.SELECTED_MICROPHONE_NAME = selected_mic["name"]
        else:
            MicrophoneSelector.SELECTED_MICROPHONE_INDEX = None
            MicrophoneSelector.SELECTED_MICROPHONE_NAME = None

    def close(self):
        self.root.destroy()

    def get(self):
        return MicrophoneSelector.SELECTED_MICROPHONE_NAME
