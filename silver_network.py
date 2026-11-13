#!/usr/bin/env python3
# SILVER NETWORK - Termux Edition
# Defensive networking and local security diagnostics.
# Python standard library only; optional integrations are detected at runtime.

import os
import sys
import ssl
import json
import time
import socket
import shutil
import hashlib
import platform
import subprocess
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

APP_NAME = "SILVER NETWORK"
VERSION = "1.0.0"
TIMEOUT = 5

C = {
    "reset": "\033[0m", "silver": "\033[97m", "cyan": "\033[96m",
    "blue": "\033[94m", "green": "\033[92m", "yellow": "\033[93m",
    "red": "\033[91m", "dim": "\033[2m", "bold": "\033[1m"
}

def paint(text, color="silver", bold=False):
    b = C["bold"] if bold else ""
    return f"{b}{C.get(color, C['silver'])}{text}{C['reset']}"

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def pause():
    input("\nPress Enter to return to the dashboard...")

def line():
    print(paint("═" *  sixty(), "blue"))

def sixty():
    return 58

def header():
    clear()
    print(paint("╔" + "═"*58 + "╗", "cyan"))
    print(paint("║" + " "*14 + "S I L V E R   N E T W O R K" + " "*17 + "║", "silver", True))
    print(paint("║" + " "*17 + "TERMUX EDITION  v" + VERSION + " "*19 + "║", "cyan"))
    print(paint("╚" + "═"*58 + "╝", "cyan"))
    print(paint(" Defensive networking • Authorized testing • Local audits", "dim"))
    print()

def ask(prompt):
    try:
        return input(paint(prompt, "cyan", True)).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""

def result(label, value, color="silver"):
    print(f"{paint(label + ':', 'cyan', True)} {paint(str(value), color)}")

def run_command(args, timeout=30):
    try:
        p = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=timeout)
        return p.returncode, p.stdout.strip()
    except FileNotFoundError:
        return 127, f"Required command not installed: {args[0]}"
    except subprocess.TimeoutExpired:
        return 124, "Command timed out."
    except Exception as e:
        return 1, str(e)

def installed(name):
    return shutil.which(name) is not None

def safe_host(value):
    # Resolve a single hostname/IP; never accepts shell syntax.
    if not value or any(ch.isspace() for ch in value):
        raise ValueError("Enter one hostname or IP address.")
    return socket.gethostbyname_ex(value)[2]

def system_info():
    header()
    print(paint("SYSTEM INFORMATION", "cyan", True)); line()
    result("Platform", platform.platform())
    result("Python", sys.version.split()[0])
    result("Architecture", platform.machine())
    result("Hostname", socket.gethostname())
    result("Current time", datetime.now().astimezone().isoformat(timespec="seconds"))
    result("Termux prefix", os.environ.get("PREFIX", "Not detected"))
    result("Available disk", shutil.disk_usage(Path.home()).free // (1024*1024), "green")
    print("\nOptional commands:")
    for name in OPTIONAL_COMMANDS:
        result(name, "Available" if installed(name) else "Not installed",
               "green" if installed(name) else "yellow")
    pause()

OPTIONAL_COMMANDS = [
    "ssh", "autossh", "mosh", "nc", "socat", "iperf3", "proxychains4",
    "tor", "torsocks", "mitmproxy", "lynis", "chkrootkit", "clamscan",
    "freshclam", "testssl.sh", "ping", "ip", "termux-wake-lock"
]

def network_info():
    header()
    print(paint("NETWORK INFORMATION", "cyan", True)); line()
    try:
        name = socket.gethostname()
        addresses = sorted(set(socket.gethostbyname_ex(name)[2]))
        result("Device hostname", name)
        result("Local IPv4", ", ".join(addresses) if addresses else "Not found")
    except Exception as e:
        result("Local address", e, "yellow")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("192.0.2.1", 80))
            result("Selected local IP", s.getsockname()[0], "green")
    except Exception:
        result("Selected local IP", "Unavailable", "yellow")
    if installed("ip"):
        code, out = run_command(["ip", "addr"], 10)
        print("\n" + out[:6000])
    else:
        print(paint("\nOptional 'ip' command is not installed.", "yellow"))
    pause()

def dns_lookup():
    header()
    print(paint("DNS LOOKUP", "cyan", True)); line()
    host = ask("Hostname: ")
    try:
        infos = socket.getaddrinfo(host, None)
        ips = sorted(set(x[4][0] for x in infos))
        for ip in ips:
            result("Address", ip, "green")
    except Exception as e:
        result("DNS lookup failed", e, "red")
    pause()

