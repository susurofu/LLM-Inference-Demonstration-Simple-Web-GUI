import re
import subprocess
import time


def start_demo():
    # Start FastAPI / Uvicorn
    uvicorn_process = subprocess.Popen(
        [
            "uvicorn",
            "backend.main:app",
            "--reload",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    print("Starting Uvicorn...")

    # Give the server a moment to start
    time.sleep(2)

    # Start Cloudflare Quick Tunnel
    cloudflare_process = subprocess.Popen(
        [
            "cloudflared",
            "tunnel",
            "--url",
            "http://localhost:8000",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    print("Starting Cloudflare tunnel...")

    tunnel_url = None

    # Read cloudflared output until the URL appears
    for line in cloudflare_process.stdout:
        print(line, end="")

        match = re.search(
            r"https://[a-zA-Z0-9-]+\.trycloudflare\.com",
            line,
        )

        if match:
            tunnel_url = match.group(0)

            print("\n-----------------------------")
            print("Public URL:")
            print(tunnel_url)
            print("-----------------------------\n")

            break

    return tunnel_url, uvicorn_process, cloudflare_process


if __name__ == "__main__":
    url, uvicorn_process, cloudflare_process = start_demo()

    if url:
        print(f"Demo available at: {url}")

    try:
        # Keep the script alive
        uvicorn_process.wait()

    except KeyboardInterrupt:
        print("\nStopping server...")

        cloudflare_process.terminate()
        uvicorn_process.terminate()

        cloudflare_process.wait()
        uvicorn_process.wait()

        print("Stopped.")