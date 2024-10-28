import tkinter as tk
from tkinter import messagebox, Toplevel
import UI.MainWindow as mw
import Tooltip as tt
import markdown as md
from tkinterhtml import HtmlFrame
from UI.SettingsWindowUI import SettingsWindowUI

class MainWindowUI:
    """
    This class handles the user interface (UI) for the main application window, 
    including the Docker status bar for managing the LLM and Whisper containers.

    :param root: The root Tkinter window.
    :param settings: The application settings passed to control the containers' behavior.
    """
    
    def __init__(self, root, settings):
        """
        Initialize the MainWindowUI class.

        :param root: The Tkinter root window.
        :param settings: The application settings used to control container states.
        """
        self.root = root  # Tkinter root window
        self.docker_status_bar = None  # Docker status bar frame
        self.app_settings = settings  # Application settings
        self.logic = mw.MainWindow()  # Logic to control the container behavior
        self.setting_window = SettingsWindowUI(self.app_settings, self)  # Settings window

    def create_docker_status_bar(self):
        """
        Create a Docker status bar to display the status of the LLM and Whisper containers.
        Adds start and stop buttons for each container and tooltips for their status.
        """
        if self.logic.container_manager.client is None:
            print("Docker client not initialized, removing status bar.")
            return
        
        if self.docker_status_bar is not None:
            return

        # Create the frame for the Docker status bar, placed at the bottom of the window
        self.docker_status_bar = tk.Frame(self.root, bd=1, relief=tk.SUNKEN)
        self.docker_status_bar.grid(row=4, column=0, columnspan=14, sticky='nsew')

        # Add a label to indicate Docker container status section
        docker_status = tk.Label(self.docker_status_bar, text="Docker Containers: ")
        docker_status.pack(side=tk.LEFT)

        # Add LLM container status label
        llm_status = tk.Label(self.docker_status_bar, text="LLM Container Status:", padx=10)
        llm_status.pack(side=tk.LEFT)
        # Tooltip explaining the LLM container's purpose
        tt.Tooltip(llm_status, text="The LLM container is essential for generating responses and creating the SOAP notes. This service must be running.")

        # Add status dot for LLM (default: red)
        llm_dot = tk.Label(self.docker_status_bar, text='●', fg='red')
        llm_dot.pack(side=tk.LEFT)
        # Tooltip explaining the color of the status dot (green = running, red = stopped)
        tt.Tooltip(llm_dot, text="LLM Container Status: Green = Running, Red = Stopped")

        # Add Whisper server status label
        whisper_status = tk.Label(self.docker_status_bar, text="Whisper Server Status:", padx=10)
        whisper_status.pack(side=tk.LEFT)
        # Tooltip explaining the Whisper server's purpose
        tt.Tooltip(whisper_status, text="The whisper server is responsible for transcribing microphone input to text. This service must be running.")

        # Add status dot for Whisper (default: red)
        whisper_dot = tk.Label(self.docker_status_bar, text='●', fg='red')
        whisper_dot.pack(side=tk.LEFT)
        # Tooltip explaining the color of the status dot (green = running, red = stopped)
        tt.Tooltip(whisper_dot, text="Whisper Status: Green = Running, Red = Stopped")

        # Start button for Whisper container with a command to invoke the start method from logic
        start_whisper_button = tk.Button(self.docker_status_bar, text="Start Whisper", command=lambda: self.logic.start_whisper_container(whisper_dot, self.app_settings))
        start_whisper_button.pack(side=tk.RIGHT)

        # Start button for LLM container with a command to invoke the start method from logic
        start_llm_button = tk.Button(self.docker_status_bar, text="Start LLM", command=lambda: self.logic.start_LLM_container(llm_dot, self.app_settings))
        start_llm_button.pack(side=tk.RIGHT)

        # Stop button for Whisper container with a command to invoke the stop method from logic
        stop_whisper_button = tk.Button(self.docker_status_bar, text="Stop Whisper", command=lambda: self.logic.stop_whisper_container(whisper_dot, self.app_settings))
        stop_whisper_button.pack(side=tk.RIGHT)

        # Stop button for LLM container with a command to invoke the stop method from logic
        stop_llm_button = tk.Button(self.docker_status_bar, text="Stop LLM", command=lambda: self.logic.stop_LLM_container(llm_dot, self.app_settings))
        stop_llm_button.pack(side=tk.RIGHT)

    def destroy_docker_status_bar(self):
        """
        Destroy the Docker status bar if it exists.
        """
        if self.docker_status_bar is not None:
            self.docker_status_bar.destroy()
            self.docker_status_bar = None

    def load_main_window(self):
        """
        Load the main window of the application.
        This method initializes the main window components, including the menu bar.
        """
        self._create_menu_bar()

    def _create_menu_bar(self):
        """
        Private method to create menu bar.
        Create a menu bar with a Help menu.
        This method sets up the menu bar at the top of the main window and adds a Help menu with an About option.
        """
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        self._create_settings_menu()
        self._create_help_menu()

    def _create_settings_menu(self):
        # Add Settings menu
        self.menu_bar.add_command(label="Settings", command=self.setting_window.open_settings_window)

    def _create_help_menu(self):
        # Add Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=lambda: self._show_help_content('src/FreeScribe.client/markdown/help/about.md'))

    
    def _show_help_content(self, file_path):
        """
        Private method to display help/about information.
        Display help information in a message box.
        This method shows a message box with information about the application when the About option is selected from the Help menu.
        """
        help_window = Toplevel(self.root)
        help_window.title("About")

        with open(file_path, "r") as file:
            readme = file.read()
        
        # Convert Markdown to HTML
        html_content = md.markdown(readme)

        # Display the HTML content in a new window using tkinterhtml
        html_frame = HtmlFrame(help_window, horizontal_scrollbar="auto")
        html_frame.set_content(html_content)
        html_frame.pack(fill="both", expand=True)


