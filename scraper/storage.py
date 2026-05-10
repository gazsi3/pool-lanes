import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .models import Final

OUTPUT_DIR = Path(__file__).parent.parent / "public" / "data"
log = logging.getLogger(__name__)


def write_finals(finals: list[Final]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "finals.json"
    data = [f.to_dict() for f in finals]
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Wrote %d finals to %s", len(finals), out_path)


def write_meta(record_count: int) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    meta = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "record_count": record_count,
    }
    (OUTPUT_DIR / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


def load_existing_finals() -> list[dict]:
    path = OUTPUT_DIR / "finals.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))
