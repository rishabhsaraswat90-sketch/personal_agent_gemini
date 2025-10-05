# 🤖 Gemini Personal Agent

This is a powerful, lightweight, multi-modal AI agent that runs on your Windows machine. It allows you to ask questions from any terminal and can intelligently handle text, screenshots, and other media files like PDFs, images, and videos.

This project uses a "client-server" model:
* **`server.py` (The Brain):** A persistent background server that runs invisibly, listens for requests, and calls the Google Gemini API.
* **`agent.py` (The Messenger):** A fast client script that you call from your terminal to send a prompt to the "Brain".
* **`gemini.bat` (The Alias):** A command alias that lets you run the agent by just typing `gemini` instead of `python agent.py`.

---

## ✨ Features

* **1-Terminal Operation:** Ask a question and get the answer back in the **same** terminal window.
* **Persistent Chat History:** Use the `--chat <chat_name>` flag to save and continue conversations. The agent remembers the context of previous questions in that specific chat.
* **Screenshot Analysis:** Use the `--model pro` flag to have the agent take a 5-second delayed screenshot and analyze it along with your text prompt.
* **Multi-Modal File Analysis:** Use the `--media` flag to open a file picker and analyze any supported file type (PDFs, images, videos, audio, etc.). This feature automatically uses the powerful `gemini-2.5-pro` model for the best results.
* **Contextual File Memory:** When you use `--media` or `--model pro` within a named chat, the agent **remembers that file** for all follow-up questions in that same chat session.
* **Background Service:** The server runs invisibly in the background and can be set to launch automatically on Windows startup.

---

## ⚙️ Technology Used

* **Python 3**
* **Core Libraries:**
    * `google-generativeai`: For connecting to the Gemini API.
    * `pyautogui`: For capturing screenshots.
    * `rich`: For beautifully formatted Markdown responses in the terminal.
    * `python-dotenv`: For securely managing your API key.
    * `tkinter`: For the graphical file picker dialog.
* **IPC:** Uses a JSON-based file system ("mailbox" files) for client-server communication.
* **OS:** Windows (uses `.bat` files, `pathlib`, `shell:startup`, and `pythonw.exe`).

---

## 🚀 Setup

1.  **Clone Repo:** Get all project files (`server.py`, `agent.py`, `gemini.bat`).
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
6.  **Run Server on Startup:** Create a `start_agent.bat` launcher script inside your Windows `shell:startup` folder (as described in the full guide) to have the server run invisibly on boot.

---

## 💻 How to Use

Once the server is running, just open *any* terminal (CMD, PowerShell, etc.) and type your command.

#### One-Off Requests (No History)

* **Simple text question (uses `flash` model):**
    ```bash
    gemini "What is the capital of France?"
    ```
* **Screenshot analysis (uses `pro` model):**
    ```bash
    gemini "What does this error message mean?" --model pro
    ```
* **Media file analysis (uses `pro` model):**
    ```bash
    gemini "Summarize this video for me" --media
    ```

#### Conversational Requests (With History)

* **Start a text-based chat (uses `flash` model):**
    ```bash
    gemini "Help me brainstorm ideas for a new Python project" --chat python_ideas
    ```
* **Introduce a file to a new chat (uses `pro` model):**
    ```bash
    gemini "Summarize this document" --media --chat report_analysis
    ```
* **Ask a follow-up question (remembers the file):**
    ```bash
    gemini "Elaborate on the third point" --chat report_analysis
    ```