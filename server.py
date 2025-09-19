import os
import json
import time
import google.generativeai as genai
import pyautogui
from dotenv import load_dotenv
from rich.console import Console
import pathlib

# --- DEFINE ABSOLUTE PATHS ---
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
IPC_FILE = SCRIPT_DIR / "prompt.json"
RESPONSE_FILE = SCRIPT_DIR / "response.json"

MODEL_MAP = {
    "flash": "gemini-2.5-flash",
    "pro": "gemini-2.5-pro"
}

def main():
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
                        image = pyautogui.screenshot()
                        console.print("  > Screenshot captured!", style="magenta")
                        payload = [prompt, image]
                    else: # 'flash'
                        console.print("  > Action: Text-only request.", style="magenta")
                        payload = [prompt]

                    console.print("  > Calling API and streaming response...", style="yellow")
                    
                    # --- THE FIX: Use stream=True and collect the response ---
                    response = model.generate_content(payload, stream=True)
                    
                    full_response_text = ""
                    for chunk in response:
                        full_response_text += chunk.text
                    # --------------------------------------------------------
                    
                    # --- SUCCESS RESPONSE ---
                    response_data = {"response": full_response_text, "error": False}
                    with open(RESPONSE_FILE, 'w') as f:
                        json.dump(response_data, f)
                    
                    console.print(f"\n...Response written to {RESPONSE_FILE}.", style="bold green")

                except Exception as e:
                    console.print(f"\n[!] Error processing request: {e}", style="bold red")
                    
                    error_message = f"An error occurred on the server:\n\n{e}"
                    response_data = {"response": error_message, "error": True}
                    with open(RESPONSE_FILE, 'w') as f:
                        json.dump(response_data, f)
                    
                    if os.path.exists(IPC_FILE):
                        os.remove(IPC_FILE)
                
                console.print(f"\nListening for messages in '{IPC_FILE}'...", style="cyan")

            time.sleep(1)
            
    except KeyboardInterrupt:
        console.print("\n\nAgent server shutting down. Goodbye!", style="bold red")

if __name__ == "__main__":
    main()