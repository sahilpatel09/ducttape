#!/bin/bash

CLI_NAME="dt" # short for ducttape
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if main.py exists in the current directory
if [ ! -f "$SCRIPT_DIR/main.py" ]; then
    echo "Error: main.py not found in the current directory."
    exit 1
fi

# Create a directory in the user's home for the script if doesn't exist
mkdir -p "$HOME/.local/bin"

cp "$SCRIPT_DIR/main.py" "$HOME/.local/bin/${CLI_NAME}_script.py"

cat > "$HOME/.local/bin/$CLI_NAME" << EOL
#!/bin/bash
python3 "$HOME/.local/bin/${CLI_NAME}_script.py" "\$@"
EOL

chmod +x "$HOME/.local/bin/$CLI_NAME"

# Check if ~/.local/bin is in PATH, if not, add it
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo "Added $HOME/.local/bin to PATH in .bashrc"
    # Also add to current session
    export PATH="$HOME/.local/bin:$PATH"
fi

source "$HOME/.bashrc"

echo "Installation complete. The '$CLI_NAME'(ducttape) command is now available."
echo "You can start using it right away in this terminal session."