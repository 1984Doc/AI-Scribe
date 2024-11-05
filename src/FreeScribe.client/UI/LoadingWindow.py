import tkinter as tk

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
        self.popup = tk.Toplevel(parent)
        self.popup.title(title)
        self.popup.geometry("200x100")
        
        # Create label
        self.popup_label = tk.Label(self.popup, text=initial_text)
        self.popup_label.pack(expand=True, padx=10, pady=10)
        
        # Disable closing of the popup manually
        self.popup.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Start the animation
        self.animate_text()
    
    def animate_text(self):
        """
        Animate the text by adding or removing ellipsis.
        
        This method updates the label text every 500ms, adding or removing
        dots to create an ellipsis animation effect. The animation continues
        until the popup is destroyed.
        
        Note
        ----
        This method is called automatically by __init__ and shouldn't
        typically be called directly.
        """
        current_text = self.popup_label.cget("text")
        base_text = "Processing Audio"
        
        if current_text.endswith("..."):
            self.popup_label.config(text=base_text)
        else:
            self.popup_label.config(text=current_text + ".")
            
        # Schedule the next animation update
        self.animation_id = self.popup.after(500, self.animate_text)
    
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
            self.popup.destroy()
