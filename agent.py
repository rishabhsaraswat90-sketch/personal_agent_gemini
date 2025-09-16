import argparse
import json
import sys
import os
import time
from rich.console import Console
from rich.markdown import Markdown
import pathlib 

# --- NEW: DEFINE ABSOLUTE PATHS ---
# Gets the full path to the directory this script (ask.py) is in
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()

# Define the full, absolute paths for our "mailbox" files
IPC_FILE = SCRIPT_DIR / "prompt.json"
RESPONSE_FILE = SCRIPT_DIR / "response.json"
# ----------------------------------


def main():
    """
    Parses user's command, writes it to a file, waits for a response
    file, and prints the response.
    """
    parser = argparse.ArgumentParser(
        description="Ask the AI agent a question. \n"
                    "Example: python ask.py \"What's this error?\" --model pro",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        '--model',
        type=str,
        choices=['pro', 'flash'],
        default='flash',
        help="Choose the model:\n"
             "  'pro'   = (Slower) Sends text + screenshot.\n"
             "  'flash' = (Faster) Sends text-only."
    )
    
    parser.add_argument(
        'prompt',
        type=str,
        nargs='+',
        help="The text prompt to send to the AI."
    )
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return

    args = parser.parse_args()
    prompt_text = " ".join(args.prompt)
    
    data = {
        "prompt": prompt_text,
        "model": args.model
    }
    
    console = Console()

    # --- 1. Clean up any old response file ---
    if os.path.exists(RESPONSE_FILE):
        os.remove(RESPONSE_FILE)

    # --- 2. Write the new prompt ---
    try:
        with open(IPC_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        console.print(f"[!] Error writing prompt file: {e}", style="bold red")
        return

    # --- 3. Wait for the response ---
    console.print(f"Sent to agent (Model: {args.model})... [bold yellow]Waiting for response...[/bold yellow]")
    
    timeout_seconds = 60 # Max time to wait (in seconds)
    start_time = time.time()
    
    while True:
        # Check for timeout
        if time.time() - start_time > timeout_seconds:
            console.print("\n[!] Error: Timed out waiting for a response from the server.", style="bold red")
            console.print("Is 'agent_server.py' running in another terminal?", style="yellow")
            break
        
        # --- 4. Check if the response file exists ---
        if os.path.exists(RESPONSE_FILE):
            try:
                # --- 5. Read the response ---
                with open(RESPONSE_FILE, 'r') as f:
                    response_data = json.load(f)
                
                # --- 6. Delete the response file ---
                os.remove(RESPONSE_FILE)
                
                # --- 7. Print the formatted Markdown answer! ---
                console.print("\n--- Gemini's Answer ---")
                response_text = response_data.get("response", "No response text found.")
                md = Markdown(response_text)
                console.print(md)
                console.print("------------------------")
                
                break # Exit the loop, we're done
                
            except Exception as e:
                console.print(f"\n[!] Error reading response file: {e}", style="bold red")
                break
        
        # Wait 1 second before checking again
        time.sleep(1)

if __name__ == "__main__":
    main()