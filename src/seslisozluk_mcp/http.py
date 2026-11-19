"""HTTP layer for seslisozluk_mcp.

Data source: Sesli Sözlük (https://www.seslisozluk.net) — Türkiye's
multilingual online dictionary since 1999 (20M+ words, 20 languages).
No login, no API key. Everything used here was verified live 2026-11-19:

- GET /en/what-is-the-meaning-of-<word>/ — one word page, server-
  rendered. The slug is the word with spaces turned into hyphens and
  punctuation percent-encoded ("how do you do?" ->
  "how-do-you-do%3F", "merhaba nasılsın" ->
  "merhaba-nas%C4%B1ls%C4%B1n"). The page auto-detects the direction:
  a Turkish word gets "Turkish - English" (+ "Turkish - Turkish")
  panels, an English word gets "English - Turkish" (+ "English -
  English" and a reverse "Turkish - English") panels. Each panel is a
  <dl> of <dd class="ordered-list"> entries: a definition-link anchor
  (or plain text for monolingual entries), optional <var class="pos">
  part-of-speech and <var class="ottoman|category"> markers, and
  example sentences as <q lang=tr> - <q lang=en> pairs.
- The right column carries "about word" sections: Hyphenation
  ("mer·ha·ba"), Pronunciation (IPA, e.g. /həˈlō/ /həˈloʊ/),
  Turkish pronunciation ("hılō"), Synonyms, Antonyms, Etymology,
  Tenses and Common Collocations (all <a class="word-link"> lists),
  plus a "Related Terms" <h3> with <dt class="similar"> pairs.
- Audio: listen_word('<accent>','<path>') onclicks — the path is
  relative to https://static.seslisozluk.net/ (verified 200 for a UK
  mp3). Accents: tr, uk, us, au.
- Not-found words still return HTTP 200 with the marker
  "sözlükte bulunamadı" ("not found in the dictionary") in the body.
- The /tr/ UI uses a different slug pattern (unverified) and is NOT
  used: the /en/ pages serve both directions.
- The search form POSTs to "/" — no search API is used; lookup builds
  the word-page URL directly.

Transport uses curl-cffi Chrome impersonation with a plain-requests
fallback (the proven Turkey-factory pattern), even though the site
currently answers plain HTTP 200. Requests are kept gentle (one at a
time, ~0.5s apart) and read-only.
"""
from __future__ import annotations

import time
from urllib.parse import quote

from curl_cffi import requests as _creq
import requests as _plain

BASE = "https://www.seslisozluk.net"
STATIC = "https://static.seslisozluk.net"
TIMEOUT = 30.0
MIN_INTERVAL = 0.5  # seconds between requests — be polite

_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
}

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

_last_fetch = 0.0


class SeslisozlukError(RuntimeError):
    pass


def _throttle() -> None:
    global _last_fetch
    wait = MIN_INTERVAL - (time.monotonic() - _last_fetch)
    if wait > 0:
        time.sleep(wait)
    _last_fetch = time.monotonic()


_PROFILES = ("chrome120", "chrome131", "safari17_0")
_MAX_ATTEMPTS = 2  # one retry with the next profile
_RETRY_BACKOFF = 1.0  # seconds between attempts
_profile_idx = 0  # sticky: profile that last succeeded


def _request(url: str, headers: dict, timeout: float = TIMEOUT):
    """GET with fingerprint rotation.

    Starts at the sticky profile (chrome120 on a fresh process), retries
    once with the next profile on HTTP 403/429 or a transport error, then
    returns the last response (so the caller raises the specific 403/429
    error) or raises a network error if every attempt failed at the
    transport.
    """
    global _profile_idx
    last_exc: Exception | None = None
    for k in range(_MAX_ATTEMPTS):
        profile = _PROFILES[(_profile_idx + k) % len(_PROFILES)]
        try:
            resp = _creq.get(url, impersonate=profile, headers=headers, timeout=timeout)
        except Exception as e:
            last_exc = e
            if k + 1 < _MAX_ATTEMPTS:
                time.sleep(_RETRY_BACKOFF)
                continue
            raise SeslisozlukError(f"network error fetching {url}: {e}") from e
        if resp.status_code in (403, 429):
            if k + 1 < _MAX_ATTEMPTS:
                time.sleep(_RETRY_BACKOFF)
                continue
            return resp
        _profile_idx = (_profile_idx + k) % len(_PROFILES)
        return resp
    raise SeslisozlukError(f"network error fetching {url}: {last_exc}") from last_exc


