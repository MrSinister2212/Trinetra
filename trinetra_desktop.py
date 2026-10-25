import sys
import os
import time
import socket
import threading
import uvicorn
import webview
import httpx

# Add backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

def find_available_port(default_port: int = 8000) -> int:
    """Finds an open port starting from default_port"""
    port = default_port
    while port < 9000:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
        port += 1
    return default_port

def start_backend_server(port: int):
    """Runs FastAPI/Uvicorn in a daemon thread"""
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

def wait_for_server(port: int, timeout: float = 10.0) -> bool:
    """Polls the backend /health endpoint until active"""
    start_time = time.time()
    url = f"http://127.0.0.1:{port}/health"
    while time.time() - start_time < timeout:
        try:
            r = httpx.get(url, timeout=1.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.2)
    return False

def main():
    print("[TRINETRA Desktop] Initializing local OSINT engine...")
    port = find_available_port(8000)

    # Launch local backend server
    server_thread = threading.Thread(target=start_backend_server, args=(port,), daemon=True)
    server_thread.start()

    # Wait for initialization
    if not wait_for_server(port):
        print("[TRINETRA Desktop] Error: Local engine failed to start.")
        sys.exit(1)

    print(f"[TRINETRA Desktop] Engine ready at http://127.0.0.1:{port}. Launching native window...")

    # Create native desktop window
    window = webview.create_window(
        title="TRINETRA — Modular OSINT & Footprint Intelligence Platform",
        url=f"http://127.0.0.1:{port}",
        width=1340,
        height=880,
        min_size=(1020, 680),
        background_color="#080d1a"
    )

    # Start PyWebView GUI loop (uses native Microsoft Edge WebView2 on Windows)
    webview.start(debug=False)
    print("[TRINETRA Desktop] Session closed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
