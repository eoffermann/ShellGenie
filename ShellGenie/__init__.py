#!/usr/bin/env python3
"""
Module: ShellGenie

This module implements the core functionality for an interactive shell interface with LLM integration.
It manages configuration, detects the shell environment, sets up and interacts with the LLM, and
executes shell commands. The structure is designed to facilitate future expansion for hosted LLMs
(e.g., OpenAI's GPT, Anthropic Claude, etc.).

Features include:
    - Local mode using quantized models (e.g., Llama via llama_cpp).
    - External mode using OpenAI's API (newly integrated via the openai_api submodule).

Future enhancements could include:
    - Integrating additional LLM backends.
    - More robust error handling and logging.
    - Enhanced cross-platform support.
"""

import os
import subprocess
import json
from typing import Any, Dict, List

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
from appdirs import user_config_dir

# Application details used for configuration storage.
APP_NAME = "ShellGenie"
APP_AUTHOR = "BigBlueCeiling"

# Determine the configuration directory and file path.
CONFIG_DIR = user_config_dir(APP_NAME, APP_AUTHOR)
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(CONFIG_DIR, "last_config.json")


def load_config() -> Dict[str, str]:
    """
    Load the last used configuration from CONFIG_FILE if available.

    Returns:
        Dict[str, str]: A dictionary containing configuration options such as repo_id,
        filename, and retry count. Defaults to {"retry": 3} if the file does not exist or an error occurs.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                if "retry" not in config:
                    config["retry"] = 3
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
    return {"retry": 3}


def save_config(repo_id: str, filename: str, retry: int) -> None:
    """
    Save the current configuration to CONFIG_FILE.

    Args:
        repo_id (str): The repository ID on Hugging Face.
        filename (str): The specific model file to use.
        retry (int): The number of retry attempts for generating a properly formatted command.
    """
    config = {"repo_id": repo_id, "filename": filename, "retry": retry}
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Error saving config: {e}")


def detect_shell() -> str:
    """
    Detect the current shell environment based on system environment variables.

    Returns:
        str: The detected shell type (e.g., 'bash', 'Windows powershell', 'Windows cmd shell', or 'unknown').
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
    Generate a system prompt instructing the LLM to output a valid shell command.

    Args:
        shell (str): The detected shell environment.

    Returns:
        str: A system prompt tailored for the specified shell environment that instructs the LLM
             to return a command wrapped in <cmd> and </cmd> tags.
    """
    return (
        f"You are an assistant that generates valid and safe shell commands for the '{shell}' environment. "
        "Always return a single shell command wrapped in <cmd> and </cmd> tags in response to the user's request. "
        "Do not provide explanations, greetings, or any additional text."
    )


def configure_llm(repo_id: str = "TheBloke/Llama-2-7B-Chat-GGUF",
                  filename: str = "llama-2-7b-chat.Q6_K.gguf") -> Llama:
    """
    Download and configure a specific quantized model from Hugging Face and instantiate a Llama model.

    Args:
        repo_id (str, optional): The repository ID on Hugging Face. Defaults to "TheBloke/Llama-2-7B-Chat-GGUF".
        filename (str, optional): The specific model file to download. Defaults to "llama-2-7b-chat.Q6_K.gguf".

    Returns:
        Llama: An instance of the Llama model configured with the downloaded model file.
    """
    model_path: str = hf_hub_download(repo_id=repo_id, filename=filename)
    llm: Llama = Llama(model_path=model_path, verbose=False)
    return llm


def call_llm(llm: Llama, command: str, retry: int) -> str:
    """
    Use the LLM to translate a natural language command into a shell command.

    This function will retry if the LLM's output does not correctly include the required <cmd>...</cmd> tags.

    Args:
        llm (Llama): The instantiated Llama model.
        command (str): The natural language command provided by the user (without the '!' prefix).
        retry (int): The maximum number of attempts for getting a properly formatted command.

    Returns:
        str: The shell command generated by the LLM. If no properly formatted command is returned after
             all retries, the raw output is returned as a fallback.
    """
    shell: str = detect_shell()
    system_prompt: str = get_system_prompt(shell)
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": command}
    ]

    for attempt in range(1, retry + 1):
        response: Dict[str, Any] = llm.create_chat_completion(
            messages=messages, max_tokens=50, stop=["\n"]
        )
        raw_output: str = response["choices"][0]["message"]["content"].strip().strip('`')
        if raw_output.startswith("<cmd>") and raw_output.endswith("</cmd>"):
            start = len("<cmd>")
            end = -len("</cmd>")
            return raw_output[start:end].strip()
        else:
            print(f"Attempt {attempt}: Response did not contain proper command tags.")

    print("Maximum retry attempts reached. Using raw output.")
    return raw_output


def execute_command(command: str) -> None:
    """
    Execute a given shell command and print its output.

    Args:
        command (str): The shell command to execute.
    """
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(e.stderr)


def run_shell(repo_id: str, filename: str, retry: int) -> None:
    """
    Run the interactive shell interface using the specified configuration.

    This function saves the configuration, sets up the LLM, and then enters an interactive
    loop to process user commands (either directly executed or processed via the LLM).

    Args:
        repo_id (str): The repository ID for the LLM model.
        filename (str): The filename of the LLM model.
        retry (int): The number of retry attempts for LLM command formatting.
    """
    save_config(repo_id, filename, retry)
    llm: Llama = configure_llm(repo_id, filename)
    session: PromptSession = PromptSession(history=FileHistory("command_history.txt"))
    completer: WordCompleter = WordCompleter(
        ["dir", "cd", "cls", "copy", "move", "del", "mkdir", "rmdir", "exit"],
        ignore_case=True
    )

    print("Welcome to the Custom Command Interface! Type your commands below.")
    print("Use '!' to invoke the LLM. Type 'exit' to quit.\n")

    while True:
        try:
            user_input: str = session.prompt("> ", completer=completer)
            if user_input.lower() == "exit":
                print("Goodbye!")
                break

            if user_input.startswith("!"):
                llm_command: str = call_llm(llm, user_input[1:].strip(), retry)
                edited_command: str = session.prompt("> ", default=llm_command).strip()
                if edited_command:
                    execute_command(edited_command)
                else:
                    print("No command entered; skipping execution.")
            else:
                execute_command(user_input)

        except KeyboardInterrupt:
            print("\nOperation canceled.")
        except EOFError:
            print("\nExiting.")
            break

# Import the new OpenAI integration submodule.
from .openai_api import run_openai_shell

__all__ = [
    "load_config",
    "save_config",
    "detect_shell",
    "get_system_prompt",
    "configure_llm",
    "call_llm",
    "execute_command",
    "run_shell",
    "run_openai_shell"
]
