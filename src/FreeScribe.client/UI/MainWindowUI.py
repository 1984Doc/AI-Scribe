import tkinter as tk
import UI.MainWindow as mw
import Tooltip as tt

class MainWindowUI():
    def __init__(self, root, settings):
        self.root = root
        self.docker_status_bar = None
        self.app_settings = settings
        self.logic = mw.MainWindow() 

    def create_docker_status_bar(self):
        print("Creating Docker Status Bar")
        # Footer frame
        self.docker_status_bar = tk.Frame(self.root, bd=1, relief=tk.SUNKEN)
        self.docker_status_bar.grid(row=4, column=0, columnspan=14, sticky='nsew')

        # Docker status bar for llm and whisper containers
        docker_status = tk.Label(self.docker_status_bar, text="Docker Containers: ")
        docker_status.pack(side=tk.LEFT)

        # LLM Container Status
        llm_status = tk.Label(self.docker_status_bar, text="LLM Container Status:", padx=10)
        llm_status.pack(side=tk.LEFT)
        tt.Tooltip(llm_status, text="The LLM container is essential for generating responses and creating the SOAP notes. This service must be running.")

        # Red dot for LLM status
        llm_dot = tk.Label(self.docker_status_bar, text='●', fg='red')
        llm_dot.pack(side=tk.LEFT)
        tt.Tooltip(llm_dot, text="LLM Container Status: Green = Running, Red = Stopped")

        # Whisper Server Status
        whisper_status = tk.Label(self.docker_status_bar, text="Whisper Server Status:", padx=10)
        whisper_status.pack(side=tk.LEFT)
        tt.Tooltip(whisper_status, text="The whisper server is responsible for transcribing microphone input to text. This service must be running.")

        # Red dot for Whisper status
        whisper_dot = tk.Label(self.docker_status_bar, text='●', fg='red')
        whisper_dot.pack(side=tk.LEFT)
        tt.Tooltip(whisper_dot, text="Whisper Status: Green = Running, Red = Stopped")

        # start whisper container button
        start_whisper_button = tk.Button(self.docker_status_bar, text="Start Whisper", command=lambda: self.logic.start_whisper_container(whisper_dot, app_settings))
        start_whisper_button.pack(side=tk.RIGHT)

        # start local llm container button
        start_llm_button = tk.Button(self.docker_status_bar, text="Start LLM", command= lambda: self.logic.start_LLM_container(llm_dot, app_settings))
        start_llm_button.pack(side=tk.RIGHT)

        #stop whisper container button
        stop_whisper_button = tk.Button(self.docker_status_bar, text="Stop Whisper", command=lambda: window.stop_whisper_container(whisper_dot, app_settings))
        stop_whisper_button.pack(side=tk.RIGHT)

        #stop llm container button
        stop_llm_button = tk.Button(self.docker_status_bar, text="Stop LLM", command=lambda: window.stop_LLM_container(llm_dot, app_settings))
        stop_llm_button.pack(side=tk.RIGHT)

    def destroy_docker_status_bar(self):
        self.docker_status_bar.destroy()