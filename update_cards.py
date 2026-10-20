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
            print("Page preview:", html[:300])
    except (HTTPError, URLError, TimeoutError) as error:
        print("Connection failed:", error)
        raise

if __name__ == "__main__":
    main()
