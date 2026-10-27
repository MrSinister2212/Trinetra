import os
import sys
import subprocess
import shutil

def build_exe():
    print("===================================================")
    print("  TRINETRA - Standalone Executable Packaging (.exe)")
    print("===================================================")

    root_dir = os.path.dirname(os.path.abspath(__file__))
    dist_ui = os.path.join(root_dir, "frontend", "dist")

    # Step 1: Ensure frontend is built
    if not os.path.exists(dist_ui):
        print("[Build] Compiling React frontend...")
        frontend_dir = os.path.join(root_dir, "frontend")
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, shell=True, check=True)

    # Step 2: Ensure sites.json exists
    sites_json = os.path.join(root_dir, "backend", "app", "modules", "data", "sites.json")
    if not os.path.exists(sites_json):
        print("[Build] Generating 500+ site definitions...")
        subprocess.run([sys.executable, os.path.join("backend", "generate_sites.py")], check=True)

    # Step 3: Run PyInstaller
    print("[Build] Invoking PyInstaller to freeze TRINETRA desktop app...")
    
    # Path separators for Windows: source;destination
    datas = [
        f"{os.path.join('backend', 'app', 'modules', 'data', 'sites.json')};app/modules/data",
        f"{os.path.join('backend', 'app', 'modules', 'data', 'darkweb_blocklist.json')};app/modules/data",
        f"{os.path.join('backend', 'app', 'reporting', 'templates')};app/reporting/templates",
        f"{os.path.join('frontend', 'dist')};dist",
    ]

    hidden_imports = [
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespans",
        "uvicorn.lifespans.on",
        "aiosqlite",
        "greenlet",
        "greenlet._greenlet",
        "sqlalchemy.dialects.sqlite",
        "xhtml2pdf",
        "reportlab",
        "docx",
        "phonenumbers",
        "PIL",
        "networkx",
        "fastapi",
        "starlette",
        "dns.resolver",
        "webview",
        "webview.platforms.winforms",
        "clr",
        "pythonnet",
        "jose",
        "passlib",
        "bcrypt",
        "app.routes.ai_routes",
        "app.ai.copilot",
        "app.ai.llm_engine",
        "app.modules.location",
    ]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed", # No black console window
        "--name", "Trinetra",
        "--paths", os.path.join(root_dir, "backend"),
    ]

    for d in datas:
        cmd.extend(["--add-data", d])

    for hi in hidden_imports:
        cmd.extend(["--hidden-import", hi])

    cmd.append("trinetra_desktop.py")

    subprocess.run(cmd, check=True)
    print("\n[SUCCESS] Standalone Desktop Package created at: dist/Trinetra/Trinetra.exe")

if __name__ == "__main__":
    build_exe()
