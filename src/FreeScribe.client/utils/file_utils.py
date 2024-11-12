import ctypes
import os
import sys

def get_file_path(*file_names: str) -> str:
  """
  Get the full path to a files. Use Temporary directory at runtime for bundled apps, otherwise use the current working directory.

  :param file_names: The names of the directories and the file.
  :type file_names: str
  :return: The full path to the file.
  :rtype: str
  """
  try:
      base_path = sys._MEIPASS
      return os.path.join(base_path, *file_names)
  except AttributeError:
      return os.path.join(*file_names)
  

def get_programdata_path() -> str:
    """
    Get the path to the ProgramData directory using ctypes.
    """
    buf = ctypes.create_unicode_buffer(1024)
    ctypes.windll.shell32.SHGetFolderPathW(None, 0x23, None, 0, buf)
    return buf.value

def get_resource_path(filename: str) -> str:
    """
    Get the path to the files. Use ProgramData for bundled apps, otherwise use the current working directory.

    :param filename: The name of the file.
    :type filename: str
    :return: The full path to the file.
    :rtype: str
    """
    if hasattr(sys, '_MEIPASS'):
        # Running as a bundled executable
        programdata_path = get_programdata_path()
        return os.path.join(programdata_path, 'FreeScribe', filename)
    else:
        # Running in development mode
        return os.path.join(os.path.abspath("."), filename)
