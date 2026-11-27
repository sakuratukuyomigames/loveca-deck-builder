from urllib.parse import urlencode
import re
import json
import os
from urllib.request import Request, urlopen
import time
from urllib.error import HTTPError
URL = "https://llofficial-cardgame.com/cardlist/"
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def main():
    print("Checking official Loveca card list...")

    request = Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    for attempt in range(3):
        try:
            response = urlopen(request, timeout=20)
            break
        except HTTPError as error:
            if error.code != 503 or attempt == 2:
                raise
            print("HTTP 503: 30秒待って再試行します")
            time.sleep(30)
    with response:
    
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
    for match in re.finditer(r"buildDetailPageUrl", js):
        print("BUILD URL CHECK:", js[max(0, match.start()-200):match.start()+1000])

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
            total_pages = (json.loads(data)["total"] + 14) // 15
            all_cards = []
            for page in range(1, total_pages + 1):
                page_url = f"https://llofficial-cardgame.com/manage/card-list-user/list?page={page}"
                page_request = Request(page_url, headers={"User-Agent": "Mozilla/5.0"})
                with urlopen(page_request, timeout=20) as page_response:
                    page_data = json.load(page_response)
                    all_cards.extend(page_data["items"])
                    print(f"Page {page}/{total_pages}: {len(all_cards)} cards")

            print("TOTAL CARDS FETCHED:", len(all_cards))
            for card in all_cards[:5]:
                print("RAW CARD CHECK:", json.dumps(card, ensure_ascii=False))
            def fetch_unit_ids(work_title, unit_name):
                unit_ids = set()
                unit_page = 1
                while True:
                    unit_url = "https://llofficial-cardgame.com/manage/card-list-user/list?" + urlencode({
                        "page": unit_page,
                        "work_title": work_title,
                        "unit_name": unit_name
                    })
                    unit_request = Request(
                        unit_url,
                        headers={"User-Agent": "Mozilla/5.0"}
                    )
                    with urlopen(unit_request, timeout=20) as unit_response:
                        unit_data = json.load(unit_response)
                    for card in unit_data["items"]:
                        unit_ids.add(card["id"])
                    if unit_page * unit_data["per_page"] >= unit_data["total"]:
                        break
                    unit_page += 1
                    time.sleep(0.3)
                return unit_ids

        units = [
            ("title_1", "Printemps"),
            ("title_1", "lily white"),
            ("title_1", "BiBi"),
            ("title_2", "CYaRon!"),
            ("title_2", "AZALEA"),
            ("title_2", "Guilty Kiss"),
            ("title_3", "DiverDiva"),
            ("title_3", "A・ZU・NA"),
            ("title_3", "QU4RTZ"),
            ("title_3", "R3BIRTH"),
        ]

        unit_map = {}

        for work_title, unit_name in units:
            ids = fetch_unit_ids(work_title, unit_name)
            unit_map[unit_name] = ids
            print(unit_name, "IDS:", len(ids))

        converted_cards = []
        for sample in all_cards:
            groups = [
                name for name, ids in unit_map.items()
                if sample["id"] in ids
            ]
            converted = {
                    "groups": groups,
                "card_number": sample.get("card_number"),
                "name": sample.get("card_name"),
                "card_type": sample.get("card_kind"),
                "rarity": sample.get("rare"),
                "image_url": sample.get("picture"),
                "colors": {"raw": sample.get("color")},
                "hearts": {"raw": sample.get("heart")},
                "blade_hearts": {"raw": sample.get("attack")},
                "blade": int(sample["attack"]) if str(sample.get("attack", "")).isdigit() else None,
                "effect_text": sample.get("text"),
                "cost": int(sample["cost"]) if str(sample.get("cost", "")).isdigit() else None,
                 }
            converted_cards.append(converted)
        print("CONVERTED CARD:", json.dumps(converted, ensure_ascii=False))
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabaseの接続設定がありません")

        save_url = SUPABASE_URL.rstrip("/") + "/rest/v1/cards?on_conflict=card_number"
        for i in range(0, len(converted_cards), 100):
            save_request = Request(
            save_url,
         data=json.dumps(converted_cards[i:i+100], ensure_ascii=False).encode("utf-8"),
            headers={
            "apikey": SUPABASE_KEY,
            "Authorization": "Bearer " + SUPABASE_KEY,
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation",
            },
            method="POST",
            )
            with urlopen(save_request, timeout=30) as save_response:
                print("SUPABASE SAVE STATUS:", save_response.status)
                print("SUPABASE SAVE RESULT:", save_response.read().decode("utf-8")[:500])
                print("TOTAL PAGES:", (json.loads(data)["total"] + json.loads(data)["per_page"] - 1) // json.loads(data)["per_page"])
                print("FIRST CARD:", json.dumps(json.loads(data)["items"][0], ensure_ascii=False))
                print("CARD NUMBER FOUND:", "PL!-bp3-019-SRL" in data.decode("utf-8", errors="replace"))
    except Exception as error:
        if hasattr(error, "read"):
            print("ERROR DETAILS:", error.read().decode("utf-8"))
        print("API check error:", type(error).__name__, str(error))
if __name__ == "__main__":
    main()