import os
import json
import time
import google.generativeai as genai
import pyautogui
from dotenv import load_dotenv
from rich.console import Console
import pathlib
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- DEFINE ABSOLUTE PATHS ---
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
IPC_FILE = SCRIPT_DIR / "prompt.json"
RESPONSE_FILE = SCRIPT_DIR / "response.json"
HISTORY_FILE = SCRIPT_DIR / "chat_history.json"
SCREENSHOT_DIR = SCRIPT_DIR / "screenshots"

# --- MODIFIED: Added a dedicated, stable model for chat sessions ---
MODEL_MAP = {
    "flash": "gemini-2.5-flash", # For fast one-off requests
    "pro": "gemini-2.5-pro",     # For powerful one-off requests
    "chat": "gemini-1.5-flash"      # Stable model for all chat history
}
# -----------------------------------------------------------------

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_history(all_chats):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(all_chats, f, indent=2)

def main():
    SCREENSHOT_DIR.mkdir(exist_ok=True)

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
    
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    try:
        while True:
            if os.path.exists(IPC_FILE):
                try:
                    with open(IPC_FILE, 'r') as f:
                        data = json.load(f)
                    os.remove(IPC_FILE)
                    
                    prompt = data.get("prompt")
                    short_model_name = data.get("model")
                    pdf_path = data.get("pdf_path")
                    chat_name = data.get("chat_name")
                    
                    if not prompt: prompt = "What is this?"

                    console.print("\n[+] New Request Received!", style="bold green")
                    console.print(f"  > Prompt: \"{prompt}\"")
                    
                    full_response_text = ""
                    
                    if chat_name:
                        # --- CHAT LOGIC ---
                        console.print(f"  > Chat Session: '{chat_name}'", style="yellow")
                        all_chats = load_history()
                        chat_object = all_chats.get(chat_name, {"file_name": None, "history": []})
                        history = chat_object.get("history", [])
                        
                        # --- MODIFIED: Always use the stable chat model ---
                        model = genai.GenerativeModel(MODEL_MAP.get("chat"), safety_settings=safety_settings)
                        console.print(f"  > Using stable chat model: {MODEL_MAP.get('chat')}")
                        # --------------------------------------------------

                        chat = model.start_chat(history=history)
                        
                        chat_payload = [prompt]
                        
                        if pdf_path:
                            console.print(f"  > Attaching PDF: '{pdf_path}'...", style="cyan")
                            uploaded_file = genai.upload_file(path=pdf_path)
                            chat_object["file_name"] = uploaded_file.name
                            chat_payload.append(uploaded_file)
                        elif short_model_name == 'pro': # Check if this is a screenshot chat
                            console.print("  > Action: PRO chat request. Saving screenshot...", style="magenta")
                            time.sleep(5)
                            image = pyautogui.screenshot()
                            temp_path = SCREENSHOT_DIR / f"temp_{int(time.time())}.png"
                            image.save(temp_path)
                            
                            uploaded_file = genai.upload_file(path=temp_path)
                            chat_object["file_name"] = uploaded_file.name
                            chat_payload.append(uploaded_file)
                            
                            os.remove(temp_path)
                            console.print(f"  > Screenshot uploaded and linked to chat.", style="dim")

                        response = chat.send_message(chat_payload, stream=True)
                        for chunk in response:
                            full_response_text += chunk.text
                        
                        chat_object["history"] = [h.to_dict() for h in chat.history]
                        all_chats[chat_name] = chat_object
                        save_history(all_chats)
                        console.print(f"  > Chat history for '{chat_name}' updated.", style="dim")
                        
                    else:
                        # --- ONE-OFF REQUEST LOGIC ---
                        payload = []
                        if pdf_path:
                            full_model_name = MODEL_MAP.get("pro")
                            # ... (rest of one-off logic is unchanged)
                            console.print(f"  > Action: PDF Analysis on '{pdf_path}'...", style="cyan")
                            uploaded_file = genai.upload_file(path=pdf_path)
                            payload = [prompt, uploaded_file]
                        elif short_model_name == 'pro':
                            full_model_name = MODEL_MAP.get("pro")
                            console.print("  > Action: PRO request. Taking screenshot...", style="magenta")
                            time.sleep(5)
                            image = pyautogui.screenshot()
                            payload = [prompt, image]
                        else: # 'flash'
                            full_model_name = MODEL_MAP.get("flash")
                            console.print("  > Action: Text-only request.", style="magenta")
                            payload = [prompt]
                        
                        model = genai.GenerativeModel(full_model_name, safety_settings=safety_settings)
                        response = model.generate_content(payload, stream=True)
                        for chunk in response:
                            full_response_text += chunk.text

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
                    if os.path.exists(IPC_FILE): os.remove(IPC_FILE)
                
                console.print(f"\nListening for messages in '{IPC_FILE}'...", style="cyan")

            time.sleep(1)
            
    except KeyboardInterrupt:
        console.print("\n\nAgent server shutting down. Goodbye!", style="bold red")

if __name__ == "__main__":
    main()