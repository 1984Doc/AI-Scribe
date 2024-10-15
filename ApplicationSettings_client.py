"""
application_settings.py

This software is released under the AGPL-3.0 license
Copyright (c) 2023-2024 Braedon Hendy

Further updates and packaging added in 2024 through the ClinicianFOCUS initiative, 
a collaboration with Dr. Braedon Hendy and Conestoga College Institute of Applied 
Learning and Technology as part of the CNERG+ applied research project, 
Unburdening Primary Healthcare: An Open-Source AI Clinician Partner Platform". 
Prof. Michael Yingbull (PI), Dr. Braedon Hendy (Partner), 
and Research Students - Software Developer Alex Simko, Pemba Sherpa (F24), and Naitik Patel.

This module contains the ApplicationSettings class, which manages the settings for an
application that involves audio processing and external API interactions, including
KoboldCPP, WhisperAudio, and OpenAI services.

"""

import json
import tkinter as tk
from tkinter import ttk, messagebox


class ApplicationSettings:
    """
    Manages application settings related to audio processing and external API services.

    Attributes
    ----------
    KOBOLDCPP_IP : str
        The IP address for the Kobold CPP service.
    WHISPERAUDIO_IP : str
        The IP address for the Whisper Audio service.
    KOBOLDCPP_PORT : str
        The port for the Kobold CPP service.
    WHISPERAUDIO_PORT : str
        The port for the Whisper Audio service.
    SSL_ENABLE : str
        Whether SSL is enabled ('1' for enabled, '0' for disabled).
    SSL_SELFCERT : str
        Whether self-signed certificates are used ('1' for enabled, '0' for disabled).
    OPENAI_API_KEY : str
        The API key for OpenAI integration.
    AISCRIBE : str
        Placeholder for the first AI Scribe settings.
    AISCRIBE2 : str
        Placeholder for the second AI Scribe settings.
    API_STYLE : str
        The API style to be used (default is 'OpenAI').

    editable_settings : dict
        A dictionary containing user-editable settings such as model parameters, audio 
        settings, and real-time processing configurations.
    
    Methods
    -------
    load_settings_from_file():
        Loads settings from a JSON file and updates the internal state.
    save_settings_to_file():
        Saves the current settings to a JSON file.
    save_settings(koboldcpp_ip, whisperaudio_ip, openai_api_key, aiscribe_text, aiscribe2_text, 
                  settings_window, koboldcpp_port, whisperaudio_port, ssl_enable, ssl_selfcert, api_style):
        Saves the current settings, including API keys, IP addresses, and user-defined parameters.
    open_settings_window():
        Opens the settings window, allowing the user to modify and save application settings.
    load_aiscribe_from_file():
        Loads the first AI Scribe text from a file.
    load_aiscribe2_from_file():
        Loads the second AI Scribe text from a file.
    build_url(ip, port):
        Constructs a URL based on IP, port, and SSL settings.
    """

    def __init__(self):
        """Initializes the ApplicationSettings with default values."""
        self.KOBOLDCPP_IP = "192.168.1.195"
        self.WHISPERAUDIO_IP = "192.168.1.195"
        self.KOBOLDCPP_PORT = "5001"
        self.WHISPERAUDIO_PORT = "8000"
        self.SSL_ENABLE = "0"
        self.SSL_SELFCERT = "1"
        self.OPENAI_API_KEY = "None"
        self.AISCRIBE = ""
        self.AISCRIBE2 = ""
        self.API_STYLE = "OpenAI"

        self.KOBOLDCPP_ENDPOINT = None
        self.WHISPERAUDIO_ENDPOINT = None

        self.basic_settings = {
            "Model",
            "Model Endpoint",
            "Local Whisper",
            "Whisper Server API Key",
            "Whisper Model",
            "Real Time",
        }

        self.advanced_settings = {
            "use_story",
            "use_memory",
            "use_authors_note",
            "use_world_info",
            "max_context_length",
            "max_length",
            "rep_pen",
            "rep_pen_range",
            "rep_pen_slope",
            "temperature",
            "tfs",
            "top_a",
            "top_k",
            "top_p",
            "typical",
            "sampler_order",
            "singleline",
            "frmttriminc",
            "frmtrmblln",
            "Real Time Audio Length",
            "Real Time Silence Length",
            "Silence cut-off"
        }

        self.editable_settings = {
            "Model": "gpt-4",
            "Model Endpoint": "https://api.openai.com/v1/",
            "use_story": False,
            "use_memory": False,
            "use_authors_note": False,
            "use_world_info": False,
            "max_context_length": 5000,
            "max_length": 400,
            "rep_pen": 1.1,
            "rep_pen_range": 5000,
            "rep_pen_slope": 0.7,
            "temperature": 0.1,
            "tfs": 0.97,
            "top_a": 0.8,
            "top_k": 30,
            "top_p": 0.4,
            "typical": 0.19,
            "sampler_order": "[6, 0, 1, 3, 4, 2, 5]",
            "singleline": False,
            "frmttriminc": False,
            "frmtrmblln": False,
            "Local Whisper": False,
            "Whisper Server API Key": "None",
            "Whisper Model": "small.en",
            "Real Time": False,
            "Real Time Audio Length": 5,
            "Real Time Silence Length": 1,
            "Silence cut-off": 0.01
        }

        self.editable_settings_entries = {}

    def load_settings_from_file(self):
        """
        Loads settings from a JSON file.

        The settings are read from 'settings.txt'. If the file does not exist or cannot be parsed,
        default settings will be used. The method updates the instance attributes with loaded values.

        Returns:
            tuple: A tuple containing the IPs, ports, SSL settings, and API key.
        """
        try:
            with open('settings.txt', 'r') as file:
                try:
                    settings = json.load(file)
                except json.JSONDecodeError:
                    return self.KOBOLDCPP_IP, self.WHISPERAUDIO_IP, self.OPENAI_API_KEY, \
                           self.KOBOLDCPP_PORT, self.WHISPERAUDIO_PORT, self.SSL_ENABLE, \
                           self.SSL_SELFCERT, self.API_STYLE

                self.KOBOLDCPP_IP = settings.get("koboldcpp_ip", self.KOBOLDCPP_IP)
                self.KOBOLDCPP_PORT = settings.get("koboldcpp_port", self.KOBOLDCPP_PORT)
                self.WHISPERAUDIO_IP = settings.get("whisperaudio_ip", self.WHISPERAUDIO_IP)
                self.WHISPERAUDIO_PORT = settings.get("whisperaudio_port", self.WHISPERAUDIO_PORT)
                self.SSL_ENABLE = settings.get("ssl_enable", self.SSL_ENABLE)
                self.SSL_SELFCERT = settings.get("ssl_selfcert", self.SSL_SELFCERT)
                self.OPENAI_API_KEY = settings.get("openai_api_key", self.OPENAI_API_KEY)
                self.API_STYLE = settings.get("api_style", self.API_STYLE)
                loaded_editable_settings = settings.get("editable_settings", {})
                for key, value in loaded_editable_settings.items():
                    if key in self.editable_settings:
                        self.editable_settings[key] = value
                return self.KOBOLDCPP_IP, self.WHISPERAUDIO_IP, self.OPENAI_API_KEY, \
                       self.KOBOLDCPP_PORT, self.WHISPERAUDIO_PORT, self.SSL_ENABLE, \
                       self.SSL_SELFCERT, self.API_STYLE
        except FileNotFoundError:
            return self.KOBOLDCPP_IP, self.WHISPERAUDIO_IP, self.OPENAI_API_KEY, \
                   self.KOBOLDCPP_PORT, self.WHISPERAUDIO_PORT, self.SSL_ENABLE, \
                   self.SSL_SELFCERT, self.API_STYLE

    def save_settings_to_file(self):
        """
        Saves the current settings to a JSON file.

        The settings are written to 'settings.txt'. This includes all application settings 
        such as IP addresses, ports, SSL settings, and editable settings.

        Returns:
            None
        """
        settings = {
            "koboldcpp_ip": self.KOBOLDCPP_IP,
            "whisperaudio_ip": self.WHISPERAUDIO_IP,
            "openai_api_key": self.OPENAI_API_KEY,
            "editable_settings": self.editable_settings,
            "koboldcpp_port": self.KOBOLDCPP_PORT,
            "whisperaudio_port": self.WHISPERAUDIO_PORT,
            "ssl_enable": str(self.SSL_ENABLE),
            "ssl_selfcert": str(self.SSL_SELFCERT),
            "api_style": self.API_STYLE
        }
        with open('settings.txt', 'w') as file:
            json.dump(settings, file)

    def save_settings(self, koboldcpp_ip, whisperaudio_ip, openai_api_key, aiscribe_text, aiscribe2_text, settings_window,
                      koboldcpp_port, whisperaudio_port, ssl_enable, ssl_selfcert, api_style):
        """
        Save the current settings, including IP addresses, API keys, and user-defined parameters.

        This method writes the AI Scribe text to separate text files and updates the internal state
        of the Settings instance.

        :param str koboldcpp_ip: The IP address for the KOBOLDCPP server.
        :param str whisperaudio_ip: The IP address for the WhisperAudio server.
        :param str openai_api_key: The OpenAI API key for authentication.
        :param str aiscribe_text: The text for the first AI Scribe.
        :param str aiscribe2_text: The text for the second AI Scribe.
        :param tk.Toplevel settings_window: The settings window instance to be destroyed after saving.
        :param str koboldcpp_port: The port for the KOBOLDCPP server.
        :param str whisperaudio_port: The port for the WhisperAudio server.
        :param int ssl_enable: Flag indicating whether SSL is enabled.
        :param int ssl_selfcert: Flag indicating whether to use a self-signed certificate.
        :param str api_style: The style of API being used.
        """
        self.KOBOLDCPP_IP = koboldcpp_ip
        self.WHISPERAUDIO_IP = whisperaudio_ip
        self.KOBOLDCPP_PORT = koboldcpp_port
        self.WHISPERAUDIO_PORT = whisperaudio_port
        self.SSL_ENABLE = ssl_enable
        self.SSL_SELFCERT = ssl_selfcert
        self.OPENAI_API_KEY = openai_api_key
        self.API_STYLE = api_style

        for setting, entry in self.editable_settings_entries.items():
            value = entry.get()
            if setting in ["max_context_length", "max_length", "rep_pen_range", "top_k"]:
                value = int(value)
            self.editable_settings[setting] = value

        self.save_settings_to_file()

        self.AISCRIBE = aiscribe_text
        self.AISCRIBE2 = aiscribe2_text

        self.KOBOLDCPP_ENDPOINT = self.build_url(self.KOBOLDCPP_IP, self.KOBOLDCPP_PORT)
        self.WHISPERAUDIO_ENDPOINT = self.build_url(self.WHISPERAUDIO_IP, str(self.WHISPERAUDIO_PORT)+"/whisperaudio")

        with open('aiscribe.txt', 'w') as f:
            f.write(self.AISCRIBE)
        with open('aiscribe2.txt', 'w') as f:
            f.write(self.AISCRIBE2)
        
        settings_window.destroy()

    def open_settings_window(self):
        """
        Open the settings window, allowing the user to modify and save application settings.

        This method creates a new window with various input fields for changing
        settings related to KOBOLDCPP, WhisperAudio, OpenAI API, and more.
        """
        settings_window = tk.Toplevel()
        settings_window.title("Settings")
        settings_window.resizable(True, True)
        settings_window.grab_set()

        main_frame = tk.Frame(settings_window)
        main_frame.pack(expand=True, fill='both')

        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill='both')

        basic_frame = ttk.Frame(notebook)
        advanced_frame = ttk.Frame(notebook)

        notebook.add(basic_frame, text="Basic Settings")
        notebook.add(advanced_frame, text="Advanced Settings")

        def add_scrollbar_to_frame(frame):
            """
            Add a vertical scrollbar to the given frame.

            :param ttk.Frame frame: The frame to which the scrollbar will be added.
            :returns: The frame containing the scrollable content.
            :rtype: ttk.Frame
            """
            canvas = tk.Canvas(frame)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            return scrollable_frame

        basic_settings_frame = add_scrollbar_to_frame(basic_frame)
        advanced_settings_frame = add_scrollbar_to_frame(advanced_frame)

        tk.Label(basic_settings_frame, text="KOBOLDCPP IP:").grid(row=0, column=0, padx=0, pady=5, sticky="w")
        koboldcpp_ip_entry = tk.Entry(basic_settings_frame, width=25)
        koboldcpp_ip_entry.insert(0, self.KOBOLDCPP_IP)
        koboldcpp_ip_entry.grid(row=0, column=1, padx=0, pady=5, sticky="w")

        tk.Label(basic_settings_frame, text="PORT:").grid(row=0, column=2, padx=0, pady=5, sticky="w")
        koboldcpp_port_entry = tk.Entry(basic_settings_frame, width=10)
        koboldcpp_port_entry.insert(0, self.KOBOLDCPP_PORT)
        koboldcpp_port_entry.grid(row=0, column=3, padx=0, pady=5, sticky="w")

        tk.Label(basic_settings_frame, text="WHISPERAUDIO IP:").grid(row=1, column=0, padx=0, pady=5, sticky="w")
        whisperaudio_ip_entry = tk.Entry(basic_settings_frame, width=25)
        whisperaudio_ip_entry.insert(0, self.WHISPERAUDIO_IP)
        whisperaudio_ip_entry.grid(row=1, column=1, padx=0, pady=5, sticky="w")

        tk.Label(basic_settings_frame, text="PORT:").grid(row=1, column=2, padx=0, pady=5, sticky="w")
        whisperaudio_port_entry = tk.Entry(basic_settings_frame, width=10)
        whisperaudio_port_entry.insert(0, self.WHISPERAUDIO_PORT)
        whisperaudio_port_entry.grid(row=1, column=3, padx=0, pady=5, sticky="w")

        tk.Label(basic_settings_frame, text="OpenAI API Key:").grid(row=5, column=0, padx=0, pady=5, sticky="w")
        openai_api_key_entry = tk.Entry(basic_settings_frame, width=25)
        openai_api_key_entry.insert(0, self.OPENAI_API_KEY)
        openai_api_key_entry.grid(row=5, column=1, padx=0, pady=5, sticky="w")

        tk.Label(basic_settings_frame, text="API Style:").grid(row=6, column=0, padx=0, pady=5, sticky="w")
        api_options = ["OpenAI"]
        dropdown = ttk.Combobox(basic_settings_frame, values=api_options, width=15, state="readonly")
        dropdown.current(api_options.index(self.API_STYLE))
        dropdown.grid(row=6, column=1, padx=0, pady=5, sticky="w")

        ssl_enable_var = tk.IntVar(value=self.SSL_ENABLE)
        tk.Label(basic_settings_frame, text="Enable SSL:").grid(row=3, column=0, padx=0, pady=5, sticky="w")
        ssl_enable_checkbox = tk.Checkbutton(basic_settings_frame, variable=ssl_enable_var)
        ssl_enable_checkbox.grid(row=3, column=1, padx=0, pady=5, sticky="w")

        ssl_selfcert_var = tk.IntVar(value=self.SSL_SELFCERT)
        tk.Label(basic_settings_frame, text="Self-Signed Cert:").grid(row=4, column=0, padx=0, pady=5, sticky="w")
        ssl_selfcert_checkbox = tk.Checkbutton(basic_settings_frame, variable=ssl_selfcert_var)
        ssl_selfcert_checkbox.grid(row=4, column=1, padx=0, pady=5, sticky="w")

        adv_row_counter = 1
        basic_row_counter = 7

        for setting, value in self.editable_settings.items():
            row_counter = None
            frame = None
            
            if setting in self.basic_settings:
                row_counter = basic_row_counter
                frame = basic_settings_frame
                basic_row_counter += 1
            elif setting in self.advanced_settings:
                row_counter = adv_row_counter
                frame = advanced_settings_frame
                adv_row_counter += 1

            tk.Label(frame, text=f"{setting}:").grid(row=row_counter, column=0, padx=0, pady=5, sticky="w")
            
            # Check if the value is a boolean
            if value in [True, False]:
                var = tk.IntVar(value=int(value))  # Convert boolean to int for checkbox
                checkbox = tk.Checkbutton(frame, variable=var)
                checkbox.grid(row=row_counter, column=1, padx=0, pady=5, sticky="w")
                self.editable_settings_entries[setting] = var
            else:
                entry = tk.Entry(frame)
                entry.insert(0, str(value))  # Ensure the value is a string
                entry.grid(row=row_counter, column=1, padx=0, pady=5, sticky="w")
                self.editable_settings_entries[setting] = entry

        # make a ai scribe edit text box
        tk.Label(advanced_settings_frame, text="Pre Prompting").grid(row=adv_row_counter, column=0, padx=0, pady=5, sticky="w")
        aiscribe_text = tk.Text(advanced_settings_frame, height=10, width=25)
        aiscribe_text.insert(tk.END, self.AISCRIBE)
        aiscribe_text.grid(row=adv_row_counter, column=1, columnspan=2, padx=0, pady=5, sticky="w")

        adv_row_counter += 1

        # make a ai scribe2 edit text box
        tk.Label(advanced_settings_frame, text="Post Prompting").grid(row=adv_row_counter, column=0, padx=0, pady=5, sticky="w")
        aiscribe2_text = tk.Text(advanced_settings_frame, height=10, width=25)
        aiscribe2_text.insert(tk.END, self.AISCRIBE2)
        aiscribe2_text.grid(row=adv_row_counter, column=1, columnspan=2, padx=0, pady=5, sticky="w")


        tk.Button(main_frame, text="Save", command=lambda: self.save_settings(
            koboldcpp_ip_entry.get(),
            whisperaudio_ip_entry.get(),
            openai_api_key_entry.get(),
            aiscribe_text.get("1.0", tk.END),
            aiscribe2_text.get("1.0", tk.END),
            settings_window,
            koboldcpp_port_entry.get(),
            whisperaudio_port_entry.get(),
            ssl_enable_var.get(),
            ssl_selfcert_var.get(),
            dropdown.get()
        ), width=10).pack(side="right", padx=2, pady=5)

        default_button = tk.Button(main_frame, text="Default", width=10, command=lambda: self.clear_settings_file(settings_window))
        default_button.pack(side="right", padx=2, pady=5)

        close_button = tk.Button(main_frame, text="Close", width=10, command=settings_window.destroy)
        close_button.pack(side="right", padx=2, pady=5)

        
    def load_aiscribe_from_file(self):
        """
        Load the AI Scribe text from a file.

        :returns: The AI Scribe text, or None if the file does not exist or is empty.
        :rtype: str or None
        """
        try:
            with open('aiscribe.txt', 'r') as f:
                return f.read()
        except FileNotFoundError:
            return None

    def load_aiscribe2_from_file(self):
        """
        Load the second AI Scribe text from a file.

        :returns: The second AI Scribe text, or None if the file does not exist or is empty.
        :rtype: str or None
        """
        try:
            with open('aiscribe2.txt', 'r') as f:
                return f.read()
        except FileNotFoundError:
            return None

    def build_url(self, ip, port):
        """
        Build a URL string based on the IP address, port, and SSL settings.

        If SSL is enabled (`SSL_ENABLE` is set to "1"), the method returns a URL
        with the `https` scheme, otherwise, it returns a URL with the `http` scheme.
        
        The method also handles the case of self-signed SSL certificates based on
        the `SSL_SELFCERT` setting.

        Parameters
        ----------
        ip : str
            The IP address of the server.
        port : str
            The port number of the server.

        Returns
        -------
        str
            A fully formed URL for either `https` or `http` depending on the SSL settings.

        Prints
        ------
        If SSL is enabled, prints a message indicating that SSL/TLS connections are enabled.
        If self-signed certificates are allowed, it prints a warning about trusting self-signed certificates.
        If SSL is disabled, prints a message indicating that unencrypted connections will be used.
        """

        if str(self.SSL_ENABLE) == "1":
            print("Encrypted SSL/TLS connections are ENABLED between client and server.")
            if str(self.SSL_SELFCERT) == "1":
                print("...Self-signed SSL certificates are ALLOWED in Settings...\n...You may disregard subsequent log Warning if you are trusting self-signed certificates from server...")
            else:
                print("...Self-signed SSL certificates are DISABLED in Settings...\n...Trusted/Verified SSL certificates must be used on server, otherwise SSL connection will fail...")
            return f"https://{ip}:{port}"
        else:
            print("UNENCRYPTED http connections are being used between Client and Whisper/Kobbold server...")
            return f"http://{ip}:{port}"

    def start(self):
        """
        Load the settings from the configuration file.

        This method initializes the application settings, including the loading
        of the default AI Scribe text and other user-defined parameters.
        """
        self.load_settings_from_file()
        self.AISCRIBE = self.load_aiscribe_from_file() or "AI, please transform the following conversation into a concise SOAP note. Do not assume any medical data, vital signs, or lab values. Base the note strictly on the information provided in the conversation. Ensure that the SOAP note is structured appropriately with Subjective, Objective, Assessment, and Plan sections. Strictly extract facts from the conversation. Here's the conversation:"
        self.AISCRIBE2 = self.load_aiscribe2_from_file() or "Remember, the Subjective section should reflect the patient's perspective and complaints as mentioned in the conversation. The Objective section should only include observable or measurable data from the conversation. The Assessment should be a summary of your understanding and potential diagnoses, considering the conversation's content. The Plan should outline the proposed management, strictly based on the dialogue provided. Do not add any information that did not occur and do not make assumptions. Strictly extract facts from the conversation."
        
        self.KOBOLDCPP_ENDPOINT = self.build_url(self.KOBOLDCPP_IP, self.KOBOLDCPP_PORT)
        self.WHISPERAUDIO_ENDPOINT = self.build_url(self.WHISPERAUDIO_IP, str(self.WHISPERAUDIO_PORT)+"/whisperaudio")

    def clear_settings_file(self, settings_window):
        try:
            open('settings.txt', 'w').close()  # This opens the files and immediately closes it, clearing its contents.
            open('aiscribe.txt', 'w').close()
            open('aiscribe2.txt', 'w').close()
            messagebox.showinfo("Settings Reset", "Settings have been reset. Please restart.")
            print("Settings file cleared.")
            settings_window.destroy()
        except Exception as e:
            print(f"Error clearing settings files: {e}")
