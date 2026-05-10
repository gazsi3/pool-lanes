"""
Entry point: python -m scraper.main [--competition "World Championships"] [--year 2022] [--dry-run]

Without arguments, scrapes all configured competitions 2000-2024.
"""
import argparse
import logging
import time

from .discovery import discover_competitions, discover_disciplines
from .models import Final
from .parser import parse_discipline
from .storage import write_finals, write_meta
from .config import RATE_LIMIT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def run(
    competition_filter: str | None = None,
    year_filter: int | None = None,
    dry_run: bool = False,
) -> None:
    log.info("Discovering competitions...")
    comps = discover_competitions()

    if competition_filter:
        comps = [c for c in comps if competition_filter.lower() in c.competition_label.lower()
                 or competition_filter.lower() in c.name.lower()]
    if year_filter:
        comps = [c for c in comps if c.year == year_filter]

    log.info("Competitions to scrape: %d", len(comps))
    for c in comps:
        log.info("  [%d] %s — %s %d (%s)", c.id, c.name, c.competition_label, c.year, c.pool)

    all_finals: list[Final] = []
    total_disciplines = 0
    failed = 0

    for comp in comps:
        log.info("=== %s %d (%s) ===", comp.competition_label, comp.year, comp.location)
        disciplines = discover_disciplines(comp)
        log.info("  %d swimming disciplines", len(disciplines))
        time.sleep(RATE_LIMIT)

        for ref in disciplines:
            total_disciplines += 1
            try:
                final = parse_discipline(ref)
                if final:
                    all_finals.append(final)
                    wr_flag = " [WR]" if any(e.world_record for e in final.entries) else ""
                    log.info("  + %s %s (%d entries)%s",
                             final.gender, ref.discipline_name,
                             len(final.entries), wr_flag)
                time.sleep(RATE_LIMIT)
            except Exception as exc:
                failed += 1
                log.error("  ! Failed %s: %s", ref.discipline_name, exc)

    log.info("Done. %d finals from %d disciplines (%d errors).",
             len(all_finals), total_disciplines, failed)

    if not dry_run:
        write_finals(all_finals)
        write_meta(len(all_finals))
        log.info("Written to public/data/finals.json")
    else:
        log.info("Dry run — no output written.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape swimming finals lane data")
    parser.add_argument("--competition", help="Filter by competition label (partial)")
    parser.add_argument("--year", type=int, help="Filter by year")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(competition_filter=args.competition, year_filter=args.year, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
