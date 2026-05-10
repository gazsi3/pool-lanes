"""
Test pagination of /fina/competitions and filter for relevant competitions.
Run: docker compose --profile scraper run --rm scraper python -m scraper.diagnose
"""
import json
import requests

API  = "https://api.worldaquatics.com"
HDRS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://www.worldaquatics.com",
    "Referer": "https://www.worldaquatics.com/",
}

SEP = "\n" + "="*60 + "\n"

def get_json(url):
    r = requests.get(url, headers=HDRS, timeout=30)
    if r.status_code == 200:
        return r.json()
    print(f"  FAILED {r.status_code}: {url}")
    return None

# ── Test pageSize=100 ─────────────────────────────────────────────────────────
print(SEP + "Test pageSize=100 — how many competitions per page?")
data = get_json(f"{API}/fina/competitions?pageSize=100")
if data:
    pi = data["pageInfo"]
    print(f"  numEntries={pi['numEntries']}  numPages={pi['numPages']}  pageSize={pi['pageSize']}")

# ── Test pageSize=1000 ────────────────────────────────────────────────────────
print(SEP + "Test pageSize=1000")
data2 = get_json(f"{API}/fina/competitions?pageSize=1000")
if data2:
    pi2 = data2["pageInfo"]
    print(f"  numEntries={pi2['numEntries']}  numPages={pi2['numPages']}  pageSize={pi2['pageSize']}")

# ── Get first page and show competition names/IDs to understand structure ─────
print(SEP + "First 50 competitions — names, IDs, dates")
data3 = get_json(f"{API}/fina/competitions?pageSize=50&page=0")
if data3:
    for comp in data3["content"]:
        print(f"  id={comp['id']:5d}  {comp['dateFrom'][:10]}  {comp['name'][:70]}")

# ── Filter by keywords in name to find Olympics/Worlds/Euros ─────────────────
print(SEP + "Search for relevant competitions across first 500 (page 0-9)")
TARGET_KEYWORDS = ["olympic", "world championship", "world aquatics", "european championship",
                   "world cup"]
relevant = []
for pg in range(10):  # 10 pages * 50 = 500 competitions
    d = get_json(f"{API}/fina/competitions?pageSize=50&page={pg}")
    if not d:
        break
    for comp in d["content"]:
        name_lower = comp["name"].lower()
        if any(kw in name_lower for kw in TARGET_KEYWORDS):
            date = comp.get("dateFrom", "")[:10]
            if date >= "2000-01-01":
                relevant.append({
                    "id": comp["id"],
                    "name": comp["name"],
                    "date": date,
                    "city": comp.get("location", {}).get("city", ""),
                    "providerId": comp.get("providerId", "")
                })

print(f"\nRelevant competitions found in first 500: {len(relevant)}")
for c in relevant:
    print(f"  id={c['id']:5d}  {c['date']}  {c['city'][:20]:20s}  {c['name'][:60]}")
