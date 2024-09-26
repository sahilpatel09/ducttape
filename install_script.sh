#!/bin/bash

read -p "Enter the command name you want to use to invoke the script (default: dt): " CLI_NAME
CLI_NAME=${CLI_NAME:-dt}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_DIR="$HOME/.local/bin"
SCRIPT_PATH="$INSTALL_DIR/${CLI_NAME}_script.py"
CLI_PATH="$INSTALL_DIR/$CLI_NAME"

if [ ! -f "$SCRIPT_DIR/main.py" ]; then
    echo "Error: main.py not found in the current directory."
    exit 1
fi

mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR/main.py" "$SCRIPT_PATH"

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