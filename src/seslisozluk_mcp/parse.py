"""Parsers for Sesli Sözlük's server-rendered word pages (stdlib only).

All markup shapes were verified against live pages fetched 2026-11-19;
offline tests run against recorded fixtures in tests/fixtures/.
"""
from __future__ import annotations

import html as _html
import re

BASE = "https://www.seslisozluk.net"
STATIC = "https://static.seslisozluk.net"

NOT_FOUND_MARKER = "sözlükte bulunamadı"


def _clean(text: str) -> str:
    """Unescape HTML entities and collapse whitespace."""
    text = _html.unescape(text)
    text = text.replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def _html_to_text(fragment: str) -> str:
    """Strip tags from an HTML fragment, keeping paragraph breaks."""
    frag = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.I)
    frag = re.sub(r"</p\s*>", "\n", frag, flags=re.I)
    frag = re.sub(r"</li\s*>", "\n", frag, flags=re.I)
    frag = re.sub(r"<[^>]+>", "", frag)
    frag = _html.unescape(frag).replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in frag.split("\n")]
    return "\n".join(ln for ln in lines if ln)


def is_found(page_html: str) -> bool:
    """A word the dictionary does not know still returns HTTP 200 —
    the body carries the "sözlükte bulunamadı" marker instead."""
    return NOT_FOUND_MARKER not in page_html


def parse_word(page_html: str) -> str | None:
    """The looked-up word: the first <dfn> on the page, else the
    <title> ("What is merhaba - Sesli Sözlük")."""
    m = re.search(r"<dfn[^>]*>(.*?)</dfn>", page_html, re.S)
    if m:
        return _clean(m.group(1)) or None
    m = re.search(r"<title>\s*What is (.*?) - Sesli", page_html, re.S)
    if m:
        return _clean(m.group(1)) or None
    return None


# ---------------------------------------------------------------------------
# Dictionary panels (<dl> blocks)
# ---------------------------------------------------------------------------

_DT_RE = re.compile(
    r"Definition of .*? in (.*?) dictionary", re.S
)
_DD_RE = re.compile(r'<dd class="ordered-list">(.*?)</dd>', re.S)
_LINK_RE = re.compile(
    r'<a class="definition-link"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S
)
_POS_RE = re.compile(r'<var class="pos"[^>]*>(.*?)</var>', re.S)
_CAT_RE = re.compile(
    r'<var class="(?:ottoman|category)"[^>]*>(.*?)</var>', re.S
)
_Q_PAIR_RE = re.compile(
    r'<q lang=["\']?tr["\']?>(.*?)</q>\s*-\s*<q lang=["\']?en["\']?>(.*?)</q>', re.S
)
_Q_SINGLE_RE = re.compile(r"<q>(.*?)</q>", re.S)


def _parse_examples(fragment: str) -> list[dict]:
    """Example sentences inside one <dd>: <q lang=tr> - <q lang=en>
    pairs, or a bare <q> (monolingual entries)."""
    out: list[dict] = []
    for tr, en in _Q_PAIR_RE.findall(fragment):
        out.append({"tr": _clean(tr), "en": _clean(en)})
    if not out:
        for q in _Q_SINGLE_RE.findall(fragment):
            # a <q> without lang is a monolingual example
            if "<q" not in q:
                out.append({"text": _clean(q)})
    return out


def _parse_entry(dd_html: str) -> dict:
    """One <dd class="ordered-list">: the definition text (a
    definition-link when present, else the plain text), part of
    speech / category markers, its own page URL, and examples."""
    pos_m = _POS_RE.search(dd_html)
    cat_m = _CAT_RE.search(dd_html)
    link_m = _LINK_RE.search(dd_html)
    examples = _parse_examples(dd_html)
    entry: dict = {}
    if pos_m:
        entry["pos"] = _clean(pos_m.group(1))
    if cat_m:
        entry["category"] = _clean(cat_m.group(1))
    if link_m:
        href = _clean(link_m.group(1))
        entry["text"] = _clean(link_m.group(2))
        entry["url"] = href if href.startswith("http") else BASE + href
    else:
        # Plain-text definition: strip the <p> example blocks and the
        # <var> markers first, then the remaining text.
        body = re.sub(r"<p>.*?</p>", "", dd_html, flags=re.S)
        body = re.sub(r"<var[^>]*>.*?</var>", "", body, flags=re.S)
        entry["text"] = _html_to_text(body)
    if examples:
        entry["examples"] = examples
    return entry


def parse_dictionaries(page_html: str) -> list[dict]:
    """Every dictionary panel: {"name" ("Turkish - English"), "entries":
    [{text, url?, pos?, category?, examples?}]} in page order."""
    out: list[dict] = []
    for dl in re.findall(r"<dl>(.*?)</dl>", page_html, re.S):
        name_m = _DT_RE.search(dl)
        if not name_m:
            continue
        entries = [_parse_entry(dd) for dd in _DD_RE.findall(dl)]
        entries = [e for e in entries if e.get("text")]
        out.append({"name": _clean(name_m.group(1)), "entries": entries})
    return out


# ---------------------------------------------------------------------------
# "About word" sections (right column)
# ---------------------------------------------------------------------------

