BASE_URL = "https://www.swimrankings.net"
RATE_LIMIT_SECONDS = 3.0
MAX_RETRIES = 3
RETRY_BACKOFF = 8
CLOUDFLARE_WAIT_SECONDS = 6

LANE_SEED_ORDER_8: dict[int, int] = {4: 1, 5: 2, 3: 3, 6: 4, 2: 5, 7: 6, 1: 7, 8: 8}
LANE_SEED_ORDER_10: dict[int, int] = {5: 1, 6: 2, 4: 3, 7: 4, 3: 5, 8: 6, 2: 7, 9: 8, 1: 9, 10: 10}

# meet_type values observed on swimrankings
# 1 = Olympics, 2 = World Championships LCM, 3 = World Championships SCM,
# 4 = European Championships — these must be confirmed on first scrape run
COMPETITION_CONFIGS = [
    {
        "competition": "Olympics",
        "pool": "LCM",
        "meet_type": 1,
        "years": list(range(2000, 2025, 4)),
    },
    {
        "competition": "World Championships",
        "pool": "LCM",
        "meet_type": 2,
        "years": [2001, 2003, 2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2022, 2023, 2024],
    },
    {
        "competition": "World Championships",
        "pool": "SCM",
        "meet_type": 3,
        "years": [2000, 2002, 2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018, 2021, 2022, 2024],
    },
    {
        "competition": "European Championships",
        "pool": "LCM",
        "meet_type": 4,
        "years": list(range(2000, 2025, 2)),
    },
]

RELAY_EVENTS = {
    "4x100m Freestyle Relay",
    "4x200m Freestyle Relay",
    "4x100m Medley Relay",
    "Mixed 4x100m Freestyle Relay",
    "Mixed 4x100m Medley Relay",
}

INDIVIDUAL_EVENTS = [
    "50m Freestyle", "100m Freestyle", "200m Freestyle", "400m Freestyle",
    "800m Freestyle", "1500m Freestyle",
    "50m Backstroke", "100m Backstroke", "200m Backstroke",
    "50m Breaststroke", "100m Breaststroke", "200m Breaststroke",
    "50m Butterfly", "100m Butterfly", "200m Butterfly",
    "200m Individual Medley", "400m Individual Medley",
]

MIN_VALID_ENTRIES = 4
