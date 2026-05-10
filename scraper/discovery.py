"""
Discover meet IDs and event IDs from swimrankings.net.

URL patterns (verified via browser inspection):
  Meet list:   /index.php?page=meetSelect&selectPage=MEET_LIST&meetType=<N>&startYear=<Y>&endYear=<Y>
  Meet detail: /index.php?page=meetDetail&meetId=<ID>
  Event result:/index.php?page=eventDetail&eventId=<ID>

NOTE: meetType values and exact URL parameters must be confirmed on first scrape run.
The constants in config.py should be updated if swimrankings uses different codes.
"""

import logging
import re
from bs4 import BeautifulSoup

from .config import BASE_URL, COMPETITION_CONFIGS, RELAY_EVENTS, INDIVIDUAL_EVENTS
from .utils import BrowserContext, fetch_page

log = logging.getLogger(__name__)


def discover_all_meets(ctx: BrowserContext) -> list[dict]:
    """
    Returns list of meet metadata dicts:
      {meet_id, competition, year, pool, location}
    """
    meets = []
    for cfg in COMPETITION_CONFIGS:
        for year in cfg["years"]:
            found = _discover_meets_for(ctx, cfg, year)
            meets.extend(found)
            log.info("Discovered %d meets for %s %d", len(found), cfg["competition"], year)
    return meets


def _discover_meets_for(ctx: BrowserContext, cfg: dict, year: int) -> list[dict]:
    url = f"{BASE_URL}/index.php"
    params = {
        "page": "meetSelect",
        "selectPage": "MEET_LIST",
        "meetType": cfg["meet_type"],
        "startYear": year,
        "endYear": year,
    }
    html = fetch_page(ctx, url, params)
    soup = BeautifulSoup(html, "lxml")
    return _parse_meet_list(soup, cfg["competition"], cfg["pool"], year)


def _parse_meet_list(
    soup: BeautifulSoup, competition: str, pool: str, year: int
) -> list[dict]:
    meets = []
    # Meet list rows: look for links containing meetId= in href
    for a_tag in soup.find_all("a", href=re.compile(r"meetId=(\d+)")):
        meet_id_match = re.search(r"meetId=(\d+)", a_tag["href"])
        if not meet_id_match:
            continue
        meet_id = meet_id_match.group(1)
        # Location is usually the link text or the parent cell
        location = a_tag.get_text(strip=True)
        meets.append(
            {
                "meet_id": meet_id,
                "competition": competition,
                "pool": pool,
                "year": year,
                "location": location,
            }
        )
    return meets


def discover_events(ctx: BrowserContext, meet: dict) -> list[dict]:
    """
    For a given meet, return list of final-round event metadata:
      {event_id, event, gender, is_relay, round}
    """
    url = f"{BASE_URL}/index.php"
    params = {"page": "meetDetail", "meetId": meet["meet_id"]}
    html = fetch_page(ctx, url, params)
    soup = BeautifulSoup(html, "lxml")
    return _parse_event_list(soup)


def _parse_event_list(soup: BeautifulSoup) -> list[dict]:
    events = []
    known_events = set(INDIVIDUAL_EVENTS) | RELAY_EVENTS

    for a_tag in soup.find_all("a", href=re.compile(r"eventId=(\d+)")):
        event_id_match = re.search(r"eventId=(\d+)", a_tag["href"])
        if not event_id_match:
            continue
        event_id = event_id_match.group(1)
        label = a_tag.get_text(strip=True)

        gender, event_name, round_name = _parse_event_label(label)
        if gender is None or round_name != "Final":
            continue

        is_relay = event_name in RELAY_EVENTS

        events.append(
            {
                "event_id": event_id,
                "event": event_name,
                "gender": gender,
                "is_relay": is_relay,
                "round": round_name,
            }
        )
    return events


def _parse_event_label(label: str) -> tuple[str | None, str, str]:
    """
    Parse event link text like 'Women 100m Freestyle Final'
    into (gender, event_name, round).
    Returns (None, label, '') if it can't be parsed.
    """
    label = label.strip()
    gender: str | None = None
    if label.startswith("Women") or label.startswith("W "):
        gender = "F"
        label = label.replace("Women", "", 1).replace("W ", "", 1).strip()
    elif label.startswith("Men") or label.startswith("M "):
        gender = "M"
        label = label.replace("Men", "", 1).replace("M ", "", 1).strip()
    elif label.startswith("Mixed"):
        gender = "X"
        # keep "Mixed" in the event name for relays

    round_name = ""
    for r in ("Final", "Heats", "Semifinal", "Heat"):
        if label.endswith(r):
            round_name = r if r != "Heat" else "Heats"
            label = label[: -len(r)].strip()
            break

    return gender, label, round_name