def _get_text(url: str) -> str:
    """GET a URL, return the decoded text body.

    Raises SeslisozlukError with a human-readable message for HTTP errors.
    """
    _throttle()
    headers = dict(_HEADERS)
    try:
        resp = _request(url, headers)
        status, text = resp.status_code, resp.text
    except Exception:
        # Fallback transport: plain requests with a browser UA.
        try:
            resp = _plain.get(url, headers={**headers, "User-Agent": _UA}, timeout=TIMEOUT)
            status, text = resp.status_code, resp.text
        except SeslisozlukError:
            raise
        except Exception as e:
            raise SeslisozlukError(f"network error fetching {url}: {e}") from e
    if status == 403:
        raise SeslisozlukError(
            "www.seslisozluk.net refused the request (HTTP 403, bot wall)"
            " — try again later"
        )
    if status == 429:
        raise SeslisozlukError(
            "www.seslisozluk.net rate-limited the request (HTTP 429)"
            " — try again later"
        )
    if status == 404:
        raise SeslisozlukError(f"www.seslisozluk.net has no page at {url} (HTTP 404)")
    if status != 200:
        raise SeslisozlukError(
            f"www.seslisozluk.net returned HTTP {status} for {url}"
        )
    return text


def word_slug(word: str) -> str:
    """The site's word-page slug: spaces become hyphens, punctuation is
    percent-encoded ("how do you do?" -> "how-do-you-do%3F")."""
    slug = "-".join((word or "").strip().split())
    return quote(slug, safe="-")


def word_url(word: str) -> str:
    """The /en/ word-page URL for a word or phrase."""
    return f"{BASE}/en/what-is-the-meaning-of-{word_slug(word)}/"


def fetch_word_page(word: str) -> str:
    """One word page (server-rendered). Raises on HTTP errors; a word
    the dictionary does not know still returns HTTP 200 with the
    "sözlükte bulunamadı" marker — see parse.is_found."""
    return _get_text(word_url(word))


def fetch_home_page() -> str:
    """The Sesli Sözlük home page (used by the health check)."""
    return _get_text(f"{BASE}/")


def health_check() -> dict:
    """Two polite probes: the home page and a known word page.

    Returns {"status": "ok"|"blocked"|"error", "http_status": int|None,
    "url": ..., "detail": ...}. Used by the `seslisozluk_health` tool
    and the daily smoke CI.
    """
    url = f"{BASE}/"
    try:
        import html as _html

        home = _html.unescape(fetch_home_page())
        if "Sesli Sözlük" not in home:
            return {
                "status": "error",
                "http_status": 200,
                "url": url,
                "detail": "home page returned 200 but no Sesli Sözlük content",
            }
        word = _html.unescape(fetch_word_page("merhaba"))
        if "Definition of" not in word or "merhaba" not in word:
            return {
                "status": "error",
                "http_status": 200,
                "url": word_url("merhaba"),
                "detail": "word page returned 200 but no definition content",
            }
    except SeslisozlukError as e:
        msg = str(e)
        if "403" in msg:
            return {"status": "blocked", "http_status": 403, "url": url, "detail": msg}
        if "429" in msg:
            return {"status": "blocked", "http_status": 429, "url": url, "detail": msg}
        return {"status": "error", "http_status": None, "url": url, "detail": msg}
    return {"status": "ok", "http_status": 200, "url": url}