def ping_host():
    header()
    print(paint("CONNECTIVITY CHECK", "cyan", True)); line()
    host = ask("Host you own or are authorized to test: ")
    try:
        ips = safe_host(host)
        result("Resolved IP", ", ".join(ips))
        if installed("ping"):
            cmd = ["ping", "-c", "4", host]
            code, out = run_command(cmd, 15)
            print("\n" + out)
        else:
            # TCP reachability fallback: DNS plus a common HTTPS connection.
            start = time.perf_counter()
            with socket.create_connection((host, 443), timeout=TIMEOUT):
                elapsed = (time.perf_counter() - start) * 1000
            result("TCP 443 reachable", f"{elapsed:.1f} ms", "green")
            print(paint("ICMP ping command is unavailable; TCP check used.", "yellow"))
    except Exception as e:
        result("Connectivity check", e, "red")
    pause()

def tcp_test():
    header()
    print(paint("SINGLE-PORT CONNECTIVITY TEST", "cyan", True)); line()
    host = ask("Host (your system / authorized target): ")
    port_s = ask("Port (1-65535): ")
    try:
        port = int(port_s)
        if not 1 <= port <= 65535:
            raise ValueError("Port must be between 1 and 65535.")
        safe_host(host)
        start = time.perf_counter()
        with socket.create_connection((host, port), timeout=TIMEOUT):
            ms = (time.perf_counter() - start) * 1000
        result("Result", "Connection successful", "green")
        result("Latency", f"{ms:.1f} ms")
    except Exception as e:
        result("Result", e, "red")
    pause()

def http_headers():
    header()
    print(paint("HTTP / HTTPS RESPONSE CHECK", "cyan", True)); line()
    url = ask("URL (include https://): ")
    if not url.startswith(("https://", "http://")):
        print(paint("Please enter a complete http:// or https:// URL.", "yellow"))
        pause(); return
    try:
        req = urllib.request.Request(url, method="HEAD",
                                    headers={"User-Agent": "SilverNetwork/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            result("Status", response.status, "green")
            result("Final URL", response.geturl())
            for k, v in response.headers.items():
                print(f"{paint(k, 'cyan')}: {v}")
    except urllib.error.HTTPError as e:
        result("HTTP status", e.code, "yellow")
        for k, v in e.headers.items():
            print(f"{paint(k, 'cyan')}: {v}")
    except Exception as e:
        result("Request failed", e, "red")
    pause()

def tls_check():
    header()
    print(paint("TLS CERTIFICATE CHECK", "cyan", True)); line()
    host = ask("Domain you own or are authorized to inspect: ")
    try:
        port_s = ask("Port [443]: ") or "443"
        port = int(port_s)
        if not 1 <= port <= 65535: raise ValueError("Invalid port.")
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                result("TLS version", ssock.version(), "green")
                result("Cipher", ssock.cipher()[0] if ssock.cipher() else "Unknown")
                result("Subject", cert.get("subject", "Unavailable"))
                result("Issuer", cert.get("issuer", "Unavailable"))
                result("Valid from", cert.get("notBefore", "Unavailable"))
                result("Valid until", cert.get("notAfter", "Unavailable"))
                result("Hostname verification", "Passed", "green")
    except Exception as e:
        result("TLS check failed", e, "red")
    pause()

def file_hash():
    header()
    print(paint("LOCAL FILE HASH", "cyan", True)); line()
    raw = ask("File path: ")
    path = Path(raw).expanduser()
    try:
        if not path.is_file(): raise FileNotFoundError("File not found.")
        sha = hashlib.sha256()
        size = 0
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024*1024), b""):
                sha.update(chunk); size += len(chunk)
        result("File", path)
        result("Size", f"{size} bytes")
        result("SHA-256", sha.hexdigest(), "green")
    except Exception as e:
        result("Hash failed", e, "red")
    pause()

def clamav_scan():
    header()
    print(paint("LOCAL FILE SCAN (CLAMAV)", "cyan", True)); line()
    if not installed("clamscan"):
        print(paint("ClamAV is not installed. This feature needs the optional clamscan engine.", "yellow"))
        print("Install it only if a compatible Termux package/repository provides it.")
        pause(); return
    raw = ask("File or directory path to scan: ")
    path = str(Path(raw).expanduser())
    if not os.path.exists(path):
        print(paint("Path does not exist.", "red")); pause(); return
    print("Scanning local files only...")
    code, out = run_command(["clamscan", "-r", "--", path], 180)
    print(out[:10000] or "(No output)")
    if code == 0: result("Scan", "No detections reported", "green")
    elif code == 1: result("Scan", "Detection(s) reported; review output carefully", "yellow")
    else: result("Scan status", "Could not complete; see output", "red")
    pause()

def ssh_manager():
    header()
    print(paint("SSH MANAGER", "cyan", True)); line()
    if not installed("ssh"):
        print(paint("OpenSSH client is not installed.", "yellow"))
        print("In Termux, install the optional package with: pkg install openssh")
        pause(); return
    host = ask("SSH username@host (your account/server): ")
    if not host or any(c in host for c in [";", "|", "&", "`", "$", " ", "\n"]):
        print(paint("Invalid input.", "red")); pause(); return
    port = ask("Port [22]: ") or "22"
    if not port.isdigit() or not 1 <= int(port) <= 65535:
        print(paint("Invalid port.", "red")); pause(); return
    print(paint("Starting SSH. Authentication is handled by OpenSSH.", "green"))
    try:
        os.execvp("ssh", ["ssh", "-p", port, host])
    except Exception as e:
        result("SSH launch failed", e, "red"); pause()

