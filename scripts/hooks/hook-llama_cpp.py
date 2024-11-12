# How to use this file
#
# 1. create a folder called "hooks" in your repo
# 2. copy this file there
# 3. add the --additional-hooks-dir flag to your pyinstaller command:
#    ex: `pyinstaller --name binary-name --additional-hooks-dir=./hooks entry-point.py`


from PyInstaller.utils.hooks import collect_data_files, get_package_paths
import os, sys

# Get the package path
package_path = get_package_paths('llama_cpp')[0]

# Collect data files
datas = collect_data_files('llama_cpp')

# Append the additional .dll or .so file
dll_path = os.path.join(package_path, 'llama_cpp', 'lib', 'llama.dll')
datas.append((dll_path, 'llama_cpp'))
