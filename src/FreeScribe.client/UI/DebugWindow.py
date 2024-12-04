import tkinter as tk
import io
import sys
from datetime import datetime

# DualOutput class for capturing output to both the console and a buffer
class DualOutput:

    buffer = None

    def __init__(self):
        DualOutput.buffer = io.StringIO()  # Buffer for capturing output
        self.original_stdout = sys.stdout  # Save the original stdout
        self.original_stderr = sys.stderr  # Save the original stderr

    def write(self, message):
        if message.strip():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if "\n" in message:  # Handle multi-line messages
                for line in message.splitlines():
                    if line.strip():
                        formatted_message = f"{timestamp} - {line}\n"
                        DualOutput.buffer.write(formatted_message)
            else:
                formatted_message = f"{timestamp} - {message}"
                DualOutput.buffer.write(formatted_message)
        else:
            DualOutput.buffer.write("\n")
        self.original_stdout.write(message)

    def flush(self):
        self.original_stdout.flush()  # Ensure console output is flushed

    @staticmethod
    def get_buffer_content():
        return DualOutput.buffer.getvalue()  # Retrieve all buffered output

# DebugPrintWindow class for the pop-up window
class DebugPrintWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)  # Create a new pop-up window

        self.window.title("Debug Output")  # Set title of the pop-up
        self.window.geometry("650x450")  # Set initial size of the pop-up

        # Create a Text widget for displaying captured output
        self.text_widget = tk.Text(self.window, wrap="none", width=80, height=20)
        self.text_widget.pack(padx=10, pady=(10, 0), fill=tk.BOTH, expand=True)  # Add some padding at the top

        # Create a Scrollbar
        scrollbar = tk.Scrollbar(self.text_widget)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Place the scrollbar on the right side

        # horizontal scrollbar
        hscrollbar = tk.Scrollbar(self.text_widget, orient=tk.HORIZONTAL)
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Attach the scrollbar to the Text widget
        scrollbar.config(command=self.text_widget.yview)
        self.text_widget.config(yscrollcommand=scrollbar.set)

        # Attach the horizontal scrollbar to the Text widget
        hscrollbar.config(command=self.text_widget.xview)
        self.text_widget.config(xscrollcommand=hscrollbar.set)


        # Add a Refresh Button
        refresh_button = tk.Button(self.window, text="Refresh", command=self.refresh_output)
        refresh_button.pack(pady=10)  # Add some padding around the button

        self.refresh_output()  # Refresh the output initially

    def refresh_output(self):
        # Fetch new content
        content = DualOutput.get_buffer_content()

        # Get current content in the Text widget
        current_content = self.text_widget.get("1.0", tk.END).strip()

        # Only append new lines if there is a difference
        if content != current_content:
            # Save the current scroll position
            top_line_index = self.text_widget.index("@0,0")

            # Clear the widget and insert the new content
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.END, content)

            # Restore scroll position
            self.text_widget.see(top_line_index)