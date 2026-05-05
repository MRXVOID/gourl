import argparse
import requests
import sys
import os
import io


try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

RED = "\033[91m"
RESET = "\033[0m"

banner = rf"""{RED}
  ________        ____ ___        .__   
 /  _____/  ____ |    |   \_______|  |  
/   \  ___ /  _ \|    |   /\_  __ \  |  
\    \_\  (  <_> )    |  /  |  | \/  |__
 \______  /\____/|______/   |__|  |____/
        \/ [ DEV : HackTuBin ] [ V1.1 ]       {RESET}
"""


class ProgressFile:
    def __init__(self, filepath):
        self.file = open(filepath, "rb")
        self.size = os.path.getsize(filepath)
        self.progress = tqdm(total=self.size, unit="B", unit_scale=True) if tqdm else None

    def read(self, chunk_size=1024):
        data = self.file.read(chunk_size)
        if self.progress and data:
            self.progress.update(len(data))
        return data

    def close(self):
        if self.progress:
            self.progress.close()
        self.file.close()


def get_qr_ascii(url):
    try:
        import qrcode
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)

        buf = io.StringIO()
        qr.print_ascii(out=buf, invert=True)
        return buf.getvalue().splitlines()

    except ImportError:
        return ["[!] install qrcode"]


def upload_file(filepath):
    if not os.path.isfile(filepath):
        return f"[ERROR] Not found: {filepath}"

    try:
        pf = ProgressFile(filepath)

        res = requests.post(
            "https://temp.sh/upload",
            files={"file": (os.path.basename(filepath), pf)},
            timeout=120
        )

        pf.close()

        if res.ok:
            return res.text.strip()
        else:
            return f"[ERROR] Upload failed ({res.status_code})"

    except requests.exceptions.RequestException as e:
        return f"[ERROR] Network: {e}"



def print_output(filename, url, show_qr):
    print(f"\nFILE: {filename}\n")

    print("URL:\n")
    print(url + "\n")

    if show_qr and not url.startswith("[ERROR]"):
        print("QR:\n")
        for line in get_qr_ascii(url):
            print(line)
        print()



def main():
    
    if len(sys.argv) == 1:
        print(banner)
        return

    if sys.argv[1] in ["-h", "--help"]:
        print(banner)

    parser = argparse.ArgumentParser(
        prog="gourl",
        description="Multi-file temp.sh uploader with progress + QR",
        add_help=False
    )

    parser.add_argument("-h", "--help", action="help", help="show this help message")

    parser.add_argument(
        "-f", "--file",
        nargs="+",
        required=True,
        help="file(s) to upload"
    )

    parser.add_argument("-u", "--url", action="store_true", help="show URL")
    parser.add_argument("-qr", "--qrcode", action="store_true", help="show QR code")

    args = parser.parse_args()

    for filepath in args.file:
        print(f"\nUploading: {filepath}\n")

        url = upload_file(filepath)

        if not args.url and not args.qrcode:
            print(url + "\n")
            continue

        print_output(os.path.basename(filepath), url, args.qrcode)


if __name__ == "__main__":
    main()
