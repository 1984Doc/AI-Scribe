import tkinter as tk
from tkinter import ttk

class ContainerManagerUI:
    def open_docker_settings_popup(self):
        """
        Open the Docker settings popup window.
        """
        popup = tk.Toplevel()
        popup.title("Docker Settings")

        # Docker IP Address
        tk.Label(popup, text="Docker IP Address:").grid(row=0, column=0, padx=10, pady=10)
        docker_ip_entry = tk.Entry(popup)
        docker_ip_entry.grid(row=0, column=1, padx=10, pady=10)

        # Docker Port
        tk.Label(popup, text="Docker Port:").grid(row=1, column=0, padx=10, pady=10)
        docker_port_entry = tk.Entry(popup)
        docker_port_entry.grid(row=1, column=1, padx=10, pady=10)

        # Save Button
        save_button = tk.Button(popup, text="Save", command=lambda: self.save_docker_settings(docker_ip_entry.get(), docker_port_entry.get()))
        save_button.grid(row=2, column=0, columnspan=2, pady=10)

    def save_docker_settings(self, docker_ip, docker_port):
        """
        Save the Docker settings.
        """
        print(f"Docker IP: {docker_ip}, Docker Port: {docker_port}")
    
