#https://stackoverflow.com/questions/20199863/how-do-you-overlap-widgets-frames-in-python-tkinter

import tkinter as tk
from tkinter import messagebox

class CustomTextBox(tk.Frame):
    def __init__(self, parent, height=10, state='normal', **kwargs):
        tk.Frame.__init__(self, parent)
        
        # create scrolled text
        self.scrolled_text = tk.scrolledtext.ScrolledText(self, wrap="word", height=height, state=state)
        self.scrolled_text.pack(side="left", fill="both", expand=True)

        # Create copy button in bottom right corner
        self.copy_button = tk.Button(
            self.scrolled_text,
            text="Copy Text",
            command=self.copy_text,
            relief="raised",
            borderwidth=1
        )
        self.copy_button.place(relx=1.0, rely=1.0, x=-2, y=-2, anchor="se")


    def copy_text(self):
        """Copy all text from the text widget to clipboard"""
        try:
            # Clear clipboard and append new text
            self.clipboard_clear()
            text_content = self.scrolled_text.get("1.0", "end-1c")
            self.clipboard_append(text_content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy text: {str(e)}")
            
    def configure(self, **kwargs):
        """Configure the text widget"""
        self.scrolled_text.configure(**kwargs)
        
    def insert(self, index, text):
        """Insert text into the widget"""
        current_state = self.scrolled_text['state']
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(index, text)
        self.scrolled_text.configure(state=current_state)
        
    def delete(self, start, end=None):
        """Delete text from the widget"""
        current_state = self.scrolled_text['state']
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.delete(start, end)
        self.scrolled_text.configure(state=current_state)
        
    def get(self, start, end=None):
        """Get text from the widget"""
        return self.scrolled_text.get(start, end)