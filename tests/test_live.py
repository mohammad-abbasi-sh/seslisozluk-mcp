"""Live tests: hit the real Sesli Sözlük site (no key, read-only).

Kept small and polite (~0.5s between requests, one call per tool).
Assertions are date-independent (counts and shapes, not frozen data).

Run with:  python -m pytest tests/test_live.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from seslisozluk_mcp.server import (  # noqa: E402
    seslisozluk_examples,
    seslisozluk_health,
    seslisozluk_lookup,
    seslisozluk_pronunciation,
    seslisozluk_synonyms,
)


def _parse(out: str) -> dict:
    return json.loads(out)


def test_live_lookup_merhaba():
    out = _parse(seslisozluk_lookup("merhaba"))
    assert "error" not in out, out.get("error")
    assert out["found"] is True
    assert out["word"] == "merhaba"
    names = [d["name"] for d in out["dictionaries"]]
    assert "Turkish English" in names
    tr_en = next(d for d in out["dictionaries"] if d["name"] == "Turkish English")
    assert len(tr_en["entries"]) >= 10
    assert tr_en["entries"][0]["text"] == "hi"
    assert out["hyphenation"] == "mer·ha·ba"
    assert out["audio"] and out["audio"][0]["accent"] == "tr"
    assert out["audio"][0]["url"].startswith(
        "https://static.seslisozluk.net/"
    )


def test_live_lookup_hello():
    out = _parse(seslisozluk_lookup("hello"))
    assert "error" not in out, out.get("error")
    assert out["found"] is True
    names = [d["name"] for d in out["dictionaries"]]
    assert "English Turkish" in names
    assert "English English" in names
    en_tr = next(d for d in out["dictionaries"] if d["name"] == "English Turkish")
    assert en_tr["entries"][0]["text"] == "Merhaba"
    assert out["hyphenation"] == "hel·lo"
    assert out["pronunciation"] and "hə" in out["pronunciation"]
    assert out["turkish_pronunciation"] == "hılō"
    assert out["etymology"] and "Edison" in out["etymology"]
    assert len(out["synonyms"]) >= 5
    assert len(out["antonyms"]) >= 1
    assert len(out["audio"]) == 3
    assert {a["accent"] for a in out["audio"]} == {"uk", "us", "au"}


def test_live_lookup_notfound():
    out = _parse(seslisozluk_lookup("zzzzzqqqx"))
    assert "error" not in out, out.get("error")
    assert out["found"] is False
    assert out["dictionaries"] == []
    assert out["audio"] == []


def test_live_lookup_phrase():
    out = _parse(seslisozluk_lookup("merhaba nasılsın"))
    assert "error" not in out, out.get("error")
    assert out["found"] is True
    assert out["dictionaries"], "expected a panel for the phrase"


def test_live_examples():
    out = _parse(seslisozluk_examples("hello"))
    assert "error" not in out, out.get("error")
    assert out["found"] is True
    assert out["count"] >= 5
    assert all("tr" in e and "en" in e for e in out["examples"][:3])


def test_live_synonyms():
    out = _parse(seslisozluk_synonyms("hello"))
    assert "error" not in out, out.get("error")
    assert out["found"] is True
    assert len(out["synonyms"]) >= 5
    assert any(s["text"] == "hi" for s in out["synonyms"])
    assert len(out["antonyms"]) >= 1
    assert len(out["collocations"]) >= 1
    assert len(out["related_terms"]) >= 5


def test_live_synonyms_empty_sections():
    out = _parse(seslisozluk_synonyms("merhaba"))
    assert "error" not in out, out.get("error")
    assert out["synonyms"] == []  # merhaba has no Synonyms section
    assert len(out["collocations"]) >= 1
    assert len(out["related_terms"]) >= 5


def test_live_pronunciation():
    out = _parse(seslisozluk_pronunciation("hello"))
    assert "error" not in out, out.get("error")
    assert out["found"] is True
    assert out["hyphenation"] == "hel·lo"
    assert out["pronunciation"] and "hə" in out["pronunciation"]
    assert out["turkish_pronunciation"] == "hılō"
    assert len(out["audio"]) == 3


def test_live_pronunciation_turkish_word():
    out = _parse(seslisozluk_pronunciation("merhaba"))
    assert "error" not in out, out.get("error")
    assert out["hyphenation"] == "mer·ha·ba"
    assert len(out["audio"]) == 1
    assert out["audio"][0]["accent"] == "tr"


def test_live_health():
    out = _parse(seslisozluk_health())
    assert out["status"] == "ok", out
    assert out["http_status"] == 200
