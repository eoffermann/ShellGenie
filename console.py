"""
Python Shell Interface with LLM Integration

This module implements an interactive shell interface in Python that supports both standard shell commands
and natural language commands interpreted by an integrated Large Language Model (LLM). The LLM generates
safe and valid shell commands based on user input. The interface features tab completion, command history,
and a confirmation prompt before executing LLM-suggested commands.

Usage:
    Run the script via:
        python shell_interface.py

Dependencies:
    - prompt_toolkit
    - llama-cpp-python
    - huggingface_hub
"""

import os
import subprocess
from typing import Any, Dict, List
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from llama_cpp import Llama
from huggingface_hub import hf_hub_download


def detect_shell() -> str:
    """
    Detects the current shell environment based on environment variables.

    Returns:
        str: The detected shell type ('bash', 'powershell', 'cmd') or 'unknown' if not identified.
    """
    # Check common environment variables that might hold the shell information.
    shell = os.environ.get("SHELL") or os.environ.get("ComSpec")
    if shell is None:
        return "unknown"
    # Determine shell type by checking substrings.
    if "bash" in shell:
        return "bash"
    elif "powershell" in shell.lower():
        return "powershell"
    elif "cmd" in shell.lower():
        return "cmd"
    else:
        return "unknown"


def configure_llm(repo_id: str = "TheBloke/LLaMA-2-7B-chat-GGUF",
                  filename: str = "llama-2-7b-chat.ggmlv3.q6_K.bin") -> Llama:
    """
    Downloads and configures a specific quantized model from Hugging Face and instantiates the Llama model.

    Args:
        repo_id (str): The repository ID on Hugging Face.
        filename (str): The specific model file to download.

    Returns:
        Llama: An instance of the Llama model configured with the downloaded model.
    """
    # Download the specified model file from Hugging Face.
    model_path: str = hf_hub_download(repo_id=repo_id, filename=filename)
    # Instantiate and return the Llama model using the downloaded model path.
    llm: Llama = Llama(model_path=model_path)
    return llm


def get_system_prompt(shell: str) -> str:
    """
    Generates a system prompt instructing the LLM to output safe and valid shell commands.

    Args:
        shell (str): The detected shell environment (e.g., 'bash', 'powershell', 'cmd').

    Returns:
        str: A system prompt string tailored for the specified shell environment.
    """
    return (
        f"You are an assistant that generates valid and safe shell commands for the '{shell}' environment. "
        "Always return a single shell command in response to the user's request. Do not provide explanations."
    )


def call_llm(llm: Llama, command: str) -> str:
    """
    Invokes the LLM to generate a shell command based on natural language input.

    Args:
        llm (Llama): The instantiated Llama model.
        command (str): The natural language command provided by the user (without the '!' prefix).

    Returns:
        str: A shell command suggested by the LLM.
    """
    # Detect the current shell environment.
    shell: str = detect_shell()
    # Get a system prompt that is appropriate for the detected shell.
    system_prompt: str = get_system_prompt(shell)

    # Prepare the conversation messages for the LLM.
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": command}
    ]

    # Generate the response from the LLM. Set max_tokens and stop conditions as needed.
    response: Dict[str, Any] = llm.create_chat_completion(messages=messages, max_tokens=50, stop=["\n"])
    # Extract and clean up the suggested command.
    suggested_command: str = response["choices"][0]["message"]["content"].strip()

    print(f"LLM suggested command for '{shell}': {suggested_command}")
    return suggested_command


def execute_command(command: str) -> None:
    """
    Executes a given shell command and prints its output.

    Args:
        command (str): The shell command to be executed.
    """
    try:
        # Execute the command with subprocess.run, capturing output and error messages.
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        # In case of an error, print the stderr output.
        print(e.stderr)


def main() -> None:
    """
    Main function that runs the interactive shell interface.
    It configures the LLM, sets up the prompt session, and handles user input and command execution.
    """
    # Configure and instantiate the LLM model.
    llm: Llama = configure_llm()

    # Create a prompt session with command history.
    session: PromptSession = PromptSession(history=FileHistory("command_history.txt"))
    # Define a set of common shell commands for tab completion.
    completer: WordCompleter = WordCompleter(
        ["dir", "cd", "cls", "copy", "move", "del", "mkdir", "rmdir", "exit"],
        ignore_case=True
    )

    print("Welcome to the Custom Command Interface! Type your commands below.")
    print("Use '!' to invoke the LLM. Type 'exit' to quit.\n")

    # Main loop to continuously accept user commands.
    while True:
        try:
            # Prompt the user for a command.
            user_input: str = session.prompt("> ", completer=completer)

            # Check if the user wants to exit.
            if user_input.lower() == "exit":
                print("Goodbye!")
                break

            # If the input starts with '!', use the LLM to interpret the command.
            if user_input.startswith("!"):
                # Remove the '!' prefix and strip whitespace.
                llm_command: str = call_llm(llm, user_input[1:].strip())
                # Ask the user to confirm the LLM-suggested command.
                confirmation: str = session.prompt(
                    f"LLM suggested command: {llm_command}\nDo you want to execute this command? (yes/no): "
                ).strip().lower()

                if confirmation in {"yes", "y"}:
                    execute_command(llm_command)
                else:
                    print("Command execution skipped.")
            else:
                # For normal commands, execute directly.
                execute_command(user_input)

        except KeyboardInterrupt:
            # Handle Ctrl+C interruption gracefully.
            print("\nOperation canceled.")
        except EOFError:
            # Handle end-of-file (e.g., Ctrl+D) gracefully.
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()
