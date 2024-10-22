import struct
import tkinter as tk
from tkinter import ttk
import pyaudio
import numpy as np
from threading import Thread

class AudioMeter(tk.Frame):
    def __init__(self, master=None, width=400, height=100, threshold=750):
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
        """Clean up resources when widget is destroyed"""
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
        """Override destroy method to ensure cleanup"""
        self.cleanup()
        super().destroy()

    def setup_audio(self):
        # Adjusted CHUNK size for 16kHz to maintain similar update rate
        self.CHUNK = 512  # Reduced from 1024 to maintain similar time resolution
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000  # Changed from 44100 to 16000
        self.p = pyaudio.PyAudio()
        
    def create_widgets(self):
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
        """Update threshold value and visual indicator"""
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