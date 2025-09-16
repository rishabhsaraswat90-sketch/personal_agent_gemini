import os
import json
import time
import google.generativeai as genai
import pyautogui
from dotenv import load_dotenv
from rich.console import Console
import pathlib 

# --- NEW: DEFINE ABSOLUTE PATHS ---
# Gets the full path to the directory this script (agent_server.py) is in
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()

# Define the full, absolute paths for our "mailbox" files
IPC_FILE = SCRIPT_DIR / "prompt.json"
RESPONSE_FILE = SCRIPT_DIR / "response.json"
# ----------------------------------


# Maps our friendly names to the full Google API names
MODEL_MAP = {
    "flash": "gemini-2.5-flash",
    "pro": "gemini-2.5-pro"
}

def main():
    """
    Main function to configure and run the agent server.
    """
    
    # Find the .env file in the script's directory
    load_dotenv(dotenv_path=SCRIPT_DIR / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        return
    
    genai.configure(api_key=api_key)
    
    console = Console()
    console.print("--- AI Agent Server (The Brain) is RUNNING ---", style="bold green")
    console.print(f"Listening for messages in '{IPC_FILE}'...", style="cyan")
    console.print("Press Ctrl+C to stop.", style="yellow")

    try:
        while True:
            if os.path.exists(IPC_FILE):
                try:
                    with open(IPC_FILE, 'r') as f:
                        data = json.load(f)
                    
                    os.remove(IPC_FILE)
                    
                    prompt = data.get("prompt")
                    short_model_name = data.get("model")
                    
                    if not prompt or not short_model_name:
                        console.print(f"Invalid data in {IPC_FILE}. Skipping.", style="red")
                        continue
                    
                    full_model_name = MODEL_MAP.get(short_model_name)
                    
                    if not full_model_name:
                        console.print(f"Invalid model name '{short_model_name}'. Skipping.", style="red")
                        continue

                    console.print("\n[+] New Request Received!", style="bold green")
                    console.print(f"  > Model: {short_model_name} (using {full_model_name})")
                    console.print(f"  > Prompt: \"{prompt}\"")
                    
                    model = genai.GenerativeModel(full_model_name)
                    
                    payload = []
                    if short_model_name == 'pro':
                        console.print("  > Action: PRO request. Taking screenshot in 5 SECONDS...", style="magenta")
                        console.print("  > QUICK! SWITCH TO THE WINDOW YOU WANT TO CAPTURE!", style="bold red")
                        time.sleep(5)
                        console.print("  > Action: Taking screenshot...", style="magenta")
                        image = pyautogui.screenshot()
                        payload = [prompt, image]
                    else: # 'flash'
                        console.print("  > Action: Text-only request.", style="magenta")
                        payload = [prompt]

                    # --- 2. MODIFIED: We are REMOVING the stream ---
                    console.print("  > Calling API (this may take a moment)...", style="yellow")
                    
                    # We are now making a single, blocking call
                    response = model.generate_content(payload)
                    
                    # --- 3. NEW: Write the answer to the response file ---
                    response_data = {"response": response.text}
                    with open(RESPONSE_FILE, 'w') as f:
                        json.dump(response_data, f)
                    
                    console.print(f"\n...Response written to {RESPONSE_FILE}.", style="bold green")
                    # -------------------------------------------------

                except Exception as e:
                    console.print(f"\n[!] Error processing request: {e}", style="bold red")
                    if os.path.exists(IPC_FILE):
                        os.remove(IPC_FILE)
                
                console.print(f"\nListening for messages in '{IPC_FILE}'...", style="cyan")

            time.sleep(1)
            
    except KeyboardInterrupt:
        console.print("\n\nAgent server shutting down. Goodbye!", style="bold red")

if __name__ == "__main__":
    main()