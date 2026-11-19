# seslisozluk-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/seslisozluk-mcp

Unofficial **read-only** MCP server for **Sesli Sözlük** (www.seslisozluk.net) — Türkiye's multilingual online dictionary since 1999 (20M+ words, 20 languages): **word lookup in both directions** (a Turkish word returns Turkish–English + Turkish–Turkish definitions, an English word returns English–Turkish + English–English + the reverse Turkish–English panel), with **hyphenation, IPA pronunciation, Turkish pronunciation, etymology, tenses, synonyms, antonyms, common collocations, related terms, example sentences** (Turkish–English pairs) and **pronunciation audio** (UK/US/AU English, Turkish — MP3 on static.seslisozluk.net).

> Part of the "Turkey MCP factory". Not affiliated with Sesli Sözlük. Data comes from Sesli Sözlük's own public word pages (server-rendered HTML) — no login, no API key, read-only. Definitions can include user-contributed content (slang is marked "(Argo)", Ottoman-era entries "(Osmanlı Dönemi)").

## For AI agents

- **Lookup**: `seslisozluk_lookup` takes a Turkish or English word or phrase (`"merhaba"`, `"hello"`, `"merhaba nasılsın"`) and returns `found` plus every dictionary panel. A word the dictionary does not know returns `found: false` ("sözlükte bulunamadı") with empty panels — the page itself still returns HTTP 200.
- **Direction is auto-detected**: `"merhaba"` → Turkish–English (19 entries: `hi`, `how do you do?`, `hello!`, …) + Turkish–Turkish (6 entries); `"hello"` → English–Turkish (15 entries, first `Merhaba`) + English–English (23 entries) + a reverse Turkish–English panel.
- **Examples**: `seslisozluk_examples` returns the deduplicated sentence pairs (`{"tr", "en"}`) — `"hello"` has 15; bare monolingual examples come back as `{"text"}`. Lookup also returns the same sentences inline with each definition.
- **Synonyms**: `seslisozluk_synonyms` returns synonyms, antonyms, collocations and related terms (each with its own Sesli Sözlük URL; related terms carry short definitions). Empty lists mean the page has no such section for the word — `"merhaba"` has no Synonyms section, `"hello"` has 15 synonyms and 4 antonyms.
- **Pronunciation**: `seslisozluk_pronunciation` returns hyphenation (`"mer·ha·ba"`, `"hel·lo"`), the IPA (`"/həˈlō/ /həˈloʊ/"`), the Turkish pronunciation spelling (`"hılō"`) and the audio URLs — `uk`/`us`/`au` for English words, `tr` for Turkish ones (verified reachable on static.seslisozluk.net).
- Every response carries `fetched_at` (UTC) and `source: www.seslisozluk.net`.

## Install

```bash
uvx seslisozluk-mcp
```

Or add to your MCP client config (e.g. Claude Desktop):

```json
{
  "mcpServers": {
    "seslisozluk": {
      "command": "uvx",
      "args": ["seslisozluk-mcp"]
    }
  }
}
```

## Tools

| Tool | What it does |
| --- | --- |
| `seslisozluk_lookup` | Full word lookup: dictionary panels, hyphenation, pronunciation, etymology, tenses, synonyms, antonyms, collocations, related terms, audio |
| `seslisozluk_examples` | Example sentences for a word (Turkish–English pairs) |
| `seslisozluk_synonyms` | Synonyms, antonyms, common collocations and related terms |
| `seslisozluk_pronunciation` | Hyphenation, IPA, Turkish pronunciation and audio URLs |
| `seslisozluk_health` | Is Sesli Sözlük's site reachable right now? |

## Example

Lookup of `"merhaba"`, 19 November 2026:

```json
{ "word": "merhaba", "found": true,
  "url": "https://www.seslisozluk.net/en/what-is-the-meaning-of-merhaba/",
  "dictionaries": [
    { "name": "Turkish English", "entries": [
      { "text": "hi", "url": "https://www.seslisozluk.net/en/what-is-the-meaning-of-hi/" },
      { "text": "hello", "url": "https://www.seslisozluk.net/en/what-is-the-meaning-of-hello/",
        "examples": [
          { "tr": "Hello, I have a reservation, my name is Kaori Yoshikawa. Here is the confirmation card.",
            "en": "Merhaba, benim bir rezervasyonum var, adım Kaori Yoshikawa. İşte onay kartı." } ] } ] },
    { "name": "Turkish Turkish", "entries": [
      { "category": "(Osmanlı Dönemi)",
        "text": "Müslümanlar arasında bir nevi selâmlaşma kelimesi olup, \"rahat olunuz, serbest olun, hoş geldiniz\" mânasında söylenir" } ] } ],
  "hyphenation": "mer·ha·ba",
  "collocations": [ { "text": "merhaba askim" }, { "text": "merhaba canim" } ],
  "audio": [ { "accent": "tr",
    "url": "https://static.seslisozluk.net/listen/f/fff25e14af3ee1c6b166172cf19c3823.mp3" } ] }
```

## Caveats

- The word-page slug is the word with spaces turned into hyphens and punctuation percent-encoded (`"how do you do?"` → `"how-do-you-do%3F"`, `"merhaba nasılsın"` → `"merhaba-nas%C4%B1ls%C4%B1n"`); the tools build it for you.
- The `/tr/` UI uses a different slug pattern that is unverified — the tools use the `/en/` pages, which serve both directions.
- The site's own search form POSTs to `/` — there is no search API; lookup builds the word-page URL directly. A phrase the dictionary does not know returns `found: false`, not an error.
- Audio URLs are MP3s on static.seslisozluk.net; the UK/US/AU accents exist for English words, the `tr` accent for Turkish ones.
- Transport uses Chrome TLS impersonation with a plain-requests fallback; requests are spaced ~0.5s apart.

## Development

```bash
python -m venv .venv && .venv/bin/pip install -e . pytest
.venv/bin/python -m pytest tests/test_parse.py -v   # offline, recorded fixtures
.venv/bin/python -m pytest tests/test_live.py -v    # live, against www.seslisozluk.net
.venv/bin/python tests/smoke_live.py                # daily CI probe
```

## License

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/) — free for personal and non-commercial use; commercial use needs a separate license.

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
