"""
Python Shell Interface with LLM Integration

This module implements an interactive shell interface in Python that supports both standard shell commands
and natural language commands interpreted by an integrated Large Language Model (LLM). The LLM generates
safe and valid shell commands based on user input. The interface features tab completion, command history,
and an editable default prompt before executing LLM-suggested commands.

Usage:
    Run the script via:
        python console.py [--repo REPO_ID] [--file FILENAME] [--retry RETRY_COUNT] [-q|--query]

Dependencies:
    - prompt_toolkit
    - llama-cpp-python
    - huggingface_hub
    - argparse
    - json
    - appdirs

This module:
    1. Detects and sets up the user's shell environment.
    2. Manages configuration loading and saving for model repository, filename, and retry attempts.
    3. Initializes and communicates with a Large Language Model to translate natural language prompts
       into shell commands wrapped between <cmd> and </cmd>.
    4. Allows user editing of LLM-suggested commands before execution.
    5. Executes commands in the detected shell and displays the results.
"""

import os
import subprocess
import argparse
import json
from typing import Any, Dict, List

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
from appdirs import user_config_dir

# Define application details for the configuration directory.
APP_NAME = "ShellGenie"
APP_AUTHOR = "BigBlueCeiling"

# Use appdirs to determine the standard config directory and config file path.
CONFIG_DIR = user_config_dir(APP_NAME, APP_AUTHOR)
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(CONFIG_DIR, "last_config.json")


