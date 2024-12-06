
from ctypes import WinDLL

# function to check if another instance of the application is already running
def window_has_running_instance(app_name: str) -> bool:
    """
    Check if another instance of the application is already running.
    Parameters:
        app_name (str): The name of the application
    Returns:
        bool: True if another instance is running, False otherwise
    """
    U32DLL = WinDLL('user32')
    # get the handle of any window matching 'app_name'
    hwnd = U32DLL.FindWindowW(None, app_name)
    print("Running instance check")
    if hwnd:  # if a matching window exists...
        print('Another instance of the application is already running.')
        # focus the existing window
        U32DLL.ShowWindow(hwnd, 5)
        U32DLL.SetForegroundWindow(hwnd)
        # bail
        return True
    return False
