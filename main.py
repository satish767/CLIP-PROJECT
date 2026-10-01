# ==============================================================================
# Part 1: All Necessary Imports
# ==============================================================================
import time
import requests
import socket
import qrcode
from flask import Flask, request, jsonify, render_template
from threading import Thread
from datetime import datetime, timedelta
import pyperclip

# ==============================================================================
# Part 2: The Flask Web Server (No Changes Here)
# ==============================================================================
app = Flask(__name__)
clipboard_content = ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get', methods=['GET'])
def get_text():
    return jsonify({'text': clipboard_content})

@app.route('/api/update', methods=['POST'])
def update_text():
    global clipboard_content
    data = request.get_json()
    if 'text' in data:
        clipboard_content = data['text']
    return jsonify({'status': 'success'})

# ==============================================================================
# Part 3: The History and Cleanup Functions (No Changes Here)
# ==============================================================================
HISTORY_FILE = "clipboard_history.txt"
DAYS_TO_KEEP = 3

def save_to_history(text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {text}\n"
    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"Saved to {HISTORY_FILE}")
    except Exception as e:
        print(f"Error saving to history file: {e}")

def cleanup_old_history():
    print("Checking for old history entries...")
    fresh_entries = []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                timestamp_str = line[1:20]
                entry_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                if datetime.now() - entry_time < timedelta(days=DAYS_TO_KEEP):
                    fresh_entries.append(line)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            f.writelines(fresh_entries)
        print("Cleanup complete.")
    except FileNotFoundError:
        print("History file not found. A new one will be created.")
    except Exception as e:
        print(f"Error during cleanup: {e}")

# ==============================================================================
# Part 4: The NEW Background Listener Logic
# This is the simplified version without any pop-ups.
# ==============================================================================
def listener_loop():
    last_text = ""
    SERVER_URL = "http://127.0.0.1:5000/api/get"
    print("Listener thread started... Silently waiting for new text.")
    while True:
        try:
            response = requests.get(SERVER_URL)
            if response.status_code == 200:
                current_text = response.json().get('text', '')
                if current_text and current_text != last_text:
                    print(f"New text received: {current_text[:30]}...")
                    
                    # 1. Silently copy to clipboard
                    pyperclip.copy(current_text)
                    
                    # 2. Silently save to history
                    save_to_history(current_text)
                    
                    last_text = current_text
        except requests.exceptions.RequestException:
            time.sleep(5) # Wait longer if server is not running
        time.sleep(2)

# ==============================================================================
# Part 5: Main Application Startup
# ==============================================================================
if __name__ == "__main__":
    # 1. Clean up old history first
    cleanup_old_history()

    # 2. Start the Flask server in a background thread
    server_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000), daemon=True)
    server_thread.start()

    # 3. Start the new silent listener in another background thread
    listener_thread = Thread(target=listener_loop, daemon=True)
    listener_thread.start()

    # 4. Generate and show the QR code
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    url = f"http://{host_ip}:5000"
    print(f"\nServer is running at: {url}")
    print("Scan the QR code with your phone to connect.")
    qr_img = qrcode.make(url)
    qr_img.show()
    
    # 5. Keep the main script alive so the background threads can run
    print("\nApplication is running silently in the background. Press CTRL+C to quit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")