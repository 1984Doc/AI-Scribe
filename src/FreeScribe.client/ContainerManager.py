import docker
import asyncio
import time

class ContainerManager:
    """
    Manages Docker containers by starting and stopping them.
    """

    def __init__(self):
        self.client = docker.from_env()

    def start_container(self, container_name):
        """
        Start a Docker container by its name.
        """
        try:
            container = self.client.containers.get(container_name)
            container.start()
            print(f"Container {container_name} started successfully.")
        except docker.errors.NotFound:
            print(f"Container {container_name} not found.")
        except docker.errors.APIError as e:
            print(f"An error occurred while starting the container: {e}")

    def stop_container(self, container_name):
        """
        Stop a Docker container by its name.
        """
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            print(f"Container {container_name} stopped successfully.")
        except docker.errors.NotFound:
            print(f"Container {container_name} not found.")
        except docker.errors.APIError as e:
            print(f"An error occurred while stopping the container: {e}")

    def check_container_status(self, container_name):
        """
        Check the status of a Docker container by its name.
        """
        try:
            container = self.client.containers.get(container_name)
            status = container.status

            if status == 'running':
                return True
            else:
                return False

            print(f"Container {container_name} is {status}.")
        except docker.errors.NotFound:
            print(f"Container {container_name} not found.")
            return False
        except docker.errors.APIError as e:
            print(f"An error occurred while checking the container status: {e}")
            return False

    def set_status_icon_color(self, widget, status):
        """
        Set the color of the status icon based on the status of the container.
        """
        
        if status:
            widget.config(fg='green')
        else:
            widget.config(fg='red')

    def check_docker_status_thread(self, llm_dot, whisper_dot, app_settings):
        while True:
            print("Checking Docker container status...")
            # Check the status of the containers and set the color of the status icons.
            if self.check_container_status(app_settings.editable_settings["LLM Container Name"]) and self.check_container_status(app_settings.editable_settings["LLM Caddy Container Name"]):
                self.set_status_icon_color(llm_dot, True)

            if self.check_container_status(app_settings.editable_settings["Whisper Container Name"]) and self.check_container_status(app_settings.editable_settings["Whisper Caddy Container Name"]):
                self.set_status_icon_color(whisper_dot, True)

            llm_dot.after(10000, lambda: self.check_docker_status_thread(llm_dot, whisper_dot, app_settings))
