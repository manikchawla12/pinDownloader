import http.server
import socketserver
import os

PORT = 3000

class CleanURLHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Get the standard translated path
        translated = super().translate_path(path)
        
        # If it doesn't exist and has no extension, check if a .html version exists
        if not os.path.exists(translated) and not os.path.splitext(translated)[1]:
            html_version = translated + ".html"
            if os.path.exists(html_version):
                return html_version
                
        return translated

# Ensure we can reuse the port immediately
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("127.0.0.1", PORT), CleanURLHandler) as httpd:
    print(f"Serving at http://127.0.0.1:{PORT} with clean URLs enabled...")
    httpd.serve_forever()
