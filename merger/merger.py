import sys
import os
import webbrowser
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from PyQt6.QtCore import QUrl

# --- 1. THE JIRA BRIDGE ---
class JiraBridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): return 
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        jira_url = f"https://sig-jm.atlassian.net{self.path.replace('/jira', '')}"
        headers = {'Authorization': self.headers.get('Authorization'), 'Content-Type': 'application/json', 'Accept': 'application/json'}
        try:
            response = requests.post(jira_url, data=post_data, headers=headers)
            self.send_response(response.status_code)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.content)
        except:
            self.send_response(500)
            self.end_headers()

def start_bridge():
    server = HTTPServer(('localhost', 8080), JiraBridgeHandler)
    server.serve_forever()

# --- 2. THE AGGRESSIVE LINK CATCHER ---
class CustomWebEnginePage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        url_str = url.toString()
        # If the URL is external (not our local file), boot it to the real browser
        if url.scheme() in ["http", "https"] and "localhost:8080" not in url_str:
            webbrowser.open(url_str)
            return False 
        return super().acceptNavigationRequest(url, _type, isMainFrame)

    # This catches "window.open" calls often used by React
    def createWindow(self, _type):
        page = CustomWebEnginePage(self.parent())
        page.urlChanged.connect(lambda url: webbrowser.open(url.toString()))
        return page

# --- 3. THE MAIN WINDOW ---
class MergerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The Merger 1.0 - Pro Suite")
        self.resize(1800, 1000)
        self.browser = QWebEngineView()
        
        # Set the page to our smart interceptor
        self.page = CustomWebEnginePage(self.browser)
        self.browser.setPage(self.page)
        
        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True) # Allow JS to trigger links

        script_dir = os.path.dirname(os.path.abspath(__file__))
        html_file = os.path.join(script_dir, "index.html")
        self.browser.setUrl(QUrl.fromLocalFile(html_file))
        self.setCentralWidget(self.browser)

if __name__ == "__main__":
    Thread(target=start_bridge, daemon=True).start()
    app = QApplication(sys.argv)
    window = MergerApp()
    window.show()
    sys.exit(app.exec())