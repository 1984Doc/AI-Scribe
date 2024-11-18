#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Build pkg installer for macOS using the pkgbuild command
pkgbuild --root ./dist/freescribe-client --identifier com.clinicianfocus.freescribe --version 1.0 --install-location /Applications ./dist/installer.pkg

echo "Build complete. Installer created: dist/installer.pkg"

# Build the final installer package using the productbuild command
productbuild --distribution ./mac/distribution.xml --package-path ./dist/ --resources ./mac/resources/ ./dist/FreeScribeInstaller.pkg

echo "Build complete. Final installer package created: dist/FreeScribeInstaller.pkg"