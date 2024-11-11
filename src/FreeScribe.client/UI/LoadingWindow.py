import tkinter as tk
from tkinter import ttk
from utils.file_utils import get_file_path

class LoadingWindow:
    """
    A class to create and manage an animated processing popup window.
    
    This class creates a popup window with an animated ellipsis to indicate
    ongoing processing. The window cannot be closed manually by the user.
    
    :param parent: The parent window for this popup
    :type parent: tk.Tk or tk.Toplevel or None
    :param title: The title of the popup window
    :type title: str
    :param initial_text: The initial text to display in the popup
    :type initial_text: str
    
    :ivar popup: The main popup window
    :type popup: tk.Toplevel
    :ivar popup_label: The label widget containing the animated text
    :type popup_label: tk.Label
    :ivar animation_id: The identifier for the current animation timer
    :type animation_id: str
    
    Example
    -------
    >>> root = tk.Tk()
    >>> processing = LoadingWindow(root)
    >>> # Do some work here
    >>> processing.destroy()
    """

    def __init__(self, parent=None, title="Processing", initial_text="Loading"):
        """
        Initialize the processing popup window.
        
        :param parent: Parent window for this popup
        :type parent: tk.Tk or tk.Toplevel or None
        :param title: Title of the popup window
        :type title: str
        :param initial_text: Initial text to display
        :type initial_text: str
        """

        self.title = title
        self.initial_text = initial_text
        self.parent = parent
        self.initial_text = initial_text
        self.popup = tk.Toplevel(parent)
        self.popup.title(title)
        self.popup.geometry("200x100")
        self.popup.iconbitmap(get_file_path('assets','logo.ico'))

        if parent:
            # Center the popup window on the parent window
            parent.update_idletasks()
            x = parent.winfo_x() + (parent.winfo_width() - self.popup.winfo_reqwidth()) // 2
            y = parent.winfo_y() + (parent.winfo_height() - self.popup.winfo_reqheight()) // 2
            self.popup.geometry(f"+{x}+{y}")
            self.popup.transient(parent)

        # Use label and progress bar instead of animated text
        self.label = tk.Label(self.popup, text=initial_text)
        self.label.pack(pady=(10,5))
        self.progress = ttk.Progressbar(self.popup, mode='indeterminate')
        self.progress.pack(padx=20, pady=(0,10), fill='x')
        self.progress.start()

        # Make it topmost window
        self.popup.grab_set()

        #Not Resizable
        self.popup.resizable(False, False)
        
        # Disable closing of the popup manually
        self.popup.protocol("WM_DELETE_WINDOW", lambda: None)
    
    
    def destroy(self):
        """
        Clean up and destroy the popup window.
        
        This method performs the following cleanup operations:
        1. Cancels any pending animation updates
        2. Destroys the popup window
        
        Note
        ----
        This method should be called when you want to close the popup window,
        rather than destroying the window directly.
        
        Example
        -------
        >>> popup = LoadingWindow()
        >>> # Do some processing
        >>> popup.destroy()  # Properly clean up and close the window
        """
        # Cancel any pending animation
        if hasattr(self, 'animation_id'):
            self.popup.after_cancel(self.animation_id)
        
        # Destroy the window
        if self.popup:
            self.progress.stop()
            self.popup.destroy()
