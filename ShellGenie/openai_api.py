#!/usr/bin/env python3
"""
Module: openai_api
Submodule of ShellGenie for integrating with the OpenAI API.

This module provides functionality to interact with OpenAI's ChatCompletion API using the new
client-based interface (v1.0.0+). It includes functions to configure the API key, call the API with a prompt,
and run an interactive shell interface similar to the local mode but using OpenAI's models.

Usage:
    - Call configure_openai(api_key) to set up the API key.
    - Use call_openai() to send a prompt to OpenAI and receive a formatted shell command.
    - Run run_openai_shell() to start an interactive shell for OpenAI mode.

Reference:
    The new client-based approach replaces the deprecated openai.ChatCompletion call.
    See: https://github.com/openai/openai-python :contentReference[oaicite:0]{index=0}
"""

import os
import json
import subprocess
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory

def configure_openai(api_key: str) -> None:
    """
    Configure the OpenAI API key by setting the environment variable.

    Args:
        api_key (str): The API key for OpenAI.
    """
    os.environ["OPENAI_API_KEY"] = api_key

def get_system_prompt(shell: str) -> str:
    """
    Generate a system prompt instructing OpenAI to output a valid shell command.

    Args:
        shell (str): The shell environment (e.g., 'bash', 'Windows cmd shell').

    Returns:
        str: A system prompt string.
    """
    return (
        f"You are an assistant that generates valid and safe shell commands for the '{shell}' environment. "
        "Always return a single shell command wrapped in <cmd> and </cmd> tags in response to the user's request. "
        "Do not provide explanations, greetings, or any additional text."
    )

def detect_shell() -> str:
    """
    Detect the current shell environment.

    Returns:
        str: The detected shell type.
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

def call_openai(command: str, openai_model: str, retry: int) -> str:
    """
    Use the OpenAI API (via the new client interface) to translate a natural language command
    into a shell command.

    This function will retry if the output does not correctly include the required <cmd>...</cmd> tags.

    Args:
        command (str): The natural language command provided by the user.
        openai_model (str): The OpenAI model to use (e.g., 'gpt-3.5-turbo').
        retry (int): Number of retry attempts.

    Returns:
        str: The extracted shell command. If proper formatting is not achieved, returns the raw output.
    """
    shell = detect_shell()
    system_prompt = get_system_prompt(shell)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": command}
    ]

    # Import the new OpenAI client-based interface.
    from openai import OpenAI
    client = OpenAI()
    raw_output = ""
    for attempt in range(1, retry + 1):
        try:
            response = client.chat.completions.create(
                model=openai_model,
                messages=messages,
                max_tokens=50,
                temperature=0.7,
                stop=["\n"]
            )
            raw_output = response.choices[0].message.content.strip().strip('`')
            if raw_output.startswith("<cmd>") and raw_output.endswith("</cmd>"):
                start = len("<cmd>")
                end = -len("</cmd>")
                return raw_output[start:end].strip()
            else:
                print(f"Attempt {attempt}: Response did not contain proper command tags.")
        except Exception as e:
            print(f"Attempt {attempt}: OpenAI API call failed with error: {e}")
    
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

def run_openai_shell(api_key: str, openai_model: str, retry: int) -> None:
    """
    Run an interactive shell interface using OpenAI API integration.

    This function configures the OpenAI API, then enters an interactive loop where the user can enter commands.
    Commands starting with '!' are processed via the OpenAI API to generate shell commands.

    Args:
        api_key (str): The API key for OpenAI.
        openai_model (str): The OpenAI model to use.
        retry (int): The number of retry attempts for formatting the shell command.
    """
    # Configure the OpenAI API key.
    configure_openai(api_key)
    
    # Optionally, save configuration for external mode.
    config = {
        "mode": "openai",
        "openai_api_key": api_key,
        "openai_model": openai_model,
        "retry": retry
    }
    config_file = os.path.join(os.path.expanduser("~"), ".shellgenie_config.json")
    try:
        with open(config_file, "w") as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Error saving OpenAI config: {e}")
    
    session = PromptSession(history=FileHistory("openai_command_history.txt"))
    completer = WordCompleter(
        ["dir", "cd", "cls", "copy", "move", "del", "mkdir", "rmdir", "exit"],
        ignore_case=True
    )
    
    print("Welcome to the OpenAI-powered Shell Interface! Type your commands below.")
    print("Use '!' to invoke the OpenAI API for command generation. Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = session.prompt("> ", completer=completer)
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            
            if user_input.startswith("!"):
                generated_command = call_openai(user_input[1:].strip(), openai_model, retry)
                # Allow user to edit the generated command before execution.
                final_command = session.prompt("> ", default=generated_command).strip()
                if final_command:
                    execute_command(final_command)
                else:
                    print("No command entered; skipping execution.")
            else:
                execute_command(user_input)
        except KeyboardInterrupt:
            print("\nOperation canceled.")
        except EOFError:
            print("\nExiting.")
            break
