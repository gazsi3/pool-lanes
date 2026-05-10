API_BASE      = "https://api.worldaquatics.com/fina"
RATE_LIMIT    = 1.5   # seconds between requests
MAX_RETRIES   = 3
RETRY_BACKOFF = 5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://www.worldaquatics.com",
    "Referer": "https://www.worldaquatics.com/",
}

# Competition name substrings → (competition label, pool type)
# Checked against lowercase competition name from /fina/competitions
COMPETITION_FILTERS = [
    # (substring_in_name, label, pool)
    ("olympic games",              "Olympics",               "LCM"),
    ("world aquatics championships","World Championships",   "LCM"),  # 2022+
    ("fina world championships",   "World Championships",   "LCM"),   # old name
    ("world championships 2022",   "World Championships",   "LCM"),   # Budapest 2022 uses this
    ("world aquatics swimming championships (25m)", "World Championships SCM", "SCM"),
    ("fina world swimming championships (25m)",     "World Championships SCM", "SCM"),
    ("world swimming championships (25m)",          "World Championships SCM", "SCM"),
    ("european aquatics championships",             "European Championships", "LCM"),
    ("european swimming championships",             "European Championships", "LCM"),
    ("len european aquatics championships",         "European Championships", "LCM"),
]

# Only keep competitions from this date range
DATE_FROM = "2000-01-01"
DATE_TO   = "2024-12-31"

LANE_SEED_ORDER_8: dict[int, int]  = {4: 1, 5: 2, 3: 3, 6: 4, 2: 5, 7: 6, 1: 7, 8: 8}
LANE_SEED_ORDER_10: dict[int, int] = {5: 1, 6: 2, 4: 3, 7: 4, 3: 5, 8: 6, 2: 7, 9: 8, 1: 9, 10: 10}

# Minimum swimmers with valid lanes to treat a heat as a scorable final
MIN_VALID_ENTRIES = 4

# Sport code for swimming events
SWIM_SPORT_CODE = "SW"
