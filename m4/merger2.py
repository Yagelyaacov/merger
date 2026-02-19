import sys
import os
import webbrowser
import time
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from PyQt6.QtCore import QUrl

# CONFIGURATION
PORT = 5555 
HOST = "127.0.0.1"

# --- 1. THE ROBUST SERVER ---
class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True # Prevents "Address already in use" errors

class UnifiedHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Print logs to terminal
        print(f"\033[96m🔹 [{self.command}] {self.path}\033[0m")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_ui_file()
        elif self.path.startswith('/jira/'):
            self.proxy_jira_request('GET')
        else:
            self.send_error(404)

    def do_POST(self): self.proxy_jira_request('POST')
    def do_PUT(self): self.proxy_jira_request('PUT')

    def serve_ui_file(self):
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            file_path = os.path.join(base_path, 'index.html')
            
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            print(f"❌ [UI ERROR] Could not serve file: {e}")
            self.send_error(500)

    def proxy_jira_request(self, method):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length > 0 else None
        
        # Remove /jira prefix to get real path
        jira_path = self.path.replace('/jira', '')
        jira_url = f"https://sig-jm.atlassian.net{jira_path}"
        
        headers = {
            'Authorization': self.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            print(f"🔸 [PROXY] {method} -> {jira_url}")
            resp = requests.request(
                method=method, 
                url=jira_url, 
                data=body, 
                headers=headers, 
                timeout=10, 
                verify=False
            )
            
            self.send_response(resp.status_code)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(resp.content)
            print(f"✅ [PROXY] Success: {resp.status_code}")
            
        except Exception as e:
            print(f"❌ [PROXY ERROR] {e}")
            self.send_error(500)

def start_server():
    try:
        server = ReusableHTTPServer((HOST, PORT), UnifiedHandler)
        print(f"🚀 SERVER STARTED: http://{HOST}:{PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"💀 SERVER CRASHED: {e}")

# --- 2. LINK INTERCEPTOR (Fixed) ---
class CustomWebEnginePage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        url_str = url.toString()
        
        # LOGIC: 
        # If the URL contains our local server address, keep it inside the app.
        # If it is anything else (github.com, atlassian.net), kick it out to Chrome/Edge.
        if "127.0.0.1:5555" not in url_str:
            print(f"🔗 [EXTERNAL LINK] Opening in Browser: {url_str}")
            webbrowser.open(url_str)
            return False  # Stop the internal app from trying to load it
            
        return super().acceptNavigationRequest(url, _type, isMainFrame)

    def createWindow(self, _type):
        # This handles target="_blank" (New Tab) requests from React
        page = CustomWebEnginePage(self.parent())
        page.urlChanged.connect(self._on_url_changed)
        return page

    def _on_url_changed(self, url):
        url_str = url.toString()
        print(f"🔗 [NEW WINDOW] Opening in Browser: {url_str}")
        webbrowser.open(url_str)

# --- 3. MAIN APP ---
class MergerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The Merger Pro")
        self.resize(1800, 1000)

        self.browser = QWebEngineView()
        self.page = CustomWebEnginePage(self.browser)
        self.browser.setPage(self.page)
        
        # Point to the new port 5555
        self.browser.setUrl(QUrl(f"http://{HOST}:{PORT}"))
        
        self.setCentralWidget(self.browser)

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    
    # Start server
    Thread(target=start_server, daemon=True).start()
    
    # Give the server 1 second to breathe before launching UI
    time.sleep(1.0)
    
    app = QApplication(sys.argv)
    window = MergerApp()
    window.show()
    sys.exit(app.exec())