import argparse
import json
import sys
import os
import time
from rich.console import Console
from rich.markdown import Markdown
import pathlib
import tkinter
from tkinter import filedialog

# --- DEFINE ABSOLUTE PATHS ---
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
IPC_FILE = SCRIPT_DIR / "prompt.json"
RESPONSE_FILE = SCRIPT_DIR / "response.json"

def main():
    """
    Parses user's command, optionally opens a file dialog for any media,
    writes the request to a file, waits for a response, and prints it.
    """
    parser = argparse.ArgumentParser(
        description="Ask the AI agent a question.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        '--chat',
        type=str,
        default=None,
        help="The name of the conversation to continue or start (e.g., 'project_ideas')."
    )

    parser.add_argument(
        '--model',
        type=str,
        choices=['pro', 'flash'],
        default='flash',
        help="Choose the model for one-off requests:\n"
             "  'pro'   = (Slower) Sends text + screenshot.\n"
             "  'flash' = (Faster) Sends text-only."
    )
    
    # --- RENAMED to --media ---
    parser.add_argument(
        '--media',
        action='store_true',
        help="Open a file dialog to select any media file for analysis (image, video, audio, etc.)."
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
    
    console = Console()
    media_path = None

    # --- UPDATED logic to handle the --media flag ---
    if args.media:
        console.print("[yellow]Please select a media file to analyze...[/yellow]")
        root = tkinter.Tk()
        root.withdraw()
        
        # Changed to allow all file types
        media_path = filedialog.askopenfilename(
            title="Select a Media File to Analyze",
            filetypes=[("All files", "*.*")] 
        )
        
        if not media_path:
            console.print("[bold red]No file selected. Aborting.[/bold red]")
            return
        
        console.print(f"[green]Selected file:[/green] {media_path}")
    
    data = {
        "prompt": prompt_text,
        "model": args.model,
        "media_path": media_path, # Renamed from pdf_path
        "chat_name": args.chat
    }
    
    if os.path.exists(RESPONSE_FILE):
        os.remove(RESPONSE_FILE)

    try:
        with open(IPC_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        console.print(f"[!] Error writing prompt file: {e}", style="bold red")
        return

    status_message = f"Sent to agent (Model: {args.model})"
    if args.chat:
        status_message += f" (Chat: {args.chat})"
    status_message += "... [bold yellow]Waiting for response...[/bold yellow]"
    
    console.print(status_message)
    
    timeout_seconds = 300 # Increased timeout for potentially large media files
    start_time = time.time()
    
    while True:
        if time.time() - start_time > timeout_seconds:
            console.print("\n[!] Error: Timed out waiting for a response from the server.", style="bold red")
            console.print("Is 'server.py' running in another terminal?", style="yellow")
            break
        
        if os.path.exists(RESPONSE_FILE):
            try:
                with open(RESPONSE_FILE, 'r') as f:
                    response_data = json.load(f)
                
                os.remove(RESPONSE_FILE)
                
                if response_data.get("error"):
                    console.print("\n[!] The Agent Server reported an error:", style="bold red")
                    console.print(response_data.get("response"))
                else:
                    console.print("\n--- Gemini's Answer ---")
                    response_text = response_data.get("response", "No response text found.")
                    md = Markdown(response_text)
                    console.print(md)
                    console.print("------------------------")
                
                break
                
            except Exception as e:
                console.print(f"\n[!] Error reading response file: {e}", style="bold red")
                break
        
        time.sleep(1)

if __name__ == "__main__":
    main()