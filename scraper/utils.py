import time
import logging
from contextlib import contextmanager
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, TimeoutError as PWTimeout

from .config import CLOUDFLARE_WAIT_SECONDS, RATE_LIMIT_SECONDS, MAX_RETRIES, RETRY_BACKOFF

log = logging.getLogger(__name__)

_last_request_time: float = 0.0


@contextmanager
def browser_context():
    """Yield a Playwright browser context. Caller is responsible for pages."""
    with sync_playwright() as pw:
        browser: Browser = pw.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        ctx: BrowserContext = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            viewport={"width": 1280, "height": 900},
        )
        try:
            yield ctx
        finally:
            ctx.close()
            browser.close()


def fetch_page(ctx: BrowserContext, url: str, params: dict | None = None) -> str:
    """
    Navigate to url (optionally with query params), wait for Cloudflare challenge
    to resolve, return the final page HTML. Respects global rate limit.
    """
    global _last_request_time

    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        full_url = f"{url}?{qs}" if "?" not in url else f"{url}&{qs}"
    else:
        full_url = url

    # Rate limiting
    elapsed = time.time() - _last_request_time
    if elapsed < RATE_LIMIT_SECONDS:
        time.sleep(RATE_LIMIT_SECONDS - elapsed)

    page: Page = ctx.new_page()
    try:
        for attempt in range(MAX_RETRIES):
            try:
                page.goto(full_url, wait_until="domcontentloaded", timeout=30_000)
                # Wait for Cloudflare JS challenge if present
                if "Just a moment" in page.title():
                    log.debug("Cloudflare challenge detected, waiting %ss", CLOUDFLARE_WAIT_SECONDS)
                    time.sleep(CLOUDFLARE_WAIT_SECONDS)
                    page.wait_for_load_state("networkidle", timeout=20_000)
                _last_request_time = time.time()
                return page.content()
            except PWTimeout:
                if attempt == MAX_RETRIES - 1:
                    raise
                wait = RETRY_BACKOFF * (attempt + 1)
                log.warning("Timeout on %s (attempt %d), retrying in %ds", full_url, attempt + 1, wait)
                time.sleep(wait)
    finally:
        page.close()

    return ""