def _section_text(page_html: str, heading: str) -> str | None:
    """The text of an about-word section by its <h2> heading
    ("Hyphenation", "Pronunciation", "Etymology", ...). Sections hold
    plain text (and links) only — no nested <div>s."""
    m = re.search(
        r"<h2>" + re.escape(heading) + r"</h2>(.*?)</div>",
        page_html, re.S,
    )
    if not m:
        return None
    text = _html_to_text(m.group(1))
    return text or None


def _section_links(page_html: str, heading: str) -> list[dict]:
    """The <a class="word-link"> items of an about-word section
    (Synonyms, Antonyms, Tenses, Common Collocations)."""
    m = re.search(
        r"<h2>" + re.escape(heading) + r"</h2>(.*?)</div>",
        page_html, re.S,
    )
    if not m:
        return []
    out: list[dict] = []
    for href, text in re.findall(
        r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', m.group(1), re.S
    ):
        text = _clean(text)
        if not text:
            continue
        out.append({
            "text": text,
            "url": href if href.startswith("http") else BASE + href,
        })
    return out


def parse_hyphenation(page_html: str) -> str | None:
    return _section_text(page_html, "Hyphenation")


def parse_pronunciation(page_html: str) -> str | None:
    return _section_text(page_html, "Pronunciation")


def parse_turkish_pronunciation(page_html: str) -> str | None:
    return _section_text(page_html, "Turkish pronunciation")


def parse_etymology(page_html: str) -> str | None:
    return _section_text(page_html, "Etymology")


def parse_synonyms(page_html: str) -> list[dict]:
    return _section_links(page_html, "Synonyms")


def parse_antonyms(page_html: str) -> list[dict]:
    return _section_links(page_html, "Antonyms")


def parse_tenses(page_html: str) -> list[dict]:
    return _section_links(page_html, "Tenses")


def parse_collocations(page_html: str) -> list[dict]:
    return _section_links(page_html, "Common Collocations")


def parse_audio(page_html: str) -> list[dict]:
    """Pronunciation audio: listen_word('<accent>','<path>') onclicks.
    The path is relative to static.seslisozluk.net. Deduplicated by
    accent (a word can list the same accent twice)."""
    out: list[dict] = []
    seen: set[str] = set()
    for accent, path in re.findall(
        r"listen_word\('([^']+)','([^']+)'", page_html
    ):
        accent = accent.strip()
        path = path.strip()
        if not accent or not path or accent in seen:
            continue
        seen.add(accent)
        out.append({
            "accent": accent,
            "url": f"{STATIC}/{path.lstrip('/')}",
        })
    return out


# ---------------------------------------------------------------------------
# Related terms (<h3>Related Terms</h3> + <dt class="similar"> pairs)
# ---------------------------------------------------------------------------

_RELATED_RE = re.compile(
    r'<dt class="similar ordered-list">(.*?)</dt>\s*<dd>(.*?)</dd>', re.S
)


def parse_related_terms(page_html: str) -> list[dict]:
    """Related terms: {"term", "url", "definitions": [str]}."""
    out: list[dict] = []
    for dt, dd in _RELATED_RE.findall(page_html):
        href_m = re.search(r'href="([^"]+)"', dt)
        term = _clean(_html_to_text(dt))
        defs = [_clean(t) for _, t in _LINK_RE.findall(dd)]
        if not defs:
            plain = _html_to_text(dd)
            defs = [plain] if plain else []
        if not term:
            continue
        out.append({
            "term": term,
            "url": (
                href_m.group(1) if href_m and href_m.group(1).startswith("http")
                else BASE + href_m.group(1)
            ) if href_m else None,
            "definitions": defs,
        })
    return out


# ---------------------------------------------------------------------------
# Whole page
# ---------------------------------------------------------------------------

def parse_examples(page_html: str) -> list[dict]:
    """All example sentences on the page (deduped, page order):
    <q lang=tr> - <q lang=en> pairs, then bare <q> examples."""
    out: list[dict] = []
    seen: set[str] = set()
    for tr, en in _Q_PAIR_RE.findall(page_html):
        item = {"tr": _clean(tr), "en": _clean(en)}
        key = item["tr"] + "||" + item["en"]
        if key not in seen:
            seen.add(key)
            out.append(item)
    for q in _Q_SINGLE_RE.findall(page_html):
        text = _clean(q)
        if text and text not in seen:
            seen.add(text)
            out.append({"text": text})
    return out


def parse_word_page(page_html: str, url: str) -> dict:
    """The full word page as one dict (see server.seslisozluk_lookup
    for the field list)."""
    found = is_found(page_html)
    return {
        "word": parse_word(page_html),
        "found": found,
        "url": url,
        "dictionaries": parse_dictionaries(page_html) if found else [],
        "hyphenation": parse_hyphenation(page_html),
        "pronunciation": parse_pronunciation(page_html),
        "turkish_pronunciation": parse_turkish_pronunciation(page_html),
        "etymology": parse_etymology(page_html),
        "tenses": parse_tenses(page_html),
        "synonyms": parse_synonyms(page_html),
        "antonyms": parse_antonyms(page_html),
        "collocations": parse_collocations(page_html),
        "related_terms": parse_related_terms(page_html),
        "audio": parse_audio(page_html),
    }
