from ContainerManager import ContainerManager
import tkinter as tk

class MainWindow:
    def __init__(self):
        """
        Initialize the main window of the application.
        """
        self.container_manager = ContainerManager()

    def start_LLM_container(self, widget_name, app_settings):
        """
        Start the LLM container.
        """
        try:
            self.container_manager.set_status_icon_color(widget_name, self.container_manager.start_container(app_settings.editable_settings["LLM Container Name"]))
            self.container_manager.set_status_icon_color(widget_name, self.container_manager.start_container(app_settings.editable_settings["LLM Caddy Container Name"]))
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred while starting the LLM container: {e}")

    def stop_LLM_container(self, widget_name, app_settings):
        """
        Stop the LLM container.
        """
        try:
            self.container_manager.set_status_icon_color(widget_name, self.container_manager.stop_container(app_settings.editable_settings["LLM Container Name"]))
            self.container_manager.set_status_icon_color(widget_name, self.container_manager.stop_container(app_settings.editable_settings["LLM Caddy Container Name"]))
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred while stoping the LLM container: {e}")

    def start_whisper_container(self, widget_name, app_settings):
        """
        Start the Whisper container.
        """
        try:
            self.container_manager.set_status_icon_color(widget_name, self.container_manager.start_container(app_settings.editable_settings["Whisper Container Name"]))
            self.container_manager.set_status_icon_color(widget_name, self.container_manager.start_container(app_settings.editable_settings["Whisper Caddy Container Name"]))
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred while starting the Whisper container: {e}")

    def stop_whisper_container(self, widget_name, app_settings):
        """
        Stop the Whisper container.
        """
        try:
            self.container_manager.set_status_icon_color(widget_name, self.container_manager.stop_container(app_settings.editable_settings["Whisper Container Name"]))
            self.container_manager.set_status_icon_color(widget_name, self.container_manager.stop_container(app_settings.editable_settings["Whisper Caddy Container Name"]))
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred while stopping the Whisper container: {e}")
