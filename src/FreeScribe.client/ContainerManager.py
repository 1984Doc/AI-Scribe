"""
This software is released under the AGPL-3.0 license
Copyright (c) 2023-2024 Braedon Hendy

Further updates and packaging added in 2024 through the ClinicianFOCUS initiative, 
a collaboration with Dr. Braedon Hendy and Conestoga College Institute of Applied 
Learning and Technology as part of the CNERG+ applied research project, 
Unburdening Primary Healthcare: An Open-Source AI Clinician Partner Platform". 
Prof. Michael Yingbull (PI), Dr. Braedon Hendy (Partner), 
and Research Students - Software Developer Alex Simko, Pemba Sherpa (F24), and Naitik Patel.
"""

import docker
import asyncio
import time

class ContainerManager:
    """
    Manages Docker containers by starting and stopping them.

    This class provides methods to interact with Docker containers,
    including starting, stopping, and checking their status.

    Attributes:
        client (docker.DockerClient): The Docker client used to interact with containers.
    """

    def __init__(self):
        """
        Initialize the ContainerManager with a Docker client.
        """
        self.client = None

        try:
            self.client = docker.from_env()
        except docker.errors.DockerException as e:
            client = None

    def start_container(self, container_name):
        """
        Start a Docker container by its name.

        :param container_name: The name of the container to start.
        :type container_name: str
        :raises docker.errors.NotFound: If the specified container is not found.
        :raises docker.errors.APIError: If an error occurs while starting the container.
        """
        try:
            container = self.client.containers.get(container_name)
            container.start()
            return True
        except docker.errors.NotFound as e:
            raise docker.errors.NotFound(f"Container {container_name} not found.") from e
        except docker.errors.APIError as e:
            raise docker.errors.APIError(f"An error occurred while starting the container: {e}") from e

    def stop_container(self, container_name):
        """
        Stop a Docker container by its name.

        :param container_name: The name of the container to stop.
        :type container_name: str
        :raises docker.errors.NotFound: If the specified container is not found.
        :raises docker.errors.APIError: If an error occurs while stopping the container.
        """
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            print(f"Container {container_name} stopped successfully.")
            return True
        except docker.errors.NotFound as e:
            raise docker.errors.NotFound(f"Container {container_name} not found.") from e
        except docker.errors.APIError as e:
            raise docker.errors.APIError(f"An error occurred while stopping the container: {e}") from e

    def check_container_status(self, container_name):
        """
        Check the status of a Docker container by its name.

        :param container_name: The name of the container to check.
        :type container_name: str
        :return: True if the container is running, False otherwise.
        :rtype: bool
        :raises docker.errors.NotFound: If the specified container is not found.
        :raises docker.errors.APIError: If an error occurs while checking the container status.
        """
        try:
            container = self.client.containers.get(container_name)
            status = container.status

            return status == "running"

        except docker.errors.NotFound:
            print(f"Container {container_name} not found.")
            return False
        except docker.errors.APIError as e:
            print(f"An error occurred while checking the container status: {e}")
            return False

    def set_status_icon_color(self, widget, status):
        """
        Set the color of the status icon based on the status of the container.

        :param widget: The widget representing the status icon.
        :type widget: tkinter.Widget
        :param status: The status of the container (True for running, False otherwise).
        :type status: bool
        """
        if status:
            widget.config(fg='green')
        else:
            widget.config(fg='red')

    def check_docker_status_thread(self, llm_dot, whisper_dot, app_settings):
        """
        Continuously check the status of Docker containers and update status icons.

        This method runs in a separate thread and periodically checks the status
        of specified containers, updating the corresponding status icons.

        :param llm_dot: The widget representing the LLM container status icon.
        :type llm_dot: tkinter.Widget
        :param whisper_dot: The widget representing the Whisper container status icon.
        :type whisper_dot: tkinter.Widget
        :param app_settings: An object containing application settings.
        :type app_settings: AppSettings
        """
        while True:
            print("Checking Docker container status...")
            # Check the status of the containers and set the color of the status icons.
            if self.check_container_status(app_settings.editable_settings["LLM Container Name"]) and self.check_container_status(app_settings.editable_settings["LLM Caddy Container Name"]):
                self.set_status_icon_color(llm_dot, True)

            if self.check_container_status(app_settings.editable_settings["Whisper Container Name"]) and self.check_container_status(app_settings.editable_settings["Whisper Caddy Container Name"]):
                self.set_status_icon_color(whisper_dot, True)

            llm_dot.after(10000, lambda: self.check_docker_status_thread(llm_dot, whisper_dot, app_settings))