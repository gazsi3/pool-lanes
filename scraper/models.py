from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RaceEntry:
    lane: int
    name: str
    nationality: str
    seed_time: Optional[str]
    final_time: Optional[str]
    position: Optional[int]
    dsq: bool = False
    dns: bool = False
    dnf: bool = False
    world_record: bool = False

    def to_dict(self) -> dict:
        d = {
            "lane": self.lane,
            "name": self.name,
            "nationality": self.nationality,
            "seed_time": self.seed_time,
            "final_time": self.final_time,
            "position": self.position,
            "dsq": self.dsq,
            "dns": self.dns,
            "dnf": self.dnf,
        }
        if self.world_record:
            d["world_record"] = True
        return d


@dataclass
class Final:
    competition: str
    year: int
    location: str
    pool: str
    event: str
    gender: str
    is_relay: bool
    entries: list[RaceEntry] = field(default_factory=list)
    meet_id: str = ""
    event_id: str = ""

    def to_dict(self) -> dict:
        return {
            "competition": self.competition,
            "year": self.year,
            "location": self.location,
            "pool": self.pool,
            "event": self.event,
            "gender": self.gender,
            "is_relay": self.is_relay,
            "meet_id": str(self.meet_id),
            "event_id": self.event_id,
            "entries": [e.to_dict() for e in self.entries],
        }
