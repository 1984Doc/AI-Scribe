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
WhisperAudio, and OpenAI services.

"""

import json
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import numpy as np
import pyaudio


p = pyaudio.PyAudio()

class SettingsWindow():
    """
    Manages application settings related to audio processing and external API services.

    Attributes
    ----------
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
    save_settings(openai_api_key, aiscribe_text, aiscribe2_text, 
                  settings_window, ssl_enable, ssl_selfcert, api_style, preset):
        Saves the current settings, including API keys, IP addresses, and user-defined parameters.
    load_aiscribe_from_file():
        Loads the first AI Scribe text from a file.
    load_aiscribe2_from_file():
        Loads the second AI Scribe text from a file.
    build_url(ip, port):
        Constructs a URL based on IP, port, and SSL settings.
    clear_settings_file(settings_window):
        Clears the content of settings files and closes the settings window.
    """

    def __init__(self):
        """Initializes the ApplicationSettings with default values."""

        self.SSL_ENABLE = "0"
        self.SSL_SELFCERT = "1"
        self.OPENAI_API_KEY = "None"
        self.API_STYLE = "OpenAI"
        self.main_window = None
        self.scribe_template_values = []
        self.scribe_template_mapping = {}

        
        self.general_settings = {
            "Show Welcome Message"            
        }

        self.whisper_settings = {
            "Local Whisper",
            "Whisper Server API Key",
            "Whisper Model",
            "Real Time",
            "Whisper Endpoint",
        }
        self.llm_settings = {
            "Model Endpoint",
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
            "best_of",
            "Use best_of",
            "Real Time Audio Length",
            "Enable Scribe Template",
            "Use Pre-Processing",
            "Use Post-Processing",
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
            "best_of": 2,
            "Use best_of": False,
            "Local Whisper": False,
            "Whisper Endpoint": "https://localhost:2224/whisperaudio",
            "Whisper Server API Key": "None",
            "Whisper Model": "small.en",
            "Real Time": False,
            "Real Time Audio Length": 5,
            "Real Time Silence Length": 1,
            "Silence cut-off": 0.015,
            "LLM Container Name": "llm-container-1",
            "LLM Caddy Container Name": "caddy-llm-container",
            "Whisper Container Name": "speech-container",
            "Whisper Caddy Container Name": "caddy",
            "Auto Shutdown Containers on Exit": True,
            "Use Docker Status Bar": False,
            "Preset": "Custom",
            "Show Welcome Message": True,
            "Enable Scribe Template": False,
            "Use Pre-Processing": True,
            "Use Post-Processing": True,
            "Pre-Processing": "Please break down the conversation into a list of facts. Take the conversation and transform it to a easy to read list:",
            "Post-Processing": "Please check your work from the list of facts and ensure the SOAP note is accurate based on the information. Please ensure the data is accurate in regards to the list of facts.",
        }

        self.docker_settings = {
            "LLM Container Name",
            "LLM Caddy Container Name",
            "Whisper Container Name",
            "Whisper Caddy Container Name",
            "Auto Shutdown Containers on Exit",
            "Use Docker Status Bar",
        }

        self.editable_settings_entries = {}

        self.load_settings_from_file()
        self.AISCRIBE = self.load_aiscribe_from_file() or "AI, please transform the following conversation into a concise SOAP note. Do not assume any medical data, vital signs, or lab values. Base the note strictly on the information provided in the conversation. Ensure that the SOAP note is structured appropriately with Subjective, Objective, Assessment, and Plan sections. Strictly extract facts from the conversation. Here's the conversation:"
        self.AISCRIBE2 = self.load_aiscribe2_from_file() or "Remember, the Subjective section should reflect the patient's perspective and complaints as mentioned in the conversation. The Objective section should only include observable or measurable data from the conversation. The Assessment should be a summary of your understanding and potential diagnoses, considering the conversation's content. The Plan should outline the proposed management, strictly based on the dialogue provided. Do not add any information that did not occur and do not make assumptions. Strictly extract facts from the conversation."

        self.get_dropdown_values_and_mapping()

    def get_dropdown_values_and_mapping(self):
        """
        Reads the 'options.txt' file to populate dropdown values and their mappings.

        This function attempts to read a file named 'options.txt' to extract templates
        that consist of three lines: a title, aiscribe, and aiscribe2. These templates
        are then used to populate the dropdown values and their corresponding mappings.
        If the file is not found, default values are used instead.

        :raises FileNotFoundError: If 'options.txt' is not found, a message is printed
                                and default values are used.
        """
        self.scribe_template_values = []
        self.scribe_template_mapping = {}
        try:
            with open('options.txt', 'r') as file:
                content = file.read().strip()
            templates = content.split('\n\n')
            for template in templates:
                lines = template.split('\n')
                if len(lines) == 3:
                    title, aiscribe, aiscribe2 = lines
                    self.scribe_template_values.append(title)
                    self.scribe_template_mapping[title] = (aiscribe, aiscribe2)
        except FileNotFoundError:
            print("options.txt not found, using default values.")
            # Fallback default options if file not found
            self.scribe_template_values = ["Settings Template"]
            self.scribe_template_mapping["Settings Template"] = (self.AISCRIBE, self.AISCRIBE2)

    def load_settings_from_file(self, filename='settings.txt'):
        """
        Loads settings from a JSON file.

        The settings are read from 'settings.txt'. If the file does not exist or cannot be parsed,
        default settings will be used. The method updates the instance attributes with loaded values.

        Returns:
            tuple: A tuple containing the IPs, ports, SSL settings, and API key.
        """
        try:
            with open(filename, 'r') as file:
                try:
                    settings = json.load(file)
                except json.JSONDecodeError:
                    print("Error loading settings file. Using default settings.")
                    return self.OPENAI_API_KEY, self.SSL_ENABLE, self.SSL_SELFCERT, self.API_STYLE

                self.SSL_ENABLE = settings.get("ssl_enable", self.SSL_ENABLE)
                self.SSL_SELFCERT = settings.get("ssl_selfcert", self.SSL_SELFCERT)
                self.OPENAI_API_KEY = settings.get("openai_api_key", self.OPENAI_API_KEY)
                self.API_STYLE = settings.get("api_style", self.API_STYLE)
                loaded_editable_settings = settings.get("editable_settings", {})
                for key, value in loaded_editable_settings.items():
                    if key in self.editable_settings:
                        self.editable_settings[key] = value

                if self.editable_settings["Use Docker Status Bar"] and self.main_window is not None:
                    self.main_window.create_docker_status_bar()
                
                if self.editable_settings["Enable Scribe Template"] and self.main_window is not None:
                    self.main_window.create_scribe_template()


                return self.OPENAI_API_KEY, self.SSL_ENABLE, self.SSL_SELFCERT, self.API_STYLE
        except FileNotFoundError:
            print("Settings file not found. Using default settings.")
            return self.OPENAI_API_KEY, self.SSL_ENABLE, self.SSL_SELFCERT, self.API_STYLE

    def save_settings_to_file(self):
        """
        Saves the current settings to a JSON file.

        The settings are written to 'settings.txt'. This includes all application settings 
        such as IP addresses, ports, SSL settings, and editable settings.

        Returns:
            None
        """
        settings = {
            "openai_api_key": self.OPENAI_API_KEY,
            "editable_settings": self.editable_settings,
            "ssl_enable": str(self.SSL_ENABLE),
            "ssl_selfcert": str(self.SSL_SELFCERT),
            "api_style": self.API_STYLE
        }
        with open('settings.txt', 'w') as file:
            json.dump(settings, file)

    def save_settings(self, openai_api_key, aiscribe_text, aiscribe2_text, settings_window,
                      ssl_enable, ssl_selfcert, api_style, silence_cutoff):
        """
        Save the current settings, including IP addresses, API keys, and user-defined parameters.

        This method writes the AI Scribe text to separate text files and updates the internal state
        of the Settings instance.

        :param str openai_api_key: The OpenAI API key for authentication.
        :param str aiscribe_text: The text for the first AI Scribe.
        :param str aiscribe2_text: The text for the second AI Scribe.
        :param tk.Toplevel settings_window: The settings window instance to be destroyed after saving.
        :param int ssl_enable: Flag indicating whether SSL is enabled.
        :param int ssl_selfcert: Flag indicating whether to use a self-signed certificate.
        :param str api_style: The style of API being used.
        """
        self.SSL_ENABLE = ssl_enable
        self.SSL_SELFCERT = ssl_selfcert
        self.OPENAI_API_KEY = openai_api_key
        self.API_STYLE = api_style

        self.editable_settings["Silence cut-off"] = silence_cutoff

        for setting, entry in self.editable_settings_entries.items():     
            value = entry.get()
            if setting in ["max_context_length", "max_length", "rep_pen_range", "top_k"]:
                value = int(value)
            self.editable_settings[setting] = value

        self.save_settings_to_file()

        self.AISCRIBE = aiscribe_text
        self.AISCRIBE2 = aiscribe2_text

        with open('aiscribe.txt', 'w') as f:
            f.write(self.AISCRIBE)
        with open('aiscribe2.txt', 'w') as f:
            f.write(self.AISCRIBE2)
      
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
  
    def clear_settings_file(self, settings_window):
        """
        Clears the content of settings files and closes the settings window.

        This method attempts to open and clear the contents of three text files:
        `settings.txt`, `aiscribe.txt`, and `aiscribe2.txt`. After clearing the
        files, it displays a message box to notify the user that the settings
        have been reset and closes the `settings_window`. If an error occurs
        during this process, the exception will be caught and printed.

        :param settings_window: The settings window object to be closed after resetting.
        :type settings_window: tkinter.Toplevel or similar
        :raises Exception: If there is an issue with file handling or window destruction.

        Example usage:

        """
        try:
            # Open the files and immediately close them to clear their contents.
            open('settings.txt', 'w').close()  
            open('aiscribe.txt', 'w').close()
            open('aiscribe2.txt', 'w').close()

            # Display a message box informing the user of successful reset.
            messagebox.showinfo("Settings Reset", "Settings have been reset. Please restart.")
            print("Settings file cleared.")

            # Close the settings window.
            settings_window.destroy()
        except Exception as e:
            # Print any exception that occurs during file handling or window destruction.
            print(f"Error clearing settings files: {e}")

    def get_available_models(self):
        """
        Returns a list of available models for the user to choose from.

        This method returns a list of available models that can be used with the AI Scribe
        service. The list includes the default model, `gpt-4`, as well as any other models
        that may be added in the future.

        Returns:
            list: A list of available models for the user to choose from.
        """
        
        headers = {
            "Authorization": f"Bearer {self.OPENAI_API_KEY}",
            "X-API-Key": self.OPENAI_API_KEY
        }

        try:
            response = requests.get(self.editable_settings["Model Endpoint"] + "/models", headers=headers, timeout=2.0)
            response.raise_for_status()  # Raise an error for bad responses
            models = response.json().get("data", [])  # Extract the 'data' field
            available_models = [model["id"] for model in models]
            available_models.append("Custom")
            return available_models
        except requests.RequestException as e:
            # messagebox.showerror("Error", f"Failed to fetch models: {e}. Please ensure your OpenAI API key is correct.") 
            return ["Failed to load models", "Custom"]

    def update_models_dropdown(self, dropdown):
        """
        Updates the models dropdown with the available models.

        This method fetches the available models from the AI Scribe service and updates
        the dropdown widget in the settings window with the new list of models.
        """
        dropdown["values"] = []
        dropdown.set("Loading models...")
        models = self.get_available_models()
        dropdown["values"] = models
        if self.editable_settings["Model"] in models:
            dropdown.set(self.editable_settings["Model"])
        else:
            dropdown.set(models[0])
        

    def load_settings_preset(self, preset_name, settings_class):
        """
        Load a settings preset from a file.

        This method loads a settings preset from a JSON file with the given name.
        The settings are then applied to the application settings.

        Parameters:
            preset_name (str): The name of the settings preset to load.

        Returns:
            None
        """
        self.editable_settings["Preset"] = preset_name

        if preset_name != "Custom":
            # load the settigns from the json preset file
            self.load_settings_from_file("presets/" + preset_name + ".json")
            messagebox.showinfo("Settings Preset", "Settings preset loaded successfully. Closing settings window. Please re-open and set respective API keys.")
            
            self.editable_settings["Preset"] = preset_name
            settings_class.settings_window.destroy()
            self.save_settings_to_file()
        else:
            messagebox.showinfo("Custom Settings", "To use custom settings then please fill in the values and save them.")

    def set_main_window(self, window):
        """
        Set the main window instance for the settings.

        This method sets the main window instance for the settings class, allowing
        the settings to interact with the main window when necessary.

        Parameters:
            window (MainWindow): The main window instance to set.
        """
        self.main_window = window

