"""
Entry point: python -m scraper.main [--competition olympics] [--year 2024] [--dry-run]

Without arguments, scrapes all configured competitions from 2000 onward.
Use --competition and --year flags to scrape a single competition for testing.
"""

import argparse
import logging
import sys

from .config import BASE_URL
from .discovery import discover_all_meets, discover_events
from .models import Final
from .parser import parse_event_page
from .storage import write_finals, write_meta, load_existing_finals
from .utils import browser_context, fetch_page

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def run(competition_filter: str | None = None, year_filter: int | None = None, dry_run: bool = False) -> None:
    all_finals: list[Final] = []

    with browser_context() as ctx:
        meets = discover_all_meets(ctx)
        log.info("Total meets discovered: %d", len(meets))

        if competition_filter:
            meets = [m for m in meets if competition_filter.lower() in m["competition"].lower()]
        if year_filter:
            meets = [m for m in meets if m["year"] == year_filter]

        log.info("Meets after filtering: %d", len(meets))

        for meet in meets:
            log.info("Processing: %s %d %s (meet_id=%s)", meet["competition"], meet["year"], meet["location"], meet["meet_id"])
            events = discover_events(ctx, meet)
            final_events = [e for e in events if e["round"] == "Final"]
            log.info("  %d finals events found", len(final_events))

            for event_meta in final_events:
                url = f"{BASE_URL}/index.php"
                params = {"page": "eventDetail", "eventId": event_meta["event_id"]}
                try:
                    html = fetch_page(ctx, url, params)
                    final = parse_event_page(html, meet, event_meta)
                    if final:
                        all_finals.append(final)
                        log.info("  + %s %s (%d entries)", event_meta["gender"], event_meta["event"], len(final.entries))
                except Exception as exc:
                    log.error("  ! Failed %s %s: %s", event_meta["gender"], event_meta["event"], exc)

    log.info("Scraping complete. %d finals collected.", len(all_finals))

    if not dry_run:
        write_finals(all_finals)
        write_meta(len(all_finals))
    else:
        log.info("Dry run — not writing output.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape swimming finals lane data")
    parser.add_argument("--competition", help="Filter by competition name (partial match)")
    parser.add_argument("--year", type=int, help="Filter by year")
    parser.add_argument("--dry-run", action="store_true", help="Don't write output files")
    args = parser.parse_args()
    run(competition_filter=args.competition, year_filter=args.year, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
