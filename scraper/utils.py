import time
import logging
from typing import Any

import requests

from .config import HEADERS, RATE_LIMIT, MAX_RETRIES, RETRY_BACKOFF

log = logging.getLogger(__name__)

_last_request_time: float = 0.0


def get_json(url: str) -> Any:
    """
    HTTP GET with rate limiting and retries. Returns parsed JSON or None on error.
    """
    global _last_request_time

    elapsed = time.time() - _last_request_time
    if elapsed < RATE_LIMIT:
        time.sleep(RATE_LIMIT - elapsed)

    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            _last_request_time = time.time()
            if r.status_code == 200:
                return r.json()
            if r.status_code == 404:
                log.debug("404 %s", url)
                return None
            log.warning("HTTP %d for %s (attempt %d)", r.status_code, url, attempt + 1)
        except requests.RequestException as e:
            log.warning("Request error for %s (attempt %d): %s", url, attempt + 1, e)

        if attempt < MAX_RETRIES - 1:
            wait = RETRY_BACKOFF * (attempt + 1)
            log.info("Retrying in %ds...", wait)
            time.sleep(wait)

    return None
