
import ctypes

# function to check if another instance of the application is already running
def window_has_running_instance() -> bool:
    """
    Check if another instance of the application is already running.
    Returns:
        bool: True if another instance is running, False otherwise
    """
    # Define the mutex name
    MUTEX_NAME = 'Global\\FreeScribe_Instance'
    ERROR_ALREADY_EXISTS = 183

    # Create a named mutex
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
    already_running = ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS
    return already_running

def bring_to_front(app_name: str):
    """
    Bring the window with the given handle to the front.
    Parameters:
        app_name (str): The name of the application window to bring to the front
    """

    # TODO - Check platform and handle for different platform
    U32DLL = ctypes.WinDLL('user32')
    SW_SHOW = 5
    hwnd = U32DLL.FindWindowW(None, app_name)
    U32DLL.ShowWindow(hwnd, SW_SHOW)
    U32DLL.SetForegroundWindow(hwnd)
