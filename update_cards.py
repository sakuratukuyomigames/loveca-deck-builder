
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
    print("HTML API PATHS:", sorted(set(re.findall(r'[^"\'\s<>]*card-list-user[^"\'\s<>]*', html))))
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
    print("Checking card list API TEST...")

    api_url = "https://llofficial-cardgame.com/manage/card-list-user/list?page=2"
    api_request = Request(
        api_url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    try:
        with urlopen(api_request, timeout=20) as response:
            data = response.read()
            print("API status:", response.status)
            print("Content-Type:", response.headers.get("Content-Type"))
            print("API response size:", len(data))
            print("API preview:", data[:500].decode("utf-8", errors="replace"))
            print("JSON KEYS:", list(json.loads(data).keys()))
            print("CARD FIELDS:", list(json.loads(data)["items"][0].keys()))
            all_cards = []
            for page in range(1, 180):
            page_url = f"https://llofficial-cardgame.com/manage/card-list-user/list?page={page}"
            page_request = Request(page_url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(page_request, timeout=20) as page_response:
                page_data = json.load(page_response)
            all_cards.extend(page_data["items"])
            print(f"Page {page}/179: {len(all_cards)} cards")

        print("TOTAL CARDS FETCHED:", len(all_cards))
        print("TOTAL PAGES:", (json.loads(data)["total"] + json.loads(data)["per_page"] - 1) // json.loads(data)["per_page"])
        print("FIRST CARD:", json.dumps(json.loads(data)["items"][0], ensure_ascii=False))
        print("CARD NUMBER FOUND:", "PL!-bp3-019-SRL" in data.decode("utf-8", errors="replace"))
    except Exception as error:
        print("API check error:", type(error).__name__, str(error))
if __name__ == "__main__":
    main()