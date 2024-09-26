#!/bin/bash

read -p "Enter the command name you want to use to invoke the script (default: dt): " CLI_NAME
CLI_NAME=${CLI_NAME:-dt}

INSTALL_DIR="$HOME/.local/bin"
SCRIPT_PATH="$INSTALL_DIR/${CLI_NAME}_script.py"
CLI_PATH="$INSTALL_DIR/$CLI_NAME"

GITHUB_URL="https://raw.githubusercontent.com/sahilpatel09/ducttape/refs/heads/master/main.py"

curl -sSL "$GITHUB_URL" -o "$SCRIPT_PATH"
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Failed to download main.py from $GITHUB_URL."
    exit 1
fi
mkdir -p "$INSTALL_DIR"

cat > "$CLI_PATH" << EOL
#!/bin/bash
python3 "$SCRIPT_PATH" "\$@"
EOL

chmod +x "$CLI_PATH"
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo 'export PATH="$INSTALL_DIR:$PATH"' >> "$HOME/.bashrc"
    echo "Added $INSTALL_DIR to PATH in .bashrc"
    # Also add to the current session
    export PATH="$INSTALL_DIR:$PATH"
fi

source "$HOME/.bashrc"
echo "Installation complete. The '$CLI_NAME' command is now available."
echo "You can start using it right away in this terminal session."