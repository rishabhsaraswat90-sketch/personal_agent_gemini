# 🤖 Gemini Personal Agent

This is a powerful, lightweight personal AI agent that runs on your Windows machine. It allows you to ask questions from any terminal, and it can intelligently decide whether to answer with text-only (for simple questions) or to take a screenshot of your screen and analyze it (for complex errors or visual questions).

This project uses a "client-server" model:
* **`server.py` (The Brain):** A persistent background server that runs invisibly, listens for requests, and calls the Google Gemini API.
* **`agenet.py` (The Messenger):** A fast client script that you call from your terminal to send a prompt to the "Brain".
* **`gemini.bat` (The Alias):** A command alias that lets you run the agent by just typing `gemini` instead of `python ask.py`.

---

## ✨ Features

* **1-Terminal Operation:** Ask a question and get the answer back in the *same* terminal.
* **Smart Model Selection:** Use the `--model` flag to choose the right tool for the job.
    * **`flash` (default):** Sends a text-only prompt for extremely fast, cheap answers.
    * **`pro`:** Tells the server to take a 5-second delayed screenshot and send both the image and your text prompt for a deep, multi-modal analysis.
* **Background Service:** The server runs invisibly in the background and can be set to launch automatically on Windows startup.
* **Custom Command:** Includes the `gemini.bat` alias so you can just type `gemini "your question"` from anywhere.

---

## ⚙️ Technology Used

* **Python 3**
* **Core Libraries:**
    * `google-generativeai`: For connecting to the Gemini API.
    * `pyautogui`: For capturing screenshots.
    * `rich`: For beautifully formatted Markdown responses in the terminal.
    * `python-dotenv`: For securely managing your API key.
* **IPC:** Uses a JSON-based file system ("mailbox" files) for client-server communication.
* **OS:** Windows (uses `.bat` files, `pathlib`, `shell:startup`, and `pythonw.exe`).

---

## 🚀 Setup

(Full setup instructions are provided in the separate guide.)

1.  **Clone Repo:** Get all project files (`agent_server.py`, `ask.py`, `gemini.bat`).
2.  **Install Python:** Make sure you have Python 3.9+ installed and added to your system `PATH`.
3.  **Install Libraries:**
    ```bash
    pip install google-generativeai python-dotenv pyautogui rich
    ```
4.  **Create `.env` File:** Create a file named `.env` in this same folder and add your API key:
    ```
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```
5.  **Add to PATH:** Add the *full path* to this project folder to your Windows `PATH` environment variable. (This enables the `gemini` command).
6.  **Run Server on Startup:** Create the `start_agent.bat` launcher script inside your Windows `shell:startup` folder (as described in the full guide) to have the server run invisibly on boot.

---

## 💻 How to Use

Once the server is running, just open *any* terminal (CMD, PowerShell, etc.) and type your command.

**For a fast, text-only question:**
```bash
gemini "What is the capital of France?"

**For a complex, visual (screenshot) question:**
gemini "What does this error message mean?" --model pro