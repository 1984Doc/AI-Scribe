#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Define the name of the executable and the main Python script
EXECUTABLE_NAME="freescribe-client"
MAIN_SCRIPT="src/FreeScribe.client/client.py"
ICON_PATH="src/FreeScribe.client/assets/logo.ico"

# Run PyInstaller to create the standalone executable
pyinstaller --additional-hooks-dir=./scripts/hooks --add-data "./src/FreeScribe.client/whisper-assets:whisper/assets" --add-data "./src/FreeScribe.client/markdown:markdown" --add-data "./src/FreeScribe.client/assets:assets" --name "$EXECUTABLE_NAME" --icon="$ICON_PATH" --noconsole "$MAIN_SCRIPT"

# Print a message indicating that the build is complete
echo "Build complete. Executable created: dist/$EXECUTABLE_NAME"