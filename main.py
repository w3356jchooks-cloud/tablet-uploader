import os
import threading
import time
import http.server
import socketserver
import json

# Localized Termux communication directory to bypass Android storage limits
COMM_DIR = "/data/data/com.termux/files/home/.backup_communication"
TRIGGER_FILE = os.path.join(COMM_DIR, ".backup_trigger")
ACCT_TRIGGER = os.path.join(COMM_DIR, ".account_trigger")
STOP_TRIGGER = os.path.join(COMM_DIR, ".backup_stop")
STATUS_FILE = os.path.join(COMM_DIR, "backup_status.txt")

global_console = "Dashboard ready. Awaiting command...\n"
current_btn_text = "Start Cloud Backup"

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global global_console, current_btn_text
        
        # 1. Serve the HTML layout
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            try:
                with open("index.html", "rb") as html_file:
                    self.wfile.write(html_file.read())
            except FileNotFoundError:
                self.wfile.write(b"Error: 'index.html' file is missing in this folder!")
                
        # 2. Continually feed layout state updates back to Chrome
        elif self.path.startswith('/status'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-store, must-revalidate')
            self.end_headers()
            
            if os.path.exists(STATUS_FILE):
                try:
                    with open(STATUS_FILE, "r") as sf:
                        status_content = sf.read()
                    
                    # Read the final line or current state for the button text
                    lines = status_content.strip().split('\n')
                    last_line = lines[-1] if lines else ""
                    
                    if "RUNNING" in last_line or "Transferred" in status_content:
                        current_btn_text = "Uploading files..."
                    elif "CONFIG_MODE" in last_line:
                        current_btn_text = "Authenticating..."
                    else:
                        current_btn_text = "Start Cloud Backup"
                    
                    # Stream the contents directly into the dashboard console log
                    global_console = status_content
                except: 
                    pass
            
            res = {"console": global_console, "btnText": current_btn_text}
            self.wfile.write(json.dumps(res).encode())
            
        # 3. Catch button clicks safely from Chrome
        elif self.path.startswith('/action'):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
            
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            act_type = query.get('type', [''])[0]
            slot = query.get('slot', ['personal'])[0]
            
            if act_type == 'backup':
                os.makedirs(COMM_DIR, exist_ok=True)
                with open(STATUS_FILE, "w") as sf: 
                    sf.write(f"[BACKUP] Launching upload tool for slot '{slot}'...\nRUNNING\n")
                with open(TRIGGER_FILE, "w") as tf: 
                    tf.write(slot)
                print(f"--> Triggered backup for {slot}")
                
            elif act_type == 'stop':
                os.makedirs(COMM_DIR, exist_ok=True)
                with open(STATUS_FILE, "w") as sf: 
                    sf.write("[HALT] Dispatched termination trigger...\nSTOPPED\n")
                with open(STOP_TRIGGER, "w") as f: 
                    f.write("stop")
                print("--> Triggered emergency stop")

def launch_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", 8080), DashboardHandler) as httpd:
        httpd.serve_forever()

if __name__ == '__main__':
    server_thread = threading.Thread(target=launch_server, daemon=True)
    server_thread.start()
    print("Dashboard server running completely offline on port 8080.")
    
    while True:
        time.sleep(1)

