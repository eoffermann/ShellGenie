# Python Shell Interface with LLM Integration

## Overview
This project is a Python-based interactive command-line interface that mimics a command shell environment, supporting **command execution**, **tab completion**, and a special feature to interact with a **Large Language Model (LLM)**. Users can execute standard shell commands or invoke the LLM for advanced assistance by prefixing commands with `!`.

### Features
- **Interactive Shell Interface**: Supports real-time command input with tab completion.
- **Command Execution**: Executes standard shell commands (`dir`, `cd`, etc.) and displays output.
- **LLM Integration**: Allows users to enter natural language commands prefixed with `!`. These commands are passed to a function `call_llm` for processing.
- **Confirmation Prompt**: Commands suggested by the LLM require user confirmation before execution.
- **Cross-Platform Support**: Works on Windows, macOS, and Linux.

---

## Installation
### Prerequisites
- Python 3.8 or higher
- `prompt_toolkit` library

### Install Dependencies
```bash
pip install prompt_toolkit
```

---

## Usage
### Running the Shell Interface
```bash
python shell_interface.py
```

### Command Examples
- **Normal Command Execution:**
    ```
    > dir
    ```
    This will execute the `dir` command and display the output.

- **Invoking the LLM (`!` prefix):**
    ```
    > !list files in the current directory
    ```
    The `call_llm` function processes the command and suggests a shell command (`dir` in this case).
    ```
    LLM suggested command: dir
    Do you want to execute this command? (yes/no): yes
    ```

### Exiting the Interface
To exit the shell, use:
```
> exit
```

---

## Project Structure
```
.
├── shell_interface.py  # Main Python script for the shell interface
└── command_history.txt # Command history file (automatically generated)
```

---

## Future Enhancements
- **Full LLM Integration**: Connect to a live LLM service (e.g., OpenAI, local LLM model).
- **Advanced Shell Features**: Support for piping (`|`), redirection (`>`), and custom aliases.
- **Customizable Tab Completion**: Dynamic command suggestions based on shell environment and user-defined commands.
- **Cross-Shell Emulation**: Simulate `bash`, `PowerShell`, or `cmd` environments.

---

## Contributing
Contributions are welcome! If you would like to contribute:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description.

---

## License
This project is licensed under the **MIT License**. See `LICENSE` for more details.

---

## Contact
For questions or suggestions, feel free to reach out:

- **Author**: [Your Name]
- **Email**: your.email@example.com
- **GitHub**: [Your GitHub Profile](https://github.com/yourusername)

---

Let me know if you want to customize this further, like adding screenshots, GIFs, or usage examples!
