import os
import subprocess
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory

def call_llm(command: str) -> str:
    """
    Mock LLM call function. Returns 'dir' for demonstration purposes.
    In future, this will connect to a large language model.
    
    Args:
        command (str): The command passed by the user without the leading '!'
    
    Returns:
        str: A shell command suggested by the LLM (for now, always returns 'dir').
    """
    print(f"Calling LLM with: {command}")
    return "dir"  # This will later be replaced with actual LLM output.

def execute_command(command: str):
    """
    Execute a shell command and display its output.
    
    Args:
        command (str): The shell command to execute.
    """
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(e.stderr)

def main():
    session = PromptSession(history=FileHistory("command_history.txt"))
    completer = WordCompleter(["dir", "cd", "cls", "copy", "move", "del", "mkdir", "rmdir", "exit"], ignore_case=True)

    print("Welcome to the Custom Command Interface! Type your commands below.")
    print("Use '!' to invoke the LLM. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = session.prompt("> ", completer=completer)
            
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            
            if user_input.startswith("!"):
                # Intercept command and pass to call_llm
                llm_command = call_llm(user_input[1:].strip())
                print(f"LLM suggested command: {llm_command}")
                confirmation = session.prompt("Do you want to execute this command? (yes/no): ").strip().lower()
                
                if confirmation in {"yes", "y"}:
                    execute_command(llm_command)
                else:
                    print("Command execution skipped.")
            else:
                # Execute normal shell command
                execute_command(user_input)

        except KeyboardInterrupt:
            print("\nOperation canceled.")
        except EOFError:
            print("\nExiting.")
            break

if __name__ == "__main__":
    main()
