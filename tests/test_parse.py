"""Offline tests for seslisozluk_mcp parsers (recorded fixtures, no network).

Fixtures (recorded 2026-11-19 from www.seslisozluk.net):
- word-merhaba-en.html — "merhaba" (TR->EN + TR-TR panels, 19 + 6 entries)
- word-hello-en.html — "hello" (EN-TR + EN-EN + reverse TR-EN panels)
- word-notfound.html — "zzzzzqqqx" (HTTP 200, "sözlükte bulunamadı")
- home.html — the home page (health-check probe)

Run with:  python -m pytest tests/test_parse.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from seslisozluk_mcp import parse as P  # noqa: E402
from seslisozluk_mcp import http as H  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"


def _read(name: str) -> str:
    return (FIX / name).read_text(encoding="utf-8")


# --- word + found ----------------------------------------------------------

def test_word_and_found():
    assert P.parse_word(_read("word-merhaba-en.html")) == "merhaba"
    assert P.parse_word(_read("word-hello-en.html")) == "hello"
    assert P.parse_word(_read("word-notfound.html")) == "zzzzzqqqx"
    assert P.is_found(_read("word-merhaba-en.html")) is True
    assert P.is_found(_read("word-hello-en.html")) is True
    assert P.is_found(_read("word-notfound.html")) is False


def test_word_slug():
    assert H.word_slug("merhaba") == "merhaba"
    assert H.word_slug("how do you do?") == "how-do-you-do%3F"
    assert H.word_slug("merhaba nasılsın") == "merhaba-nas%C4%B1ls%C4%B1n"
    assert H.word_slug("g'day") == "g%27day"
    assert H.word_url("merhaba") == (
        "https://www.seslisozluk.net/en/what-is-the-meaning-of-merhaba/"
    )


# --- dictionary panels ------------------------------------------------------

def test_merhaba_panels_and_counts():
    dicts = P.parse_dictionaries(_read("word-merhaba-en.html"))
    assert [d["name"] for d in dicts] == ["Turkish English", "Turkish Turkish"]
    assert len(dicts[0]["entries"]) == 19
    assert len(dicts[1]["entries"]) == 6
    first = dicts[0]["entries"][0]
    assert first["text"] == "hi"
    assert first["url"] == (
        "https://www.seslisozluk.net/en/what-is-the-meaning-of-hi/"
    )
    # slang marker survives as category
    assert dicts[0]["entries"][-1]["text"] == "g'day"
    assert dicts[0]["entries"][-1]["category"] == "(Argo)"


def test_merhaba_turkish_turkish_plain_text():
    dicts = P.parse_dictionaries(_read("word-merhaba-en.html"))
    tr_tr = dicts[1]["entries"]
    assert tr_tr[0]["category"] == "(Osmanlı Dönemi)"
    assert tr_tr[0]["text"].startswith("Müslümanlar arasında")
    assert "url" not in tr_tr[0]  # plain-text definition, no link
    assert tr_tr[-1]["text"].startswith('"Geniş ve mamur yere geldiniz')


def test_hello_three_panels_reverse_lookup():
    dicts = P.parse_dictionaries(_read("word-hello-en.html"))
    assert [d["name"] for d in dicts] == [
        "English Turkish", "English English", "Turkish English",
    ]
    assert len(dicts[0]["entries"]) == 15
    assert len(dicts[1]["entries"]) == 23
    assert dicts[0]["entries"][0]["text"] == "Merhaba"
    # English-English plain-text definition with a bare <q> example
    en_en = dicts[1]["entries"][0]
    assert en_en["text"].startswith("A greeting (salutation)")
    assert en_en["examples"] == [{"text": "Hello, everyone."}]


def test_notfound_has_no_dictionaries():
    assert P.parse_dictionaries(_read("word-notfound.html")) == []


# --- examples ---------------------------------------------------------------

def test_examples_pairs_and_bare():
    ex = P.parse_examples(_read("word-merhaba-en.html"))
    assert len(ex) == 2
    assert ex[0]["tr"].startswith("Hello, I have a reservation")
    assert ex[0]["en"].startswith("Merhaba, benim bir rezervasyonum")
    assert ex[1] == {
        "tr": "Hello, are you Mr Ogawa?",
        "en": "Merhaba, siz Bay Ogawa mısınız?",
    }
    hello_ex = P.parse_examples(_read("word-hello-en.html"))
    assert len(hello_ex) == 15
    assert hello_ex[0] == {
        "tr": "Merhaba Mimi! Nasılsın?",
        "en": "Hello Mimi! How are you?",
    }
    # bare <q> examples are kept as {"text": ...}
    assert {"text": "Hello, everyone."} in hello_ex
    assert P.parse_examples(_read("word-notfound.html")) == []


def test_examples_inline_with_entry():
    dicts = P.parse_dictionaries(_read("word-hello-en.html"))
    merhaba = dicts[0]["entries"][0]
    assert merhaba["text"] == "Merhaba"
    assert len(merhaba["examples"]) == 2
    assert merhaba["examples"][0]["en"] == "Hello Mimi! How are you?"


# --- about-word sections ----------------------------------------------------

def test_hyphenation_and_pronunciation():
    merhaba = _read("word-merhaba-en.html")
    assert P.parse_hyphenation(merhaba) == "mer·ha·ba"
    assert P.parse_pronunciation(merhaba) is None
    assert P.parse_turkish_pronunciation(merhaba) is None
    assert P.parse_etymology(merhaba) is None
    hello = _read("word-hello-en.html")
    assert P.parse_hyphenation(hello) == "hel·lo"
    assert P.parse_pronunciation(hello) == "/həˈlō/ /həˈloʊ/"
    assert P.parse_turkish_pronunciation(hello) == "hılō"
    assert P.parse_etymology(hello).startswith("[ h&-lO, he- ]")
    assert "Thomas Edison" in P.parse_etymology(hello)


def test_synonyms_antonyms_tenses_collocations():
    hello = _read("word-hello-en.html")
    syn = P.parse_synonyms(hello)
    assert len(syn) == 15
    assert syn[0]["text"] == "g'day"
    assert syn[0]["url"].startswith("https://www.seslisozluk.net/en/")
    ant = P.parse_antonyms(hello)
    assert [a["text"] for a in ant] == ["bye", "goodbye", "au revoir", "adios"]
    tenses = P.parse_tenses(hello)
    assert [t["text"] for t in tenses] == ["hellos", "helloing", "helloed"]
    coll = P.parse_collocations(hello)
    assert [c["text"] for c in coll] == [
        "hello there", "hello friend", "hello friends",
    ]
    merhaba = _read("word-merhaba-en.html")
    assert P.parse_synonyms(merhaba) == []
    assert P.parse_antonyms(merhaba) == []
    assert [c["text"] for c in P.parse_collocations(merhaba)] == [
        "merhaba askim", "merhaba canim", "merhaba nasilsin canim",
    ]


def test_related_terms():
    hello = _read("word-hello-en.html")
    rel = P.parse_related_terms(hello)
    assert len(rel) == 34
    assert rel[0]["term"] == "hello all"
    assert rel[0]["url"].endswith("/en/what-is-the-meaning-of-hello-all/")
    assert rel[0]["definitions"] == ["herkese merhaba"]
    assert any(r["term"] == "hello world" for r in rel)
    merhaba = _read("word-merhaba-en.html")
    rel_m = P.parse_related_terms(merhaba)
    assert len(rel_m) == 11
    assert rel_m[0]["term"] == "merhaba demek"
    assert rel_m[0]["definitions"] == ["say hello"]


# --- audio ------------------------------------------------------------------

def test_audio_accents():
    merhaba = P.parse_audio(_read("word-merhaba-en.html"))
    assert merhaba == [{
        "accent": "tr",
        "url": "https://static.seslisozluk.net/listen/f/fff25e14af3ee1c6b166172cf19c3823.mp3",
    }]
    hello = P.parse_audio(_read("word-hello-en.html"))
    assert [a["accent"] for a in hello] == ["uk", "us", "au"]
    assert all(a["url"].startswith("https://static.seslisozluk.net/pronunciation/en/")
               for a in hello)
    assert P.parse_audio(_read("word-notfound.html")) == []


# --- whole page ---------------------------------------------------------------

def test_parse_word_page_merhaba():
    d = P.parse_word_page(
        _read("word-merhaba-en.html"),
        "https://www.seslisozluk.net/en/what-is-the-meaning-of-merhaba/",
    )
    assert d["word"] == "merhaba"
    assert d["found"] is True
    assert d["url"].endswith("/what-is-the-meaning-of-merhaba/")
    assert len(d["dictionaries"]) == 2
    assert d["hyphenation"] == "mer·ha·ba"
    assert d["pronunciation"] is None
    assert d["etymology"] is None
    assert d["tenses"] == []
    assert d["synonyms"] == []
    assert d["antonyms"] == []
    assert len(d["collocations"]) == 3
    assert len(d["related_terms"]) == 11
    assert len(d["audio"]) == 1


def test_parse_word_page_notfound():
    d = P.parse_word_page(
        _read("word-notfound.html"),
        "https://www.seslisozluk.net/en/what-is-the-meaning-of-zzzzzqqqx/",
    )
    assert d["word"] == "zzzzzqqqx"
    assert d["found"] is False
    assert d["dictionaries"] == []
    assert d["hyphenation"] is None
    assert d["audio"] == []
    assert d["related_terms"] == []
