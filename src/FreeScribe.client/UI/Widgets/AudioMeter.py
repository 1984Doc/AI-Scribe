import struct
import tkinter as tk
from tkinter import ttk
import pyaudio
import numpy as np
from threading import Thread

class AudioMeter(tk.Frame):
    """
    A Tkinter widget that displays an audio level meter.

    This widget captures audio input and displays the audio level in real-time.
    It includes a threshold slider to adjust the sensitivity of the meter.

    :param master: The parent widget.
    :type master: tkinter.Widget
    :param width: The width of the widget.
    :type width: int
    :param height: The height of the widget.
    :type height: int
    :param threshold: The initial threshold value for the audio meter.
    :type threshold: int
    """
    def __init__(self, master=None, width=400, height=100, threshold=750):
        """
        Initialize the AudioMeter widget.

        :param master: The parent widget.
        :type master: tkinter.Widget
        :param width: The width of the widget.
        :type width: int
        :param height: The height of the widget.
        :type height: int
        :param threshold: The initial threshold value for the audio meter.
        :type threshold: int
        """
        super().__init__(master)
        self.master = master
        self.width = width
        self.height = height
        self.running = False
        self.threshold = threshold  # Default threshold value - adjusted for int16 audio values
        self.setup_audio()
        self.create_widgets()
        
        # Bind the cleanup method to widget destruction
        self.bind('<Destroy>', self.cleanup)

    def cleanup(self, event=None):
        """
        Clean up resources when the widget is destroyed.

        This method stops the audio stream and terminates the PyAudio instance.

        :param event: The event that triggered the cleanup (default is None).
        :type event: tkinter.Event
        """
        if self.running:
            self.running = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=1.0)  # Wait for thread to finish
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.p:
                self.p.terminate()

    def destroy(self):
        """
        Override the destroy method to ensure cleanup.

        This method calls the cleanup method before destroying the widget.
        """
        self.cleanup()
        super().destroy()

    def setup_audio(self):
        """
        Set up the audio parameters for capturing audio input.

        This method initializes the PyAudio instance and sets the audio format,
        number of channels, sample rate, and chunk size.
        """
        # Adjusted CHUNK size for 16kHz to maintain similar update rate
        self.CHUNK = 512  # Reduced from 1024 to maintain similar time resolution
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000  # Changed from 44100 to 16000
        self.p = pyaudio.PyAudio()
        
    def create_widgets(self):
        """
        Create the UI elements for the audio meter.

        This method creates the slider for adjusting the threshold, the canvas
        for displaying the audio level, and the threshold line indicator.
        """
        # Create frame for slider
        self.slider_frame = tk.Frame(self)
        self.slider_frame.pack(fill='x', padx=5, pady=5)
        
        # Add threshold slider - adjusted range for int16 audio values
        self.threshold_slider = tk.Scale(
            self.slider_frame,
            from_=0,
            to=32767,  # Max value for 16-bit audio
            orient='horizontal',
            command=self.update_threshold,
            length=self.width
        )
        self.threshold_slider.set(self.threshold)  # Set default threshold
        self.threshold_slider.pack(side='left', fill='x', expand=True, padx=0)
               
        # Make the canvas shorter since we only need enough height for the bar
        self.canvas = tk.Canvas(
            self, 
            width=self.width,
            height=30,
            borderwidth=0,
            highlightthickness=0
        )
        self.canvas.pack(expand=True, fill='both', padx=0, pady=0)
        
        # Create horizontal level meter rectangle
        self.level_meter = self.canvas.create_rectangle(
            0, 5,
            0, 25,
            fill='green'
        )
        
        # Create threshold line indicator
        self.threshold_line = self.canvas.create_line(
            50, 0,
            50, 30,
            fill='red',
            width=2
        )
        
        self.toggle_monitoring()
    
    def update_threshold(self, value):
        """
        Update the threshold value and the visual indicator.

        This method updates the threshold value based on the slider position
        and adjusts the position of the threshold line on the canvas.

        :param value: The new threshold value from the slider.
        :type value: str
        """
        self.threshold = float(value)

        # Update threshold line position
        # Scale the threshold value to canvas width
        scaled_position = (float(value) / 32767) * 380
        self.canvas.coords(
            self.threshold_line,
            scaled_position, 0,
            scaled_position, 30
        )

    def toggle_monitoring(self):
        """
        Start or stop the audio monitoring.

        This method starts or stops the audio stream and the monitoring thread
        based on the current state of the widget.
        """
        if not self.running:
            self.running = True
            self.stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            self.monitoring_thread = Thread(target=self.update_meter)
            self.monitoring_thread.start()
        else:
            self.running = False
            self.stream.stop_stream()
            self.stream.close()
    
    def update_meter(self):
        """
        Continuously update the audio meter.

        This method reads audio data from the stream, calculates the maximum
        audio level, and updates the meter display on the main thread.
        """
        while self.running:
            try:
                # Read audio data
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                # Convert to integers
                audio_data = struct.unpack(f'{self.CHUNK}h', data)

                # Get max value
                max_value = max(abs(np.array(audio_data)))

                # Scale to 0-380 for display
                level = min(380, int((max_value / 32767) * 380))
                
                # Update meter on main thread
                self.master.after(0, self.update_meter_display, level)
            except Exception as e:
                print(f"Error: {e}")
                break
    
    def update_meter_display(self, level):
        """
        Update the meter display on the canvas.

        This method updates the position and color of the audio level meter
        based on the current audio level.

        :param level: The current audio level to display.
        :type level: int
        """
        # Update meter position
        self.canvas.coords(
            self.level_meter,
            0, 5,
            level, 25
        )
        
        # Color logic
        if level < 120:
            color = 'green'
        elif level < 250:
            color = 'yellow'
        else:
            color = 'red'
        self.canvas.itemconfig(self.level_meter, fill=color)
