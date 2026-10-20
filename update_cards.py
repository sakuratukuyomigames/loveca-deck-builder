
import re
import json
from urllib.request import Request, urlopen

URL = "https://llofficial-cardgame.com/cardlist/"

def main():
    print("Checking official Loveca card list...")

    request = Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urlopen(request, timeout=20) as response:
        html = response.read().decode("utf-8", errors="replace")
        print("HTTP status:", response.status)
        print("Page size:", len(html))

    links = re.findall(
        r"""(?:href|src)=["']([^"']+)["']""",
        html
    )

    candidates = [
        link
        for link in links
        if any(
            word in link.lower()
            for word in ("card", "api", "json", "search")
        )
    ]

    print(
        "Candidate links:",
        json.dumps(candidates[:30], ensure_ascii=False)
    )

if __name__ == "__main__":
    main()
