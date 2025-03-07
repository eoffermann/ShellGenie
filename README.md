# ShellGenie: An Interactive Shell Interface with LLM Integration

## Overview

ShellGenie is a Python-based interactive command-line interface that emulates a traditional shell environment while integrating with a Large Language Model (LLM). It supports standard command execution, real-time tab completion, and natural language interpretation of commands. ShellGenie now offers two modes of operation:

- **Local Mode:** Leverages quantized LLMs (via [llama-cpp-python](https://pypi.org/project/llama-cpp-python/)) to translate natural language instructions into safe, valid shell commands.
- **External Mode:** Connects to OpenAI’s API to process natural language commands using models like `gpt-3.5-turbo`.

Both modes include a confirmation prompt for executing LLM-suggested commands, and advanced configuration is handled automatically through a configuration file stored in your user’s config directory.

## Features

- **Dual LLM Integration:** Choose between locally hosted quantized models or externally hosted OpenAI models.
- **Interactive Shell Interface:** Enjoy real-time command input with tab completion and persistent command history.
- **Natural Language Command Translation:** Issue commands in plain language prefixed with `!` to have the LLM suggest a safe shell command wrapped in `<cmd>...</cmd>` tags.
- **Robust Configuration Management:** Automatically save and load your preferred settings, including mode, model repository, and retry attempts.
- **Cross-Platform Support:** Works on Windows, macOS, and Linux.
- **Enhanced Error Handling:** Improved retry mechanisms and error messages for smoother operation.

## Installation

### Prerequisites

- **Python:** Version 3.8 or higher.
- **C Compiler:** Required for building certain dependencies.
  - **Windows:** [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
  - **macOS:** Xcode Command Line Tools (install with `xcode-select --install`)
  - **Linux:** GCC or Clang

### Conda Environment Setup

This project includes an `environment.yml` file to easily set up a dedicated Conda environment. To create and activate the environment, run:

```bash
conda env create -f environment.yml
conda activate ShellGenie
```

*(Note: Replace `ShellGenie` with the actual environment name specified in your `environment.yml` if it differs.)*

### Additional Dependencies

If you prefer using `pip`, ensure the following packages are installed:

- **`prompt_toolkit`**: Provides the interactive shell interface.
- **`llama-cpp-python`**: For local LLM functionalities.
- **`huggingface_hub`**: To download quantized models from Hugging Face.

You can install them via:

```bash
pip install prompt_toolkit huggingface_hub llama-cpp-python
```

### LLM-Specific Setup

#### Local Mode (Quantized Models)

For local LLM usage, ShellGenie downloads the quantized model from Hugging Face. The default settings use:

- **Repository ID:** `TheBloke/Llama-2-7B-Chat-GGUF`
- **Model File:** `llama-2-7b-chat.Q6_K.gguf`

The model is automatically downloaded and cached when you run the shell.

#### External Mode (OpenAI API)

To use external mode, you must provide:
- **OpenAI API Key**
- **OpenAI Model Name** (e.g., `gpt-3.5-turbo`)

Example command:

```bash
python console.py -e openai --openai-api-key YOUR_API_KEY --openai-model gpt-3.5-turbo
```

*Note: The configuration is saved in a file under your home directory for subsequent runs.*

## Usage

### Running ShellGenie

1. **Local Mode (default):**

   Run the following command to start ShellGenie using a locally hosted model:

   ```bash
   python console.py
   ```

2. **External Mode (OpenAI API):**

   Start the shell in external mode by providing the required API key and model:

   ```bash
   python console.py -e openai --openai-api-key YOUR_API_KEY --openai-model gpt-3.5-turbo
   ```

3. **Query Current Configuration:**

   To display the current configuration without starting the shell:

   ```bash
   python console.py -q
   ```

### Command Examples

- **Standard Command Execution:**

  ```
  > dir
  ```

  Executes the `dir` command and displays the output.

- **Invoking the LLM:**

  ```
  > !list files in the current directory
  ```

  The LLM will generate a corresponding shell command (e.g., `dir`) wrapped in `<cmd>...</cmd>` tags. You can review and edit the command before execution.

- **Exiting the Interface:**

  Simply type:

  ```
  > exit
  ```

## Project Structure

```
.
├── console.py           # Entry point script for launching ShellGenie
├── ShellGenie/          # Module containing core functionality and submodules
│   ├── __init__.py      # Core module and configuration management
│   └── openai_api.py    # OpenAI API integration for external mode
├── environment.yml      # Conda environment file for dependency management
└── LICENSE              # MIT License
```

## Future Enhancements

- **Broader LLM Support:** Integration with additional hosted LLM services beyond OpenAI.
- **Advanced Shell Features:** Enhanced support for piping (`|`), redirection (`>`), and custom command aliases.
- **Dynamic Tab Completion:** More context-aware command suggestions based on your shell environment.
- **Improved Logging and Error Handling:** Deeper integration of logging frameworks and more robust error management.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.
