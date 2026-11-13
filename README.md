# SILVER NETWORK

**A Termux-first networking and defensive security toolkit for Android.**

SILVER NETWORK brings practical network diagnostics and integrations for trusted command-line tools into one organized Python interface. It is designed to run inside **Termux on Android**, with a clean terminal dashboard and honest dependency checks.

## Short description

> One Termux dashboard for network diagnostics, secure connections, and authorized defensive checks.

## Features

### Built-in Python features
These use Python's standard library and do not need separate Python packages:

- System information
- Local network information
- DNS lookup
- Basic connectivity check
- Single-host, single-port TCP connectivity test
- HTTP/HTTPS response-header check
- TLS certificate validation and details
- Local file SHA-256 hashing

### Optional integrations
These require their own executable programs. SILVER NETWORK checks whether a program is installed before offering its integration.

- OpenSSH — SSH client
- autossh — persistent SSH connection helper
- Mosh — roaming remote terminal
- Netcat — basic TCP/UDP connection utility
- Socat — connection relay utility
- iperf3 — throughput testing with an authorized test server
- Proxychains — proxy-aware command launching
- Tor / Torsocks — Tor service and application proxying
- mitmproxy — inspect traffic in your own test lab
- Lynis — Unix/Linux security auditing
- chkrootkit — Unix/Linux rootkit checks
- ClamAV — local file scanning
- testssl.sh — TLS configuration testing

**Important:** An item in this list is not automatically installed or fully integrated just because it appears in the project plan. The current application reports missing executables and only launches integrations that are implemented and available. Some listed programs may not be packaged for Android/Termux, or may need a conventional Linux environment or root privileges.

## Requirements

- Android device
- Termux from a trusted source
- Python 3 in Termux
- Internet access only for features that need network access, package installation, or updates
- Optional command-line engines for their respective integrations

The core Python application uses only the Python standard library. See `requirements.txt`.

## Installation in Termux

### 1. Install Termux packages

Open Termux and run:

```bash
pkg update && pkg upgrade -y
pkg install python git -y
```

### 2. Download the project

If you have the project ZIP in Android's Downloads folder:

```bash
termux-setup-storage
cd ~/storage/downloads
```

Extract it using Python:

```bash
python -m zipfile -e SILVER_NETWORK_Termux_v1.0.zip .
cd silver_network
```

If you have cloned the project from a Git repository instead, enter the cloned project directory:

```bash
cd SILVER_NETWORK
```

### 3. Install Python requirements

```bash
python -m pip install -r requirements.txt
```

There are currently no third-party Python dependencies. This command is included so future Python dependencies can be installed consistently.

### 4. Install the launcher

```bash
mkdir -p "$HOME/.local/bin"
cp silver_network.py "$HOME/.local/bin/silver-network"
chmod +x "$HOME/.local/bin/silver-network"
```

Add the launcher directory to PATH:

```bash
grep -q 'HOME/.local/bin' "$HOME/.bashrc" || \
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
source "$HOME/.bashrc"
```

### 5. Start SILVER NETWORK

```bash
silver-network
```

You can also run it directly from the project folder:

```bash
python silver_network.py
```

## Optional Termux command-line tools

Install only the engines you need, and check package availability in your current Termux repository:

```bash
pkg search openssh
pkg search iperf3
pkg search tor
pkg search clamav
```

Commonly available packages may include:

```bash
pkg install openssh iperf3 tor netcat-openbsd socat -y
```

Package availability can vary by Termux repository, Android version, and device. Do not assume every program below can be installed directly with `pkg`.

For other tools, consult their official installation documentation and verify Android/Termux compatibility before installing. Avoid running random one-line installation scripts from untrusted sources.

## Updating

If installed from Git:

```bash
cd /path/to/SILVER_NETWORK
git pull
```

Then copy the updated launcher again if needed:

```bash
cp silver_network.py "$HOME/.local/bin/silver-network"
chmod +x "$HOME/.local/bin/silver-network"
```

## Troubleshooting

- **`silver-network: command not found`** — run `source ~/.bashrc`, then check `echo "$PATH"`.
- **Permission denied** — run `chmod +x "$HOME/.local/bin/silver-network"`.
- **Optional command missing** — install it from a trusted, Termux-compatible source; some tools may not support Android.
- **TLS check fails** — verify the hostname, port, internet connection, device date/time, and certificate trust.
- **A security scanner does not run** — some Linux auditing utilities require privileges or system interfaces unavailable to ordinary Termux apps.

## Responsible use

Use SILVER NETWORK only on devices, files, servers, and networks that you own or have explicit permission to assess. Do not use it to access accounts or systems without permission, intercept other people's traffic, or disrupt networks.

Security tools can produce incomplete or misleading results in Android's restricted app environment. Treat results as diagnostic information, not a guarantee that a system is secure.

## Project status

This is an actively developed project. Check the feature implementation and dependency status in the application before relying on any optional integration. Contributions and bug reports should include the Termux version, Android version, command used, and error output with secrets removed.

## License

This project is distributed under the MIT License. See [LICENSE](LICENSE).
