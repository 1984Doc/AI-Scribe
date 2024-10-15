import json
import tkinter as tk
from tkinter import ttk, messagebox

class ApplicationSettings:
    def __init__(self):
        # Default settings and variables
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
            "sampler_order": [6, 0, 1, 3, 4, 2, 5],
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

        with open('aiscribe.txt', 'w') as f:
            f.write(self.AISCRIBE)
        with open('aiscribe2.txt', 'w') as f:
            f.write(self.AISCRIBE2)
        
        settings_window.destroy()

    def open_settings_window(self):
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
        koboldcpp_ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(basic_settings_frame, text="PORT:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        koboldcpp_port_entry = tk.Entry(basic_settings_frame, width=10)
        koboldcpp_port_entry.insert(0, self.KOBOLDCPP_PORT)
        koboldcpp_port_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        tk.Label(basic_settings_frame, text="WHISPERAUDIO IP:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        whisperaudio_ip_entry = tk.Entry(basic_settings_frame, width=25)
        whisperaudio_ip_entry.insert(0, self.WHISPERAUDIO_IP)
        whisperaudio_ip_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(basic_settings_frame, text="PORT:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        whisperaudio_port_entry = tk.Entry(basic_settings_frame, width=10)
        whisperaudio_port_entry.insert(0, self.WHISPERAUDIO_PORT)
        whisperaudio_port_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        tk.Label(basic_settings_frame, text="OpenAI API Key:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        openai_api_key_entry = tk.Entry(basic_settings_frame, width=25)
        openai_api_key_entry.insert(0, self.OPENAI_API_KEY)
        openai_api_key_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        tk.Label(basic_settings_frame, text="API Style:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        api_options = ["OpenAI"]
        dropdown = ttk.Combobox(basic_settings_frame, values=api_options, width=15, state="readonly")
        dropdown.current(api_options.index(self.API_STYLE))
        dropdown.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        ssl_enable_var = tk.IntVar(value=self.SSL_ENABLE)
        tk.Label(basic_settings_frame, text="Enable SSL:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        ssl_enable_checkbox = tk.Checkbutton(basic_settings_frame, variable=ssl_enable_var)
        ssl_enable_checkbox.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        ssl_selfcert_var = tk.IntVar(value=self.SSL_SELFCERT)
        tk.Label(basic_settings_frame, text="Self-Signed Cert:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        ssl_selfcert_checkbox = tk.Checkbutton(basic_settings_frame, variable=ssl_selfcert_var)
        ssl_selfcert_checkbox.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        tk.Label(basic_settings_frame, text="AI Scribe:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        aiscribe_textbox = tk.Text(basic_settings_frame, height=4, width=30)
        aiscribe_textbox.insert(1.0, self.AISCRIBE)
        aiscribe_textbox.grid(row=7, column=1, padx=5, pady=5, sticky="w")

        tk.Label(basic_settings_frame, text="AI Scribe2:").grid(row=8, column=0, padx=5, pady=5, sticky="w")
        aiscribe2_textbox = tk.Text(basic_settings_frame, height=4, width=30)
        aiscribe2_textbox.insert(1.0, self.AISCRIBE2)
        aiscribe2_textbox.grid(row=8, column=1, padx=5, pady=5, sticky="w")

        tk.Label(advanced_settings_frame, text="Editable Settings", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        row_counter = 1
        for setting, value in self.editable_settings.items():
            tk.Label(advanced_settings_frame, text=f"{setting}:").grid(row=row_counter, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(advanced_settings_frame)
            entry.insert(0, value)
            entry.grid(row=row_counter, column=1, padx=5, pady=5, sticky="w")
            self.editable_settings_entries[setting] = entry
            row_counter += 1

        tk.Button(settings_window, text="Save", command=lambda: self.save_settings(
            koboldcpp_ip_entry.get(),
            whisperaudio_ip_entry.get(),
            openai_api_key_entry.get(),
            aiscribe_textbox.get("1.0", "end").strip(),
            aiscribe2_textbox.get("1.0", "end").strip(),
            settings_window,
            koboldcpp_port_entry.get(),
            whisperaudio_port_entry.get(),
            ssl_enable_var.get(),
            ssl_selfcert_var.get(),
            dropdown.get()
        )).pack(pady=10)

        settings_window.protocol("WM_DELETE_WINDOW", settings_window.destroy)

    def start(self):
        self.load_settings_from_file()