def load_config() -> Dict[str, str]:
    """
    Load the last used configuration from CONFIG_FILE if it exists.

    Returns:
        Dict[str, str]: A dictionary containing the configuration options.
    
    Raises:
        Exception: If there is an error in reading or parsing the JSON file.
    
    Note:
        The returned dictionary always includes a 'retry' key, defaulting to 3 if not present in the file.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                # Ensure 'retry' exists in the configuration; default to 3 otherwise.
                if "retry" not in config:
                    config["retry"] = 3
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
    # Default config if file does not exist or an error occurred.
    return {"retry": 3}


def save_config(repo_id: str, filename: str, retry: int) -> None:
    """
    Save the current configuration to CONFIG_FILE.

    Args:
        repo_id (str): The repository ID on Hugging Face.
        filename (str): The specific model file to use from the repository.
        retry (int): The number of retries allowed when generating a valid command.
    
    Raises:
        Exception: If there is an issue writing to the CONFIG_FILE.
    """
    config = {"repo_id": repo_id, "filename": filename, "retry": retry}
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Error saving config: {e}")


def detect_shell() -> str:
    """
    Detect the current shell environment based on environment variables.

    Returns:
        str: The detected shell type ('bash', 'Windows powershell', 'Windows cmd shell', or 'unknown').
    """
    shell = os.environ.get("SHELL") or os.environ.get("ComSpec")
    if shell is None:
        return "unknown"
    if "bash" in shell:
        return "bash"
    elif "powershell" in shell.lower():
        return "Windows powershell"
    elif "cmd" in shell.lower():
        return "Windows cmd shell"
    else:
        return f"{shell} shell"


def get_system_prompt(shell: str) -> str:
    """
    Generate a system prompt instructing the LLM to output safe and valid shell commands.

    Args:
        shell (str): The detected shell environment (e.g., 'bash', 'powershell', 'cmd').

    Returns:
        str: A system prompt string tailored for the specified shell environment.

    The prompt ensures that the LLM returns a single command
    enclosed in <cmd> and </cmd> tags without extra text.
    """
    return (
        f"You are an assistant that generates valid and safe shell commands for the '{shell}' environment. "
        "Always return a single shell command wrapped in <cmd> and </cmd> tags in response to the user's request. "
        "Do not provide explanations, greetings, or any additional text."
    )


def configure_llm(repo_id: str = "TheBloke/Llama-2-7B-Chat-GGUF",
                  filename: str = "llama-2-7b-chat.Q6_K.gguf") -> Llama:
    """
    Download and configure a specific quantized model from Hugging Face, then instantiate a Llama model.

    Args:
        repo_id (str, optional): The repository ID on Hugging Face. Defaults to "TheBloke/Llama-2-7B-Chat-GGUF".
        filename (str, optional): The specific model file to download. Defaults to "llama-2-7b-chat.Q6_K.gguf".

    Returns:
        Llama: An instance of the Llama model configured with the downloaded model.

    Note:
        The function uses hf_hub_download to retrieve the model file from Hugging Face.
    """
    # Download model file from Hugging Face Hub.
    model_path: str = hf_hub_download(repo_id=repo_id, filename=filename)
    # Create an instance of the Llama model with the downloaded path.
    llm: Llama = Llama(model_path=model_path, verbose=False)
    return llm


def call_llm(llm: Llama, command: str, retry: int) -> str:
    """
    Invoke the LLM to generate a shell command based on a natural language input.

    This function attempts to parse the returned command from the LLM, ensuring
    that it is wrapped in <cmd>...</cmd> tags. It retries if the required format
    is not found, up to `retry` times.

    Args:
        llm (Llama): The instantiated Llama model.
        command (str): The natural language command provided by the user (minus the '!' prefix).
        retry (int): The maximum number of attempts to get a properly formatted command.

    Returns:
        str: The shell command suggested by the LLM. If no properly formatted command is returned
        after the specified retries, the raw output is returned as a fallback.

    TODO:
        Consider additional validation or sanitation of the returned command if security is a concern.
    """
    shell: str = detect_shell()
    system_prompt: str = get_system_prompt(shell)
    # Prepare message list for the LLM with a system-level instruction and user query.
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": command}
    ]

    for attempt in range(1, retry + 1):
        # Request LLM to create a chat completion.
        response: Dict[str, Any] = llm.create_chat_completion(messages=messages, max_tokens=50, stop=["\n"])
        raw_output: str = response["choices"][0]["message"]["content"].strip().strip('`')
        
        # Check if the output is enclosed within <cmd>...</cmd> tags.
        if raw_output.startswith("<cmd>") and raw_output.endswith("</cmd>"):
            start = len("<cmd>")
            end = -len("</cmd>")
            # Extract only the command within the tags.
            return raw_output[start:end].strip()
        else:
            print(f"Attempt {attempt}: Response did not contain proper command tags.")
    
    # Fallback if no valid command after all retries.
    print("Maximum retry attempts reached. Using raw output.")
    return raw_output


def execute_command(command: str) -> None:
    """
    Execute a given shell command and print its output.

    Args:
        command (str): The shell command to be executed.
    
    Raises:
        subprocess.CalledProcessError: If the command execution fails.
    
    TODO:
        - Consider handling cross-platform differences in commands more robustly.
        - Add more detailed logging or output formatting if desired.
    """
    try:
        # Run the shell command, capturing the output.
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        # Print stdout from the command.
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        # If command execution fails, print stderr to provide error info.
        print(e.stderr)


def main() -> None:
    """
    Parse command-line arguments, configure the model, and enter an interactive prompt session.

    This function:
      - Reads or defaults configuration for model repository, filename, and retry attempts.
      - Initializes and configures an LLM instance for generating shell commands from natural language queries.
      - Starts a PromptSession for interactive user input. If a command starts with "!", it is
        interpreted via the LLM for command generation.
      - Allows the user to edit the LLM-suggested command before execution.
      - Executes shell commands and displays the results.
      - Ends when the user types "exit", presses Ctrl+D (EOFError), or Ctrl+C (KeyboardInterrupt).

    Usage:
        python console.py [--repo REPO_ID] [--file FILENAME] [--retry RETRY_COUNT] [-q|--query]
    """
    parser = argparse.ArgumentParser(description="Custom AI Shell Interface")
    parser.add_argument("--repo", type=str, help="Repository ID for the model")
    parser.add_argument("--file", type=str, help="Filename for the model")
    parser.add_argument("--retry", type=int, help="Number of retry attempts for LLM command formatting", default=None)
    parser.add_argument("-q", "--query", action="store_true", help="Print repo id, filename, and retry count without starting the shell")
    args = parser.parse_args()

    # Load stored configuration if available.
    config = load_config()

    # Retrieve arguments or default to values found in config or specified defaults.
    repo_id = args.repo if args.repo is not None else config.get("repo_id", "TheBloke/LLaMA-2-7B-chat-GGUF")
    filename = args.file if args.file is not None else config.get("filename", "llama-2-7b-chat.Q6_K.gguf")
    retry_value = args.retry if args.retry is not None else config.get("retry", 3)

    # If query flag is set, print the configuration and exit immediately.
    if args.query:
        print(f"Repository ID: {repo_id}")
        print(f"Filename: {filename}")
        print(f"Retry Attempts: {retry_value}")
        return

    # Save the configuration for future runs.
    save_config(repo_id, filename, retry_value)

    # Configure and instantiate the LLM model.
    llm: Llama = configure_llm(repo_id, filename)

    # Initialize a PromptSession with a local file history for storing command lines.
    session: PromptSession = PromptSession(history=FileHistory("command_history.txt"))
    # Define a simple WordCompleter for basic tab completion of common shell commands.
    completer: WordCompleter = WordCompleter(
        ["dir", "cd", "cls", "copy", "move", "del", "mkdir", "rmdir", "exit"],
        ignore_case=True
    )

    print("Welcome to the Custom Command Interface! Type your commands below.")
    print("Use '!' to invoke the LLM. Type 'exit' to quit.\n")

    while True:
        try:
            # Prompt user for input.
            user_input: str = session.prompt("> ", completer=completer)

            # Check for exit condition.
            if user_input.lower() == "exit":
                print("Goodbye!")
                break

            # If the command starts with '!', interpret it with the LLM.
            if user_input.startswith("!"):
                # Call the LLM to generate a command.
                llm_command: str = call_llm(llm, user_input[1:].strip(), retry_value)
                # Allow user to edit the suggested command before execution.
                edited_command: str = session.prompt("> ", default=llm_command).strip()
                if edited_command:
                    execute_command(edited_command)
                else:
                    print("No command entered; skipping execution.")
            else:
                # Otherwise, execute the user-provided command as-is.
                execute_command(user_input)

        except KeyboardInterrupt:
            print("\nOperation canceled.")
            # The loop continues, allowing the user to either type a new command or exit.
        except EOFError:
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()
