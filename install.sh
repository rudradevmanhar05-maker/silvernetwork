#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"
echo "Installing SILVER NETWORK..."
pkg update -y
pkg install python -y
mkdir -p "$HOME/.local/bin"
cp silver_network.py "$HOME/.local/bin/silver-network"
chmod +x "$HOME/.local/bin/silver-network"
if ! grep -q 'HOME/.local/bin' "$HOME/.bashrc" 2>/dev/null; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi
echo
echo "Installed. Restart Termux or run:"
echo 'source ~/.bashrc && silver-network'
