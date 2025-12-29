import subprocess
import time
import sys
import os
import urllib.request
import urllib.error
import signal

BACKEND_URL = "http://localhost:3000/health"
BACKEND_DIR = "backend"
FRONTEND_SCRIPT = "src/interface/app.py"


def is_port_in_use(port):
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def kill_port_process(port):
    print(f"⚠️ Port {port} is in use. Attempting to free it...")
    # Windows specific
    if sys.platform == "win32":
        subprocess.run(
            f"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :{port}') do taskkill /f /pid %a",
            shell=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )


def start_backend():
    print("\n🦀 [1/2] Starting Rust Backend (cargo run)...")
    # Check if port 3000 is occupied
    if is_port_in_use(3000):
        kill_port_process(3000)

    # We use shell=False to better control the process, but on Windows cargo might need shell=True if slightly misconfigured.
    # Usually standard install works without shell=True.
    try:
        # Popen allows us to run it without blocking
        proc = subprocess.Popen(
            ["cargo", "run", "--quiet"],
            cwd=BACKEND_DIR,
            # We don't pipe stdout/stderr so the user can see Rust logs directly in the console
            # If you want to hide them, use stdout=subprocess.DEVNULL
        )
        return proc
    except FileNotFoundError:
        print("❌ 'cargo' not found. Please install Rust.")
        sys.exit(1)


def wait_for_backend(timeout=300):
    print("⏳ Waiting for Backend to be ready...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(BACKEND_URL) as response:
                if response.getcode() == 200:
                    print(f"✅ Backend is ready at {BACKEND_URL}!")
                    return True
        except urllib.error.URLError:
            pass  # Connection refused means not ready yet
        except Exception as e:
            print(f"Warning: {e}")

        time.sleep(1)
        # Print a dot every second to show life
        sys.stdout.write(".")
        sys.stdout.flush()

    print("\n❌ Backend failed to start within timeout.")
    return False


def start_frontend():
    print("\n🐍 [2/2] Starting Streamlit Frontend...")
    # Use the current python interpreter
    cmd = [sys.executable, "-m", "streamlit", "run", FRONTEND_SCRIPT]

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        pass


def sync_env():
    """Sync root .env to backend/.env to ensure API key availability."""
    root_env = ".env"
    backend_env = os.path.join(BACKEND_DIR, ".env")

    if os.path.exists(root_env):
        try:
            # Read logic that handles encoding could be better, but simple copy is usually enough.
            # However, shutil.copy helps.
            import shutil

            shutil.copy(root_env, backend_env)
            print("✅ Synced .env to backend/.env")
        except Exception as e:
            print(f"⚠️ Failed to sync .env: {e}")
    else:
        print("ℹ️ No root .env found. Ensure backend/.env exists or env vars are set.")


def main():
    print("🚀 Launching Law Scraping System...")

    sync_env()
    backend_proc = start_backend()

    try:
        if wait_for_backend():
            # Backend is up, launch frontend (this will block until frontend is closed)
            start_frontend()
        else:
            print("Failed to start system.")
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    finally:
        if backend_proc:
            print("🛑 Terminating backend...")
            backend_proc.terminate()
            try:
                backend_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_proc.kill()
            print("Backend stopped.")


if __name__ == "__main__":
    main()
