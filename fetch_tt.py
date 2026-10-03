import re, json, sys, urllib.request

ROUTES = {
    "zhongli_hsinchu": (1100, 1210),
    "hsinchu_taichung": (1210, 3300),
    "taichung_hsinchu": (3300, 1210),
    "hsinchu_zhongli": (1210, 1100),
}

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

def norm(s):
    # payload uses mojibake-safe raw utf8 already; ensure str
    return s

def extract(html):
    arr = json.loads(re.search(r'id="__NUXT_DATA__">(.*?)</script>', html, re.S).group(1))
    def d(i):
        v = arr[i]
        if isinstance(v, int) and isinstance(arr[v], dict):
            v = arr[v]
        return v
    root = arr[4]
    for key in ("timetable", "timetableReturn", "timetable_back"):
        pass
    # find any list of dicts that contain trainNo
    out = []
    def walk(node, depth=0):
        if depth > 6:
            return
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, depth + 1)
        elif isinstance(node, list):
            if node and all(isinstance(x, int) for x in node[:5]):
                recs = [arr[x] for x in node if isinstance(arr[x], dict) and "trainNo" in arr[x]]
                if recs:
                    for r in recs:
                        out.append({
                            "no": arr[r["trainNo"]],
                            "type": arr[r["trainType"]] if isinstance(r["trainType"], int) else r["trainType"],
                            "dep": arr[r["departure"]] if isinstance(r["departure"], int) else r["departure"],
                            "arr": arr[r["arrive"]] if isinstance(r["arrive"], int) else r["arrive"],
                            "dur": arr[r["travelTime"]] if isinstance(r["travelTime"], int) else r["travelTime"],
                            "price": arr[r["price"]] if isinstance(r["price"], int) else r["price"],
                        })
                    return
            for v in node:
                walk(v, depth + 1)
        elif isinstance(node, int):
            walk(arr[node], depth + 1)
    walk(root)
    return out

result = {}
for name, (a, b) in ROUTES.items():
    url = f"https://timetables.tw/routes/{a}/{b}"
    try:
        rows = extract(get(url))
    except Exception as e:
        rows = [{"error": str(e)}]
    result[name] = rows
    print(name, len(rows), file=sys.stderr)

with open("raw_timetables.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print("done")
