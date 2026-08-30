import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path


def _install_cloudflared_linux():

    if shutil.which("cloudflared"):
        print("cloudflared is already installed.")
        return

    architecture = platform.machine()

    if architecture in ("x86_64", "amd64"):
        package_arch = "amd64"

    elif architecture in ("aarch64", "arm64"):
        package_arch = "arm64"

    else:
        print(
            f"Unsupported architecture: {architecture}"
        )
        sys.exit(1)

    url = (
        "https://github.com/cloudflare/cloudflared/"
        "releases/latest/download/"
        f"cloudflared-linux-{package_arch}.deb"
    )

    package_path = Path("/tmp/cloudflared.deb")

    print("Downloading cloudflared...")
    print(url)

    urllib.request.urlretrieve(
        url,
        package_path
    )

    print("Installing cloudflared...")

    subprocess.run(
        [
            "sudo",
            "dpkg",
            "-i",
            str(package_path)
        ],
        check=True
    )

    package_path.unlink(
        missing_ok=True
    )

    print("cloudflared installed successfully.")


def _start_tunnel_linux():

    print(
        "Starting tunnel for "
        "http://localhost:8000"
    )

    subprocess.run([
        "cloudflared",
        "tunnel",
        "--url",
        "http://localhost:8000"
    ])

