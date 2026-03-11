import json
import sys
from pathlib import Path

import requests


def main() -> int:
    pdf = Path(
        r"C:\Users\ASUS\Documents\Code\projects\project-allocator\src\demo_docs\projects\project1.pdf"
    )
    url = "http://127.0.0.1:8000/admin/upload-project"

    if not pdf.exists():
        print(f"PDF not found: {pdf}", file=sys.stderr)
        return 2

    with pdf.open("rb") as f:
        r = requests.post(url, files={"file": (pdf.name, f, "application/pdf")}, timeout=300)

    print("status:", r.status_code)
    try:
        data = r.json()
        print(json.dumps(data, indent=2))
    except Exception:
        print(r.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

