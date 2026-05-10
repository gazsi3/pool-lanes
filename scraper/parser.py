"""
Parse /fina/events/{discipline_id} JSON into Final objects.

Response structure:
  { DisciplineName, Gender, SportCode, Heats: [ { PhaseName, Name, Results: [...] } ] }

Each result in the Finals heat has:
  Lane, Rank, FullName, FirstName, LastName, NAT, Time, RT, Points,
  MedalTag (G/S/B), RecordTags (list), AthleteResultAge, BiographyId
"""
from __future__ import annotations
import re
import logging
from typing import Optional

from .config import API_BASE, MIN_VALID_ENTRIES, SWIM_SPORT_CODE
from .discovery import DisciplineRef
from .models import Final, RaceEntry
from .utils import get_json

log = logging.getLogger(__name__)

_RELAY_KEYWORDS = re.compile(r"\brelay\b|\bx\d+\b", re.IGNORECASE)
_GENDER_MAP = {"Women": "F", "Men": "M", "Mixed": "X", "1": "F", "2": "M"}


def _is_relay(discipline_name: str) -> bool:
    return bool(_RELAY_KEYWORDS.search(discipline_name))


def _parse_gender(heat: dict, disc_data: dict) -> str:
    raw = heat.get("Gender") or disc_data.get("Gender") or ""
    return _GENDER_MAP.get(raw, raw[:1].upper() or "?")


def _normalize_event_name(discipline_name: str) -> str:
    """
    'Women\'s 50m Freestyle'  →  '50m Freestyle'
    'Men\'s 4x100m Freestyle Relay'  →  '4x100m Freestyle Relay'
    'Mixed 4x100m Medley Relay'  →  'Mixed 4x100m Medley Relay'
    """
    name = re.sub(r"^(Women's|Men's)\s+", "", discipline_name)
    return name.strip()


def _parse_result(r: dict) -> Optional[RaceEntry]:
    """Convert one API result object into a RaceEntry."""
    lane_raw = r.get("Lane")
    try:
        lane = int(lane_raw)
    except (TypeError, ValueError):
        return None

    # Detect non-finishers by presence of status codes
    status = (r.get("Status") or "").upper()
    time_str = r.get("Time") or ""
    dsq = "DSQ" in status or "DQ" in status
    dns = "DNS" in status or lane == 0
    dnf = "DNF" in status

    # Record type: "WR" (World Record), "OR" (Olympic Record), "ER" (European Record), etc.
    record_type: str | None = r.get("RecordType") or None

    position: Optional[int] = None
    if not (dsq or dns or dnf):
        rank = r.get("Rank")
        if rank is not None:
            try:
                position = int(rank)
            except (TypeError, ValueError):
                pass

    # Name: prefer FullName, fall back to First + Last
    full = r.get("FullName") or ""
    if not full:
        first = r.get("FirstName") or ""
        last  = r.get("LastName") or ""
        full  = f"{first} {last}".strip()

    nat = r.get("NAT") or ""

    final_time: Optional[str] = time_str if (time_str and not dns and not dsq) else None

    return RaceEntry(
        lane=lane,
        name=full,
        nationality=nat,
        seed_time=None,
        final_time=final_time,
        position=position,
        dsq=dsq,
        dns=dns,
        dnf=dnf,
        record_type=record_type,
    )


def _find_final_heat(heats: list[dict]) -> Optional[dict]:
    """Return the heat whose PhaseName is 'Finals' (preferring Name=='Final')."""
    finals = [h for h in heats if h.get("PhaseName") == "Finals"]
    if not finals:
        return None
    # Prefer the heat literally named "Final" (not "Final A / Final B")
    named_final = next((h for h in finals if h.get("Name") == "Final"), None)
    return named_final or finals[0]


def parse_discipline(ref: DisciplineRef) -> Optional[Final]:
    """
    Fetch /fina/events/{discipline_id} and return the Finals heat as a Final object.
    Returns None if no Finals heat or too few valid entries.
    """
    url = f"{API_BASE}/events/{ref.discipline_id}"
    data = get_json(url)
    if not data:
        return None

    sport_code = data.get("SportCode", "")
    if sport_code and sport_code != SWIM_SPORT_CODE:
        return None

    heats = data.get("Heats") or []
    final_heat = _find_final_heat(heats)
    if not final_heat:
        log.debug("No Finals heat for %s", ref.discipline_name)
        return None

    results_raw = final_heat.get("Results") or []
    entries: list[RaceEntry] = []
    for r in results_raw:
        entry = _parse_result(r)
        if entry is not None:
            entries.append(entry)

    # DNS swimmers don't occupy a lane — don't count them toward minimum
    scoreable = [e for e in entries if not e.dns]
    if len(scoreable) < MIN_VALID_ENTRIES:
        log.warning("Too few entries (%d) for %s %s %d — skipping",
                    len(scoreable), ref.comp.competition_label,
                    ref.discipline_name, ref.comp.year)
        return None

    gender = _parse_gender(final_heat, data)
    event_name = _normalize_event_name(ref.discipline_name)

    return Final(
        competition=ref.comp.competition_label,
        year=ref.comp.year,
        location=ref.comp.location,
        pool=ref.comp.pool,
        event=event_name,
        gender=gender,
        is_relay=_is_relay(ref.discipline_name),
        entries=entries,
        meet_id=ref.comp.id,
        event_id=ref.discipline_id,
    )
