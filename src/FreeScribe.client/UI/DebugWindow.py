import tkinter as tk
import io
import sys

# DualOutput class for capturing output to both the console and a buffer
class DualOutput:
    def __init__(self):
        self.buffer = io.StringIO()  # Buffer for capturing output
        self.original_stdout = sys.stdout  # Save the original stdout

    def write(self, message):
        self.original_stdout.write(message)  # Write to the console
        self.buffer.write(message)  # Write to the buffer

    def flush(self):
        self.original_stdout.flush()  # Ensure console output is flushed

    def get_buffer_content(self):
        return self.buffer.getvalue()  # Retrieve all buffered output
