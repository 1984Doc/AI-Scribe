import tkinter as tk
from tkinter import ttk
import pyaudio

class MicrophoneSelector:
    """
    A class to manage microphone selection using a Tkinter UI.

    Attributes
    ----------
    PYAUDIO : pyaudio.PyAudio
        A PyAudio instance used to interact with audio devices.
    SELECTED_MICROPHONE_INDEX : int
        The index of the currently selected microphone.
    SELECTED_MICROPHONE_NAME : str
        The name of the currently selected microphone.
    """

    PYAUDIO = pyaudio.PyAudio()
    SELECTED_MICROPHONE_INDEX = 1
    SELECTED_MICROPHONE_NAME = PYAUDIO.get_device_info_by_index(SELECTED_MICROPHONE_INDEX)['name']

    def __init__(self, root, row, column, app_settings):
        """
        Initialize the MicrophoneSelector class.

        Parameters
        ----------
        root : tk.Tk
            The root Tkinter instance.
        row : int
            The row position in the Tkinter grid for UI elements.
        column : int
            The column position in the Tkinter grid for UI elements.
        app_settings : dict
            Application settings including editable settings.
        """
        self.root = root
        self.settings = app_settings

        # Create UI elements
        self.label = tk.Label(root, text="Select a Microphone:")
        self.label.grid(row=row, column=0, pady=5, sticky="w")

        self.dropdown = ttk.Combobox(root, state="readonly", width=15)
        self.dropdown.grid(row=row, pady=5, column=1)

        # Populate microphones in the dropdown
        self.update_microphones()

        # Bind selection event
        self.dropdown.bind("<<ComboboxSelected>>", self.on_mic_selected)

    def update_microphones(self):
        """
        Populate the dropdown with available microphones and update the selection.
        """
        # Get microphone device list
        self.mic_info = []
        mic_names = []
        selected_index = -1

        for i in range(MicrophoneSelector.PYAUDIO.get_device_count()):
            device_info = MicrophoneSelector.PYAUDIO.get_device_info_by_index(i)

            # Include devices with input channels
            if device_info['maxInputChannels'] > 0:
                # Check if the device matches the current mic setting
                if device_info['name'] == self.settings.editable_settings["Current Mic"] and selected_index == -1:
                    selected_index = device_info["index"]

                # Avoid duplicate microphone names
                if device_info['name'] not in mic_names:
                    mic_names.append(device_info['name'])
                    self.mic_info.append({
                        "name": device_info["name"],
                        "index": device_info["index"],
                        "channels": device_info['maxInputChannels'],
                        "defaultSampleRate": device_info['defaultSampleRate']
                    })

        # Update dropdown
        self.dropdown['values'] = mic_names
        if selected_index != -1:
            self.dropdown.set(self.settings.editable_settings["Current Mic"])
            self.update_selected_microphone(selected_index)
        elif mic_names:
            self.dropdown.current(0)  # Set the first microphone as default
            self.update_selected_microphone(0)  # Initialize selection
        else:
            self.dropdown.set("No microphones available")
            self.update_selected_microphone(-1)

    def on_mic_selected(self, event):
        """
        Handle the event when a microphone is selected from the dropdown.

        Parameters
        ----------
        event : tk.Event
            The event object containing information about the selection.
        """
        selected_index = self.dropdown.get()
        for mic in self.mic_info:
            if mic["name"] == selected_index:
                self.update_selected_microphone(mic["index"])
                break

    def update_selected_microphone(self, selected_index):
        """
        Update the selected microphone index and name.

        Parameters
        ----------
        selected_index : int
            The index of the selected microphone.
        """
        if selected_index >= 0 and selected_index < len(self.mic_info):
            selected_mic = MicrophoneSelector.PYAUDIO.get_device_info_by_index(selected_index)
            MicrophoneSelector.SELECTED_MICROPHONE_INDEX = selected_mic["index"]
            MicrophoneSelector.SELECTED_MICROPHONE_NAME = selected_mic["name"]
        else:
            MicrophoneSelector.SELECTED_MICROPHONE_INDEX = None
            MicrophoneSelector.SELECTED_MICROPHONE_NAME = None

    def close(self):
        """
        Close the Tkinter root window.
        """
        self.root.destroy()

    def get(self):
        """
        Get the name of the currently selected microphone.

        Returns
        -------
        str
            The name of the currently selected microphone.
        """
        return MicrophoneSelector.SELECTED_MICROPHONE_NAME
