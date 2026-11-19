# seslisozluk-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/seslisozluk-mcp

**Sesli Sözlük** (www.seslisozluk.net) için resmi olmayan, **salt okunur** MCP sunucusu — 1999'dan beri Türkiye'nin çok dilli çevrimiçi sözlüğü (20 milyondan fazla sözcük, 20 dil): **her iki yönde kelime arama** (Türkçe bir kelime Türkçe–İngilizce + Türkçe–Türkçe tanımlar, İngilizce bir kelime İngilizce–Türkçe + İngilizce–İngilizce + ters Türkçe–İngilizce paneli döndürür); **heceleme, IPA telaffuz, Türkçe okunuş, etimoloji, çekimler, eş anlamlılar, zıt anlamlılar, yaygın kullanımlar, ilgili terimler, örnek cümleler** (Türkçe–İngilizce çiftleri) ve **telaffuz sesleri** (İngiliz İngilizcesi / Amerikan İngilizcesi / Avustralya İngilizcesi, Türkçe — static.seslisozluk.net üzerinde MP3).

> "Turkey MCP factory" projesinin bir parçasıdır. Sesli Sözlük ile bağlantısı yoktur. Veriler Sesli Sözlük'ün herkese açık kelime sayfalarından (sunucu tarafında oluşturulan HTML) alınır — giriş yok, API anahtarı yok, salt okunur. Tanımlar kullanıcı katkılı içerik barındırabilir (argo "(Argo)", Osmanlı dönemi girdileri "(Osmanlı Dönemi)" olarak işaretlenir).

## Yapay zekâ ajanları için

- **Arama**: `seslisozluk_lookup` Türkçe veya İngilizce bir kelime ya da ifade alır (`"merhaba"`, `"hello"`, `"merhaba nasılsın"`) ve `found` ile birlikte tüm sözlük panellerini döndürür. Sözlüğün bilmediği bir kelime `found: false` ("sözlükte bulunamadı") ve boş paneller döndürür — sayfanın kendisi yine de HTTP 200 verir.
- **Yön otomatik algılanır**: `"merhaba"` → Türkçe–İngilizce (19 girdi: `hi`, `how do you do?`, `hello!`, …) + Türkçe–Türkçe (6 girdi); `"hello"` → İngilizce–Türkçe (15 girdi, ilki `Merhaba`) + İngilizce–İngilizce (23 girdi) + ters Türkçe–İngilizce paneli.
- **Örnekler**: `seslisozluk_examples` yinelenmeyen cümle çiftlerini döndürür (`{"tr", "en"}`) — `"hello"` için 15 tane; tek dilli örnekler `{"text"}` olarak gelir. Arama da aynı cümleleri her tanımın içinde döndürür.
- **Eş anlamlılar**: `seslisozluk_synonyms` eş anlamlıları, zıt anlamlıları, yaygın kullanımları ve ilgili terimleri döndürür (her birinin kendi Sesli Sözlük URL'si var; ilgili terimler kısa tanımlar da taşır). Boş listeler, o kelime için sayfada böyle bir bölüm olmadığı anlamına gelir — `"merhaba"`nın Eş Anlamlılar bölümü yoktur, `"hello"`nun 15 eş anlamlısı ve 4 zıt anlamlısı vardır.
- **Telaffuz**: `seslisozluk_pronunciation` hecelemeyi (`"mer·ha·ba"`, `"hel·lo"`), IPA'yı (`"/həˈlō/ /həˈloʊ/"`), Türkçe okunuşu (`"hılō"`) ve ses URL'lerini döndürür — İngilizce kelimelerde `uk`/`us`/`au`, Türkçe kelimelerde `tr` (static.seslisozluk.net üzerinde erişilebilirliği doğrulandı).
- Her yanıt `fetched_at` (UTC) ve `source: www.seslisozluk.net` taşır.

## Kurulum

```bash
uvx seslisozluk-mcp
```

Veya MCP istemci yapılandırmanıza ekleyin (ör. Claude Desktop):

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

## Araçlar

| Araç | Ne yapar |
| --- | --- |
| `seslisozluk_lookup` | Tam kelime araması: sözlük panelleri, heceleme, telaffuz, etimoloji, çekimler, eş/zıt anlamlılar, yaygın kullanımlar, ilgili terimler, ses |
| `seslisozluk_examples` | Bir kelimenin örnek cümleleri (Türkçe–İngilizce çiftleri) |
| `seslisozluk_synonyms` | Eş anlamlılar, zıt anlamlılar, yaygın kullanımlar ve ilgili terimler |
| `seslisozluk_pronunciation` | Heceleme, IPA, Türkçe okunuş ve ses URL'leri |
| `seslisozluk_health` | Sesli Sözlük sitesine şu an erişilebiliyor mu? |

## Örnek

`"merhaba"` araması, 19 Kasım 2026:

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

## Dikkat edilecekler

- Kelime sayfası adresi, kelimenin boşlukları tireye çevrilip noktalama işaretleri yüzde-kodlamayla yazılmış hâlidir (`"how do you do?"` → `"how-do-you-do%3F"`, `"merhaba nasılsın"` → `"merhaba-nas%C4%B1ls%C4%B1n"`); araçlar bunu sizin için oluşturur.
- `/tr/` arayüzü doğrulanmamış farklı bir adres düzeni kullanır — araçlar her iki yönü de sunan `/en/` sayfalarını kullanır.
- Sitenin kendi arama formu `/` adresine POST yapar — arama API'si yoktur; arama, kelime sayfası URL'sini doğrudan oluşturur. Sözlüğün bilmediği bir ifade `found: false` döndürür, hata değil.
- Ses URL'leri static.seslisozluk.net üzerinde MP3'tür; İngiliz İngilizcesi / Amerikan İngilizcesi / Avustralya İngilizcesi aksanları İngilizce kelimelerde, `tr` aksanı Türkçe kelimelerde vardır.
- Aktarım, Chrome TLS taklidi ve düz requests yedeği kullanır; istekler ~0,5 sn arayla gönderilir.

## Geliştirme

```bash
python -m venv .venv && .venv/bin/pip install -e . pytest
.venv/bin/python -m pytest tests/test_parse.py -v   # çevrimdışı, kayıtlı örnekler
.venv/bin/python -m pytest tests/test_live.py -v    # canlı, www.seslisozluk.net karşısında
.venv/bin/python tests/smoke_live.py                # günlük CI denetimi
```

## Lisans

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/) — kişisel ve ticari olmayan kullanım için ücretsizdir; ticari kullanım ayrı bir lisans gerektirir.

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
