# Shell Interface with LLM Integration

## Overview

This project provides a Python-based interactive command-line interface that emulates a traditional shell environment. It supports standard command execution, tab completion, and integrates with a Large Language Model (LLM) to interpret natural language commands. Users can execute typical shell commands or invoke the LLM for advanced assistance by prefixing commands with `!`.

## Features

- **Interactive Shell Interface**: Real-time command input with tab completion.
- **Command Execution**: Run standard shell commands (`dir`, `cd`, etc.) and display their output.
- **LLM Integration**: Interpret natural language commands prefixed with `!` and convert them into executable shell commands.
- **Confirmation Prompt**: Prompt users for confirmation before executing commands suggested by the LLM.
- **Cross-Platform Support**: Compatible with Windows, macOS, and Linux environments.

## Installation

### Prerequisites

- **Python**: Version 3.8 or higher.
- **C Compiler**: Required for building certain dependencies.
  - **Windows**: [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
  - **macOS**: Xcode Command Line Tools
  - **Linux**: GCC or Clang

### Dependencies

- **`prompt_toolkit`**: For the interactive shell interface.
- **`llama-cpp-python`**: Python bindings for the `llama.cpp` library, enabling LLM functionalities.
- **`huggingface_hub`**: Interface to download models from Hugging Face.

### Installation Steps

1. **Install `prompt_toolkit` and `huggingface_hub`:**

   ```bash
   pip install prompt_toolkit huggingface_hub
   ```

2. **Install `llama-cpp-python`:**

   The installation of `llama-cpp-python` may require additional configuration based on your operating system and hardware. Below are the general steps:

   - **macOS with Metal (MPS) Support:**

     Ensure you have Xcode installed:

     ```bash
     xcode-select --install
     ```

     Then, install `llama-cpp-python` with Metal support:

     ```bash
     CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python
     ```

   - **Windows:**

     Install the necessary build tools:

     1. Download and install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
     2. During installation, select "Desktop development with C++".

     Then, install `llama-cpp-python`:

     ```bash
     pip install llama-cpp-python
     ```

   - **Linux:**

     Install the necessary build tools:

     ```bash
     sudo apt-get update
     sudo apt-get install build-essential
     ```

     Then, install `llama-cpp-python`:

     ```bash
     pip install llama-cpp-python
     ```

   For detailed installation instructions and troubleshooting, refer to the [llama-cpp-python documentation](https://pypi.org/project/llama-cpp-python/).

3. **Download a Quantized Model:**

   To utilize the LLM functionalities, download a quantized model (e.g., 6-bit) from Hugging Face:

   ```python
   from huggingface_hub import hf_hub_download

   model_path = hf_hub_download(
       repo_id="TheBloke/LLaMA-2-7B-chat-GGML",
       filename="model.q6_K.bin"
   )
   ```

   This script downloads the specified model file and returns the local path where it's saved.

## Usage

1. **Running the Shell Interface:**

   Save the provided Python script (e.g., `shell_interface.py`) and execute it:

   ```bash
   python shell_interface.py
   ```

2. **Command Examples:**

   - **Standard Command Execution:**

     ```
     > dir
     ```

     Executes the `dir` command and displays the output.

   - **Invoking the LLM:**

     ```
     > !list files in the current directory
     ```

     The LLM interprets the natural language command and suggests an equivalent shell command:

     ```
     LLM suggested command: dir
     Do you want to execute this command? (yes/no): yes
     ```

     Upon confirmation, the suggested command is executed.

3. **Exiting the Interface:**

   To exit, type:

   ```
   > exit
   ```

## Project Structure

```
.
├── shell_interface.py  # Main Python script for the shell interface
└── command_history.txt # Command history file (automatically generated)
```

## Future Enhancements

- **Enhanced LLM Integration**: Connect to live LLM services for more dynamic command generation.
- **Advanced Shell Features**: Support for piping (`|`), redirection (`>`), and custom aliases.
- **Dynamic Tab Completion**: Offer command suggestions based on the current shell environment and user-defined commands.
- **Extended Shell Support**: Emulate environments like `bash`, `PowerShell`, or `cmd` more closely.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

## Contact

For questions or suggestions, feel free to reach out:

- **Author**: [Your Name]
- **Email**: your.email@example.com
- **GitHub**: [Your GitHub Profile](https://github.com/yourusername)
