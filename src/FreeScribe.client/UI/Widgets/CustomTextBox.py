"""
CustomTextBox.py

This software is released under the AGPL-3.0 license
Copyright (c) 2023-2024 Braedon Hendy

Further updates and packaging added in 2024 through the ClinicianFOCUS initiative, 
a collaboration with Dr. Braedon Hendy and Conestoga College Institute of Applied 
Learning and Technology as part of the CNERG+ applied research project, 
Unburdening Primary Healthcare: An Open-Source AI Clinician Partner Platform". 
Prof. Michael Yingbull (PI), Dr. Braedon Hendy (Partner), 
and Research Students - Software Developer Alex Simko, Pemba Sherpa (F24), and Naitik Patel.

Classes:
    CustomTextBox: Custom text box with copy text button overlay.
"""

import tkinter as tk
from tkinter import messagebox

class CustomTextBox(tk.Frame):
    """
    A custom text box widget with a built-in copy button.

    This widget extends the `tk.Frame` class and contains a `tk.scrolledtext.ScrolledText` widget
    with an additional copy button placed in the bottom-right corner. The copy button allows
    users to copy the entire content of the text widget to the clipboard.

    :param parent: The parent widget.
    :type parent: tk.Widget
    :param height: The height of the text widget in lines of text. Defaults to 10.
    :type height: int, optional
    :param state: The state of the text widget, which can be 'normal' or 'disabled'. Defaults to 'normal'.
    :type state: str, optional
    :param kwargs: Additional keyword arguments to pass to the `tk.Frame` constructor.
    """
    def __init__(self, parent, height=10, state='normal', **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        
        # Create scrolled text widget
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
        """
        Copy all text from the text widget to the clipboard.

        If an error occurs during the copy operation, a message box will display the error message.
        """
        try:
            # Clear clipboard and append new text
            self.clipboard_clear()
            text_content = self.scrolled_text.get("1.0", "end-1c")
            self.clipboard_append(text_content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy text: {str(e)}")
            
    def configure(self, **kwargs):
        """
        Configure the text widget with the given keyword arguments.

        :param kwargs: Keyword arguments to pass to the `configure` method of the `ScrolledText` widget.
        """
        self.scrolled_text.configure(**kwargs)
        
    def insert(self, index, text):
        """
        Insert text into the widget at the specified index.

        If the widget is in a 'disabled' state, it will be temporarily set to 'normal' to allow insertion.

        :param index: The index at which to insert the text.
        :type index: str
        :param text: The text to insert.
        :type text: str
        """
        current_state = self.scrolled_text['state']
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(index, text)
        self.scrolled_text.configure(state=current_state)
        
    def delete(self, start, end=None):
        """
        Delete text from the widget between the specified start and end indices.

        If the widget is in a 'disabled' state, it will be temporarily set to 'normal' to allow deletion.

        :param start: The start index of the text to delete.
        :type start: str
        :param end: The end index of the text to delete. If None, deletes from `start` to the end of the text.
        :type end: str, optional
        """
        current_state = self.scrolled_text['state']
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.delete(start, end)
        self.scrolled_text.configure(state=current_state)
        
    def get(self, start, end=None):
        """
        Get text from the widget between the specified start and end indices.

        :param start: The start index of the text to retrieve.
        :type start: str
        :param end: The end index of the text to retrieve. If None, retrieves from `start` to the end of the text.
        :type end: str, optional
        :return: The text between the specified indices.
        :rtype: str
        """
        return self.scrolled_text.get(start, end)