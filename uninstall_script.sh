#!/bin/bash

read -p "Enter the command name you used to install the script (default: dt): " CLI_NAME
CLI_NAME=${CLI_NAME:-dt}

INSTALL_DIR="$HOME/.local/bin"
SCRIPT_PATH="$INSTALL_DIR/${CLI_NAME}_script.py"
CLI_PATH="$INSTALL_DIR/$CLI_NAME"

rm -f "$CLI_PATH" "$SCRIPT_PATH"

if [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
    sed -i '/export PATH="$INSTALL_DIR:$PATH"/d' "$HOME/.bashrc"
    echo "Removed $INSTALL_DIR from PATH in .bashrc"
fi
source "$HOME/.bashrc"
echo "Uninstallation complete. The '$CLI_NAME' command has been removed."