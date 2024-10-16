import docker

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
