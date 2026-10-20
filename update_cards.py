
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
    for link in links:
        if "bushiroad-card-manager" in link and ".js" in link:
            print("CARD SCRIPT:", link)
            
    print("Checking card list JavaScript...")

    js_url = (
        "https://llofficial-cardgame.com/wordpress/"
        "wp-content/plugins/bushiroad-card-manager/"
        "assets/sys.cardlist.js"
    )

    js_request = Request(
        js_url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urlopen(js_request, timeout=20) as response:
        js = response.read().decode("utf-8", errors="replace")

    print("JS size:", len(js))

    for word in ("ajax", "api", "fetch", "admin-ajax", "wp-json"):
        print(word, "found:", word in js.lower())

    print("JS preview:", js[:1000])

    for word in ("endpoints", "card_list", "cardlist"):
        pos = js.lower().find(word.lower())
        if pos >= 0:
            print("FOUND", word, js[max(0, pos-150):pos+350])
    for match in re.finditer(r".{0,120}endpoints.{0,300}", js, re.I):
        print("ENDPOINT DETAIL:", match.group(0)[:420])

if __name__ == "__main__":
    main()