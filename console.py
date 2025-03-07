#!/usr/bin/env python3
"""
Console Entry Point for ShellGenie

This script processes command-line arguments, including flags for switching between
locally hosted and external (OpenAI) LLM models. It supports authentication and model selection
for OpenAI via the --openai-api-key and --openai-model flags. The configuration is stored in the
config file and can be displayed using the -q/--query flag.

When external mode is selected (using -e openai), the OpenAI submodule is used to drive the
interactive shell interface.
"""

import argparse
import json
import sys
from ShellGenie import load_config, run_shell, save_config, run_openai_shell

# CONFIG_FILE is defined in ShellGenie/__init__.py; we import it here to update the config for external mode.
from ShellGenie import CONFIG_FILE

def main() -> None:
    """
    Parse command-line arguments, update the configuration with OpenAI authentication/model settings
    if external mode is selected, and launch the interactive shell.

    Modes:
        - Local (default): Uses locally hosted models (repo_id and filename).
        - External: Uses the OpenAI API. Requires --openai-api-key and --openai-model.

    The -q/--query flag prints the current configuration.
    """
    parser = argparse.ArgumentParser(description="Custom AI Shell Interface with LLM integration")
    
    # Mutually exclusive mode flags: external vs local
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("-e", "--external", type=str, choices=["openai"],
                            help="Use external hosted LLM. Currently, only 'openai' is supported.")
    mode_group.add_argument("-l", "--local", action="store_true",
                            help="Use locally hosted LLM (default).")
    
    # Local model configuration (only used in local mode)
    parser.add_argument("--repo", type=str, help="Repository ID for the local model")
    parser.add_argument("--file", type=str, help="Filename for the local model")
    
    # General configuration
    parser.add_argument("--retry", type=int,
                        help="Number of retry attempts for LLM command formatting", default=None)
    
    # OpenAI configuration (only used in external mode)
    parser.add_argument("--openai-api-key", type=str, help="API key for OpenAI")
    parser.add_argument("--openai-model", type=str, help="OpenAI model name (e.g., gpt-3.5-turbo)")
    
    # Query flag to display the current configuration
    parser.add_argument("-q", "--query", action="store_true",
                        help="Print configuration and exit")
    
    args = parser.parse_args()

    # Load stored configuration (a dict read from the config file)
    config = load_config()

    # Determine mode: external (openai) vs local. Default to local.
    if args.external == "openai":
        mode = "openai"
    elif args.local:
        mode = "local"
    else:
        mode = config.get("mode", "local")

    # Process configuration based on the selected mode
    if mode == "openai":
        # For OpenAI, require both API key and model name
        openai_api_key = args.openai_api_key if args.openai_api_key is not None else config.get("openai_api_key")
        openai_model = args.openai_model if args.openai_model is not None else config.get("openai_model")
        if not openai_api_key or not openai_model:
            print("Error: For external OpenAI mode, you must provide both --openai-api-key and --openai-model.")
            print("Example usage:")
            print("  python console.py -e openai --openai-api-key YOUR_API_KEY --openai-model gpt-3.5-turbo")
            sys.exit(1)
    else:
        # For local mode, use repo and file flags or stored defaults
        repo_id = args.repo if args.repo is not None else config.get("repo_id", "TheBloke/LLaMA-2-7B-chat-GGUF")
        filename = args.file if args.file is not None else config.get("filename", "llama-2-7b-chat.Q6_K.gguf")

    # Determine retry count (common to both modes)
    retry_value = args.retry if args.retry is not None else config.get("retry", 3)

    # Update configuration dictionary with the latest values
    config["mode"] = mode
    config["retry"] = retry_value
    if mode == "openai":
        config["openai_api_key"] = openai_api_key
        config["openai_model"] = openai_model
    else:
        config["repo_id"] = repo_id
        config["filename"] = filename

    # If query flag is set, print the current configuration and exit
    if args.query:
        print("Current Configuration:")
        print(f"  Mode: {config.get('mode')}")
        if config.get("mode") == "openai":
            print(f"  OpenAI API Key: {config.get('openai_api_key')}")
            print(f"  OpenAI Model: {config.get('openai_model')}")
        else:
            print(f"  Repository ID: {config.get('repo_id')}")
            print(f"  Filename: {config.get('filename')}")
        print(f"  Retry Attempts: {config.get('retry')}")
        return

    # Save the updated configuration to the config file.
    # For external (OpenAI) mode, we write the entire config dict.
    if mode == "openai":
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")
    else:
        save_config(config.get("repo_id"), config.get("filename"), retry_value)

    # Launch the appropriate shell interface.
    if mode == "openai":
        print("External OpenAI mode selected.")
        # Run the OpenAI-powered shell interface.
        run_openai_shell(openai_api_key, openai_model, retry_value)
    else:
        run_shell(config.get("repo_id"), config.get("filename"), retry_value)

if __name__ == "__main__":
    main()
