"""
Parse swimrankings.net event result pages into Final objects.

Expected column order in result tables:
  RANK | HEAT | LANE | NAME | NOC | BORN | R.T. | [split times...] | TIME | GAP | FINA PTS

The parser searches for LANE and other critical columns by header text,
so it is resilient to column-count variations between events.
"""

import logging
import re
from typing import Optional

from bs4 import BeautifulSoup, Tag

from .config import RELAY_EVENTS, MIN_VALID_ENTRIES
from .models import Final, RaceEntry

log = logging.getLogger(__name__)

_STATUS_TOKENS = {"DSQ", "DNS", "DNF", "DQ", "NT", "NS"}


def parse_event_page(html: str, meet_meta: dict, event_meta: dict) -> Optional[Final]:
    soup = BeautifulSoup(html, "lxml")

    table = _find_results_table(soup)
    if table is None:
        log.debug("No results table on event %s", event_meta["event_id"])
        return None

    headers, col_idx = _parse_headers(table)
    if col_idx.get("lane") is None:
        log.debug("No LANE column for event %s", event_meta["event_id"])
        return None

    entries = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all(["td", "th"])
        if len(cells) < 4:
            continue
        entry = _parse_row(cells, col_idx)
        if entry is not None:
            entries.append(entry)

    if len([e for e in entries if not e.dns]) < MIN_VALID_ENTRIES:
        log.warning(
            "Too few valid entries (%d) for %s %s %s — skipping",
            len(entries),
            meet_meta["year"],
            meet_meta["competition"],
            event_meta["event"],
        )
        return None

    return Final(
        competition=meet_meta["competition"],
        year=meet_meta["year"],
        location=meet_meta["location"],
        pool=meet_meta["pool"],
        event=event_meta["event"],
        gender=event_meta["gender"],
        is_relay=event_meta["is_relay"],
        entries=entries,
        meet_id=meet_meta["meet_id"],
        event_id=event_meta["event_id"],
    )


def _find_results_table(soup: BeautifulSoup) -> Optional[Tag]:
    # Try known class names first
    for cls in ("rankingTable", "results", "eventresults", "meetResultsTable"):
        t = soup.find("table", class_=cls)
        if t:
            return t
    # Fall back: find any table that has a LANE header
    for t in soup.find_all("table"):
        headers_text = " ".join(
            th.get_text(strip=True).upper() for th in t.find_all("th")
        )
        if "LANE" in headers_text:
            return t
    return None


def _parse_headers(table: Tag) -> tuple[list[str], dict[str, int]]:
    header_row = table.find("tr")
    if header_row is None:
        return [], {}
    headers = [th.get_text(strip=True).upper() for th in header_row.find_all(["th", "td"])]
    idx: dict[str, int] = {}
    for i, h in enumerate(headers):
        if h == "RANK" and "rank" not in idx:
            idx["rank"] = i
        elif h == "LANE" and "lane" not in idx:
            idx["lane"] = i
        elif h in ("NAME", "ATHLETE", "SURNAME & NAME") and "name" not in idx:
            idx["name"] = i
        elif h in ("NOC", "NAT", "COUNTRY") and "noc" not in idx:
            idx["noc"] = i
        elif h in ("TIME", "RESULT") and "time" not in idx:
            idx["time"] = i
    return headers, idx


def _parse_row(cells: list[Tag], col_idx: dict[str, int]) -> Optional[RaceEntry]:
    def text(i: int) -> str:
        if i >= len(cells):
            return ""
        return cells[i].get_text(strip=True)

    lane_text = text(col_idx["lane"])
    try:
        lane = int(lane_text)
    except ValueError:
        return None  # header or section row

    rank_text = text(col_idx.get("rank", 0))
    time_text = text(col_idx.get("time", len(cells) - 3))
    name_text = text(col_idx.get("name", 3))
    noc_text = text(col_idx.get("noc", 4))

    combined = f"{rank_text} {time_text}".upper()
    dsq = "DSQ" in combined or "DQ" in combined
    dns = "DNS" in combined or "NS" in combined
    dnf = "DNF" in combined

    position: Optional[int] = None
    if not (dsq or dns or dnf):
        m = re.match(r"(\d+)", rank_text)
        if m:
            position = int(m.group(1))

    final_time: Optional[str] = None
    if not dsq and not dns and time_text and not any(t in time_text.upper() for t in _STATUS_TOKENS):
        final_time = time_text

    return RaceEntry(
        lane=lane,
        name=name_text,
        nationality=noc_text,
        seed_time=None,
        final_time=final_time,
        position=position,
        dsq=dsq,
        dns=dns,
        dnf=dnf,
    )
