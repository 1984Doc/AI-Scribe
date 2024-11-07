import os
import sys

def get_file_path(*file_names):
  """
  Get the full path to a file in the application directory.

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