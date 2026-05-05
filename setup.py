import os
import sys
import subprocess
from pathlib import Path
import webbrowser

def detect_os():
    if "TERMUX_VERSION" in os.environ:
        return "termux"
    elif os.name == "nt":
        return "windows"
    else:
        return "linux"


def install_requirements():
    print("[*] Installing dependencies (user-level)...\n")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "--user", "-r", "requirements.txt"
        ])
    except subprocess.CalledProcessError:
        print("[!] Trying fallback (--break-system-packages)...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "--break-system-packages",
            "-r", "requirements.txt"
        ])


def create_shortcut():
    script_path = Path(__file__).resolve().parent / "gourl.py"

    if "TERMUX_VERSION" in os.environ:
        target = "/data/data/com.termux/files/usr/bin/gourl"
    else:
        target = "/usr/local/bin/gourl"

    print(f"[*] Creating global command at: {target}")

    try:
        with open(target, "w") as f:
            f.write(f"""#!/usr/bin/env bash
python3 "{script_path}" "$@"
""")

        os.chmod(target, 0o755)
        print("[+] Global command 'gourl' ready!\n")

    except PermissionError:
        print("[ERROR] Permission denied → try with sudo")
        sys.exit(1)



def open_instagram():
    url = "https://www.instagram.com/hacktubin/"
    print("[*] Opening Instagram page...\n")
    try:
        webbrowser.open(url)
    except Exception:
        print("[!] Could not open browser")

def main():
    os_type = detect_os()

    print(f"[+] OS detected: {os_type}\n")

    install_requirements()

    if os_type in ["linux", "termux"]:
        create_shortcut()
    else:
        print("[*] Windows → only dependencies installed (no global cmd)\n")

    print("[✓] Setup complete!")
    print("Usage: gourl -f test.txt -u -qr\n")
    open_instagram()


if __name__ == "__main__":
    main()