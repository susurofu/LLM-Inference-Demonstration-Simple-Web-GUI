import shutil
import subprocess
import sys

def _install_cloudflared_mac():
    # Check whether cloudflared already exists
    if shutil.which("cloudflared"):
        print("cloudflared is already installed.")
        return

    # Check whether Homebrew exists
    if not shutil.which("brew"):
        print("Homebrew is not installed.")
        print("Install Homebrew first, then run this script again.")
        sys.exit(1)

    print("Installing cloudflared...")

    subprocess.run(
        ["brew", "install", "cloudflared"],
        check=True
    )

    print("cloudflared installed successfully.")
