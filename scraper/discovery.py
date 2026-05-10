"""
Discover all relevant competitions and their swimming discipline IDs
using the worldaquatics.com REST API.

Two-step:
 1. Paginate /fina/competitions (100/page) to find competitions matching our filters
 2. For each, call /fina/competitions/{id}/events to get swimming discipline UUIDs
"""
from __future__ import annotations
import time
import logging
from dataclasses import dataclass

from .config import (
    API_BASE, RATE_LIMIT,
    COMPETITION_FILTERS, COMPETITION_EXCLUDES, DATE_FROM, DATE_TO, SWIM_SPORT_CODE,
)
from .utils import get_json

log = logging.getLogger(__name__)


@dataclass
class CompetitionMeta:
    id: int
    name: str
    competition_label: str   # "Olympics", "World Championships", etc.
    pool: str                # "LCM" or "SCM"
    year: int
    location: str


@dataclass
class DisciplineRef:
    comp: CompetitionMeta
    discipline_id: str       # UUID for /fina/events/{id}
    discipline_name: str     # e.g. "Women's 50m Freestyle"


def _match_competition(name: str) -> tuple[str, str] | None:
    """Return (label, pool) if this competition name matches our filters."""
    nl = name.lower()
    if any(ex in nl for ex in COMPETITION_EXCLUDES):
        return None
    for substr, label, pool in COMPETITION_FILTERS:
        if substr in nl:
            return label, pool
    return None


def discover_competitions(max_pages: int | None = None) -> list[CompetitionMeta]:
    """
    Paginate /fina/competitions (100 per page) and return filtered competitions.
    max_pages: cap for quick testing; None = all pages.
    """
    comps: list[CompetitionMeta] = []
    page = 0
    total_pages = 1  # updated on first response

    while page < total_pages:
        if max_pages is not None and page >= max_pages:
            break

        url = f"{API_BASE}/competitions?pageSize=100&page={page}"
        data = get_json(url)
        if not data:
            break

        if page == 0:
            total_pages = data["pageInfo"]["numPages"]
            log.info("Competitions: %d total across %d pages",
                     data["pageInfo"]["numEntries"], total_pages)

        for comp in data.get("content", []):
            date_str = (comp.get("venueDateFrom") or comp.get("dateFrom") or "")[:10]
            if not date_str or date_str < DATE_FROM or date_str > DATE_TO:
                continue

            match = _match_competition(comp["name"])
            if not match:
                continue

            label, pool = match
            comps.append(CompetitionMeta(
                id=comp["id"],
                name=comp["name"],
                competition_label=label,
                pool=pool,
                year=int(date_str[:4]),
                location=comp.get("location", {}).get("city", ""),
            ))

        page += 1
        time.sleep(RATE_LIMIT / 4)  # lighter rate for pagination

    log.info("Found %d relevant competitions", len(comps))
    return comps


def discover_disciplines(comp: CompetitionMeta) -> list[DisciplineRef]:
    """
    For one competition, fetch its event structure and return all swimming discipline refs.
    """
    url = f"{API_BASE}/competitions/{comp.id}/events"
    data = get_json(url)
    if not data:
        return []

    refs: list[DisciplineRef] = []
    for sport in data.get("Sports", []):
        if sport.get("Code") != SWIM_SPORT_CODE:
            continue
        for disc in sport.get("DisciplineList", []):
            disc_id   = disc.get("Id")
            disc_name = disc.get("DisciplineName") or disc.get("Name") or ""
            if disc_id and disc_name:
                refs.append(DisciplineRef(
                    comp=comp,
                    discipline_id=disc_id,
                    discipline_name=disc_name,
                ))

    log.debug("  %s %d: %d swimming disciplines",
              comp.competition_label, comp.year, len(refs))
    return refs
