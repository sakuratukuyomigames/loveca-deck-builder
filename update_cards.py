import re
import json


from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

URL = "https://llofficial-cardgame.com/cardlist/"

def main():
    print("Checking official Loveca card list...")

    request = Request(
        URL,
        headers={"User-Agent": "LovecaDeckBuilder/0.1"}
    )

    try:
        with urlopen(request, timeout=20) as response:
            html = response.read().decode("utf-8", errors="replace")
            print("HTTP status:", response.status)
            print("Page size:", len(html))
            print("Contains cardlist:", "cardlist" in html.lower())
            print("Page preview:", html[:300])            links = re.findall(r'(?:href|src)=["\']([^"\']+)["\']', html)
                        links = re.findall(r'(?:href|src)=["\']([^"\']+)["\']', html)candidates = [
                            candidates = [link for link in links
                if any(word in link.lower() for word in
                       ("card", "api", "json", "search"))
            ]
            print("Candidate links:", json.dumps(candidates[:30], ensure_ascii=False))

    except (HTTPError, URLError, TimeoutError) as error:
        print("Connection failed:", error)
        raise

if __name__ == "__main__":
    main()
