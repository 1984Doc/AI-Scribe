import docker
import asyncio

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