def optional_launcher(title, command, args=None, note=""):
    header()
    print(paint(title, "cyan", True)); line()
    if not installed(command):
        print(paint(f"{command} is not installed.", "yellow"))
        if note: print(note)
        pause(); return
    print(paint("This launches the installed program. Use only your own systems or an authorized lab.", "yellow"))
    if args is None:
        args = []
    try:
        subprocess.run([command] + args)
    except Exception as e:
        result("Launch failed", e, "red")
    pause()

def iperf_menu():
    header()
    print(paint("IPERF3 SPEED TEST", "cyan", True)); line()
    if not installed("iperf3"):
        print(paint("iperf3 engine not installed.", "yellow"))
        print("Optional Termux package: pkg install iperf3")
        pause(); return
    print("1. Client test against your own / authorized iperf3 server")
    print("2. Start a local iperf3 server")
    choice = ask("Choose: ")
    if choice == "1":
        host = ask("Server hostname/IP: ")
        try: safe_host(host)
        except Exception as e:
            result("Invalid host", e, "red"); pause(); return
        code, out = run_command(["iperf3", "-c", host, "-t", "5"], 15)
        print(out)
    elif choice == "2":
        print("Local server mode. Stop with Ctrl+C.")
        try: subprocess.run(["iperf3", "-s"])
        except Exception as e: result("Server error", e, "red")
    else:
        print("Cancelled.")
    pause()

def tor_status():
    header()
    print(paint("TOR / LOCAL SOCKS STATUS", "cyan", True)); line()
    result("Tor executable", "Available" if installed("tor") else "Not installed",
           "green" if installed("tor") else "yellow")
    for port in (9050, 9150):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                result(f"SOCKS localhost:{port}", "Listening", "green")
        except OSError:
            result(f"SOCKS localhost:{port}", "Not listening", "yellow")
    print("\nThis checks local availability only; it does not start Tor.")
    pause()

def dependency_dashboard():
    header()
    print(paint("OPTIONAL ENGINE STATUS", "cyan", True)); line()
    for name in OPTIONAL_COMMANDS:
        ok = installed(name)
        print(f"{paint('●', 'green' if ok else 'yellow')} {name:<20} "
              f"{paint('READY' if ok else 'NOT INSTALLED', 'green' if ok else 'yellow')}")
    print("\nThe core diagnostics use Python's standard library.")
    print("Optional engines are separate programs; the toolkit does not pretend to replace them.")
    pause()

def security_notes():
    header()
    print(paint("SECURITY AUDIT NOTES", "cyan", True)); line()
    print("• Run audits only on devices, files, servers and networks you own")
    print("  or have explicit permission to assess.")
    print("• Lynis and chkrootkit are primarily designed for Unix/Linux systems;")
    print("  they may not work on a non-rooted Android/Termux environment.")
    print("• A missing command is reported honestly; no fake scan results.")
    print("• This release does not perform exploitation, password attacks,")
    print("  network-wide scanning, or interception of third-party traffic.")
    pause()

def dashboard():
    while True:
        header()
        options = [
            ("01", "System information", system_info),
            ("02", "Network information", network_info),
            ("03", "DNS lookup", dns_lookup),
            ("04", "Connectivity check", ping_host),
            ("05", "Single-port connection test", tcp_test),
            ("06", "HTTP/HTTPS response headers", http_headers),
            ("07", "TLS certificate check", tls_check),
            ("08", "SSH manager", ssh_manager),
            ("09", "Iperf3 speed test", iperf_menu),
            ("10", "Tor / local SOCKS status", tor_status),
            ("11", "Local file SHA-256", file_hash),
            ("12", "ClamAV local file scan", clamav_scan),
            ("13", "Optional tool status", dependency_dashboard),
            ("14", "Security audit notes", security_notes),
        ]
        print(paint(" MAIN DASHBOARD", "silver", True))
        line()
        for num, label, _ in options:
            print(f" {paint('['+num+']', 'cyan', True)}  {label}")
        print(f" {paint('[00]', 'yellow', True)}  Exit")
        line()
        choice = ask("SILVER NETWORK > ")
        if choice == "00":
            print(paint("\nThank you for using SILVER NETWORK.", "cyan", True))
            break
        selected = next((fn for num, _, fn in options if num == choice), None)
        if selected:
            selected()
        else:
            print(paint("Invalid option.", "red"))
            time.sleep(0.8)

if __name__ == "__main__":
    try:
        dashboard()
    except KeyboardInterrupt:
        print("\n" + paint("SILVER NETWORK closed.", "cyan"))
