# Ducttape

Ducttape is a powerful CLI tool designed to streamline common operations in Linux environments. It provides a fast and intuitive interface for working with Docker, Kubernetes, Git, and various system management tasks.

## Features

- Quick access to common operations for Docker, Kubernetes & Git
- Interactive fuzzy-finding for selecting items (containers, pods, branches, etc.)
- Customizable aliases for frequently used commands
- Preview pane for additional information without executing commands

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ducttape.git
   cd ducttape
   ```

2. Run the installation script:
   ```
   chmod +x install.sh
   ./install.sh
   ```

## Requirements

- Python 3.6+
- fzf (Fuzzy Finder)
- Docker (for Docker-related commands)
- kubectl (for Kubernetes-related commands)
- Git (for Git-related commands)

Make sure these are installed on your system for full functionality.

## Usage

The basic syntax for ducttape is:

```
dt <command> [<alias>] [<args>]
```

Where:
- `<command>` is the main command category (e.g., d for Docker, k for Kubernetes)
- `<alias>` is a shortcut for a specific operation
- `<args>` are any additional arguments for the command

### Examples

1. List and interact with Docker containers:
   ```
   dt d
   ```

2. View logs of a Docker container:
   ```
   dt d logs
   ```

3. Execute a command in a Kubernetes pod:
   ```
   dt k exec
   ```

4. Checkout a Git branch:
   ```
   dt gb c
   ```

## Available Commands

- `d`: Docker operations
- `k`: Kubernetes operations
- `gb`: Git branch operations
- `p`: Process management
- `s`: System service management
- `a`: APT package management

## Customization

You can add your own commands or modify existing ones by editing the `COMMANDS` dictionary in the `main.py` file.

## License

[MIT License](LICENSE)

## Support

If you encounter any problems or have any questions, please open an issue on the GitHub repository.

---

Happy ducttaping!