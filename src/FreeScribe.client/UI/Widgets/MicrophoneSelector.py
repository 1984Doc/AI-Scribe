import tkinter as tk
from tkinter import ttk
import pyaudio


class MicrophoneSelector:

    SELECTED_MICROPHONE = 1

    def __init__(self, root, row, column):
        self.root = root

        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()

        # Create UI elements
        self.label = tk.Label(root, text="Select a Microphone:")
        self.label.grid(row=row, column=0,pady=5, sticky="w")

        self.dropdown = ttk.Combobox(root, state="readonly", width=15)
        self.dropdown.grid(row=row, pady=5, column=1)

        self.refresh_button = ttk.Button(root, text="↻", command=self.update_microphones)
        self.refresh_button.grid(row=row + 1,pady=5, column=1)

        # Populate microphones in the dropdown
        self.update_microphones()

        # Bind selection event
        self.dropdown.bind("<<ComboboxSelected>>", self.on_mic_selected)

    def update_microphones(self):
        # Get microphone device list
        self.mic_list = []
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:  # Filter input devices
                self.mic_list.append(device_info['name'])

        # Update dropdown
        self.dropdown['values'] = self.mic_list
        if self.mic_list:
            self.dropdown.current(0)  # Set the first microphone as default
        else:
            self.dropdown.set("No microphones available")

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
        self.audio.terminate()
        self.root.destroy()

