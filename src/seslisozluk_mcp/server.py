"""MCP server: unofficial read-only access to Sesli Sözlük (Turkish dictionary)."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from . import http as _http
from . import parse as _P

mcp = FastMCP("seslisozluk-mcp")

INSTRUCTIONS = """\
Unofficial read-only MCP server for Sesli Sözlük (www.seslisozluk.net) \
— Türkiye's multilingual online dictionary since 1999 (20M+ words, 20 \
languages): word lookup in both directions (a Turkish word returns \
Turkish–English + Turkish–Turkish definitions, an English word returns \
English–Turkish + English–English + the reverse Turkish–English panel), \
with hyphenation, IPA pronunciation, Turkish pronunciation, etymology, \
tenses, synonyms, antonyms, common collocations, related terms, example \
sentences (Turkish–English pairs) and pronunciation audio (UK/US/AU \
English, Turkish — MP3 on static.seslisozluk.net). Data comes from \
www.seslisozluk.net (server-rendered word pages) — no login, no API key. \
A word the dictionary does not know returns found=false ("sözlükte \
bulunamadı"). Definitions can include user-contributed content (slang \
is marked "(Argo)", Ottoman-era entries "(Osmanlı Dönemi)"). Read-only; \
transport uses Chrome TLS impersonation with a plain-requests fallback; \
requests are spaced ~0.5s apart. Built by Mohammad Abbasi \
(mohammad-abbasi-sh) — https://almanibama.ir · https://mabbasi.ir — \
Turkey MCP factory.\
"""

_SOURCE = "www.seslisozluk.net"
_DISCLAIMER = (
    "Unofficial read-only Sesli Sözlük data from the public word pages "
    "of www.seslisozluk.net; verify on the official site before acting "
    "on it. Definitions can include user-contributed content."
)


def _envelope() -> dict:
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": _SOURCE,
        "disclaimer": _DISCLAIMER,
    }


def _ok(payload: dict) -> str:
    return json.dumps({**_envelope(), **payload}, ensure_ascii=False)


def _err(e: Exception) -> str:
    return _ok({"error": str(e)})


def _word_page(word: str) -> tuple[str, str]:
    """Fetch + parse one word page. Returns (page_html, url)."""
    word = (word or "").strip()
    if not word:
        raise ValueError("word must not be empty")
    url = _http.word_url(word)
    return _http.fetch_word_page(word), url


@mcp.tool()
def seslisozluk_lookup(word: str) -> str:
    """Look up a word or phrase in Sesli Sözlük (Turkish–English and
    English–Turkish, both directions auto-detected).

    word: a Turkish or English word or phrase, e.g. "merhaba",
    "hello", "merhaba nasılsın". Returns found (false when the
    dictionary does not know the word), the dictionary panels
    (definitions with part of speech, category, example sentences and
    links), hyphenation, IPA pronunciation, Turkish pronunciation,
    etymology, tenses, synonyms, antonyms, common collocations,
    related terms and pronunciation audio URLs (uk/us/au/tr MP3)."""
    try:
        page, url = _word_page(word)
        return _ok(_P.parse_word_page(page, url))
    except (ValueError, _http.SeslisozlukError) as e:
        return _err(e)


@mcp.tool()
def seslisozluk_examples(word: str) -> str:
    """Example sentences for a word or phrase, as Turkish–English
    pairs ({"tr", "en"}) — or a bare {"text"} example for monolingual
    entries.

    word: a Turkish or English word or phrase. Returns found plus the
    deduplicated example sentences in page order. Useful for seeing a
    word in real use; seslisozluk_lookup returns the same sentences
    inline with each definition."""
    try:
        page, url = _word_page(word)
        return _ok({
            "word": _P.parse_word(page),
            "found": _P.is_found(page),
            "url": url,
            "count": len(_P.parse_examples(page)),
            "examples": _P.parse_examples(page),
        })
    except (ValueError, _http.SeslisozlukError) as e:
        return _err(e)


@mcp.tool()
def seslisozluk_synonyms(word: str) -> str:
    """Synonyms, antonyms, common collocations and related terms for a
    word or phrase.

    word: a Turkish or English word or phrase. Returns found plus the
    four lists (each item carries its own Sesli Sözlük URL; related
    terms also carry their short definitions). Empty lists mean the
    page has no such section for this word."""
    try:
        page, url = _word_page(word)
        return _ok({
            "word": _P.parse_word(page),
            "found": _P.is_found(page),
            "url": url,
            "synonyms": _P.parse_synonyms(page),
            "antonyms": _P.parse_antonyms(page),
            "collocations": _P.parse_collocations(page),
            "related_terms": _P.parse_related_terms(page),
        })
    except (ValueError, _http.SeslisozlukError) as e:
        return _err(e)


@mcp.tool()
def seslisozluk_pronunciation(word: str) -> str:
    """Pronunciation of a word or phrase: hyphenation, IPA, Turkish
    pronunciation and audio.

    word: a Turkish or English word or phrase. Returns found plus
    hyphenation ("mer·ha·ba"), the IPA pronunciation ("/həˈlō/"),
    the Turkish pronunciation spelling ("hılō") and the audio URLs
    (accent uk/us/au/tr, MP3 on static.seslisozluk.net — verified
    reachable)."""
    try:
        page, url = _word_page(word)
        return _ok({
            "word": _P.parse_word(page),
            "found": _P.is_found(page),
            "url": url,
            "hyphenation": _P.parse_hyphenation(page),
            "pronunciation": _P.parse_pronunciation(page),
            "turkish_pronunciation": _P.parse_turkish_pronunciation(page),
            "audio": _P.parse_audio(page),
        })
    except (ValueError, _http.SeslisozlukError) as e:
        return _err(e)


@mcp.tool()
def seslisozluk_health() -> str:
    """Check whether Sesli Sözlük's site is reachable right now.

    Returns status ok (HTTP 200), blocked (HTTP 403/429 — bot wall or
    rate limit) or error, plus the HTTP status and the probed URL.
    Two polite requests; it does not fetch any word definitions beyond
    the "merhaba" probe page."""
    return _ok(_http.health_check())


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    import sys

    sys.exit(main())
