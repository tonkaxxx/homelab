import http.server
import socketserver
import os
from dotenv import load_dotenv

load_dotenv()

dir = os.getenv('DIR')
port = int(os.getenv('PORT'))

os.chdir(dir)

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", port), Handler) as httpd:
    httpd.serve_forever()
