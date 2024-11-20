#!/bin/bash

# Ensure the script exits if any command fails
set -e

DIR_NAME="dist/client"
IDENTIFIER="com.clinicianfocus.freescribe"

# Create a directory to store the built application and move the app into it
mkdir -p $DIR_NAME
mv dist/freescribe-client.app $DIR_NAME

# Build pkg installer for macOS using the pkgbuild command
pkgbuild --root $DIR_NAME --identifier $IDENTIFIER --scripts ./mac/scripts/ --version 1.0 --install-location /Applications ./dist/installer.pkg

echo "Build complete. Installer created: dist/installer.pkg"

# Build the final installer package using the productbuild command
productbuild --distribution ./mac/distribution.xml --package-path ./dist/ --resources ./mac/resources/ ./dist/FreeScribeInstaller.pkg

echo "Build complete. Final installer package created: dist/FreeScribeInstaller.pkg"