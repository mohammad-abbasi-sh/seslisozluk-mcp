# seslisozluk-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/seslisozluk-mcp

سرور MCP غیررسمی و **فقط‌خواندنی** برای **Sesli Sözlük** (فرهنگ لغت چندزبانهٔ آنلاین ترکیه از سال ۱۹۹۹، www.seslisozluk.net — بیش از ۲۰ میلیون واژه، ۲۰ زبان): **جست‌وجوی واژه در هر دو جهت** (واژهٔ ترکی، تعریف‌های ترکی–انگلیسی + ترکی–ترکی برمی‌گرداند؛ واژهٔ انگلیسی، تعریف‌های انگلیسی–ترکی + انگلیسی–انگلیسی + پنل معکوس ترکی–انگلیسی)، همراه با **بخش‌بندی هجایی، تلفظ IPA، تلفظ ترکی، ریشه‌شناسی، صرف‌ها، مترادف‌ها، متضادها، ترکیب‌های رایج، واژه‌های مرتبط، جمله‌های نمونه** (جفت‌های ترکی–انگلیسی) و **صدای تلفظ** (انگلیسی بریتانیایی/آمریکایی/استرالیایی و ترکی — MP3 در static.seslisozluk.net).

> بخشی از پروژهٔ «کارخانهٔ MCP ترکیه». وابسته به Sesli Sözlük نیست. داده‌ها از صفحات عمومی واژه‌های خود Sesli Sözlük (HTML سمت سرور) گرفته می‌شوند — بدون ورود، بدون کلید API، فقط‌خواندنی. تعریف‌ها می‌توانند محتوای مشارکتی کاربران باشند (عامیانه با «(Argo)» و مدخل‌های دورهٔ عثمانی با «(Osmanlı Dönemi)» مشخص شده‌اند).

## برای ایجنت‌های هوش مصنوعی

- **جست‌وجو**: `seslisozluk_lookup` یک واژه یا عبارت ترکی یا انگلیسی می‌گیرد (`"merhaba"`، `"hello"`، `"merhaba nasılsın"`) و `found` را همراه با همهٔ پنل‌های فرهنگ لغت برمی‌گرداند. واژه‌ای که فرهنگ لغت نمی‌شناسد، `found: false` («sözlükte bulunamadı») با پنل‌های خالی برمی‌گرداند — خود صفحه همچنان HTTP 200 می‌دهد.
- **جهت به‌صورت خودکار تشخیص داده می‌شود**: `"merhaba"` ← ترکی–انگلیسی (۱۹ مدخل: `hi`، `how do you do?`، `hello!`، …) + ترکی–ترکی (۶ مدخل)؛ `"hello"` ← انگلیسی–ترکی (۱۵ مدخل، اولی `Merhaba`) + انگلیسی–انگلیسی (۲۳ مدخل) + پنل معکوس ترکی–انگلیسی.
- **نمونه‌ها**: `seslisozluk_examples` جمله‌های نمونهٔ بدون تکرار را به‌صورت جفت (`{"tr", "en"}`) برمی‌گرداند — برای `"hello"` تعداد ۱۵؛ نمونه‌های تک‌زبانه به‌صورت `{"text"}` می‌آیند. جست‌وجو هم همین جمله‌ها را در کنار هر تعریف برمی‌گرداند.
- **مترادف‌ها**: `seslisozluk_synonyms` مترادف‌ها، متضادها، ترکیب‌های رایج و واژه‌های مرتبط را برمی‌گرداند (هر یک با URL خودش در Sesli Sözlük؛ واژه‌های مرتبط تعریف‌های کوتاه هم دارند). فهرست خالی یعنی صفحه برای آن واژه چنین بخشی ندارد — `"merhaba"` بخش مترادف ندارد و `"hello"` دارای ۱۵ مترادف و ۴ متضاد است.
- **تلفظ**: `seslisozluk_pronunciation` بخش‌بندی هجایی (`"mer·ha·ba"`، `"hel·lo"`)، IPA (`"/həˈlō/ /həˈloʊ/"`)، تلفظ ترکی (`"hılō"`) و URLهای صوتی را برمی‌گرداند — برای واژه‌های انگلیسی `uk`/`us`/`au` و برای واژه‌های ترکی `tr` (دسترسی‌پذیری در static.seslisozluk.net بررسی شده است).
- هر پاسخ شامل `fetched_at` (UTC) و `source: www.seslisozluk.net` است.

## نصب

```bash
uvx seslisozluk-mcp
```

یا به پیکربندی کلاینت MCP خود اضافه کنید (مثلاً Claude Desktop):

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

## ابزارها

| ابزار | کارکرد |
| --- | --- |
| `seslisozluk_lookup` | جست‌وجوی کامل واژه: پنل‌های فرهنگ لغت، بخش‌بندی هجایی، تلفظ، ریشه‌شناسی، صرف‌ها، مترادف/متضاد، ترکیب‌های رایج، واژه‌های مرتبط، صدا |
| `seslisozluk_examples` | جمله‌های نمونهٔ یک واژه (جفت‌های ترکی–انگلیسی) |
| `seslisozluk_synonyms` | مترادف‌ها، متضادها، ترکیب‌های رایج و واژه‌های مرتبط |
| `seslisozluk_pronunciation` | بخش‌بندی هجایی، IPA، تلفظ ترکی و URLهای صوتی |
| `seslisozluk_health` | آیا سایت Sesli Sözlük در حال حاضر در دسترس است؟ |

## مثال

جست‌وجوی `"merhaba"`، ۱۹ نوامبر ۲۰۲۶:

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

## نکات

- اسلاگ صفحهٔ واژه، واژه‌ای است که فاصله‌هایش به خط تیره تبدیل و علائم نگارشی‌اش درصد-کدگذاری شده‌اند (`"how do you do?"` ← `"how-do-you-do%3F"` و `"merhaba nasılsın"` ← `"merhaba-nas%C4%B1ls%C4%B1n"`)؛ ابزارها این کار را برای شما انجام می‌دهند.
- رابط `/tr/` الگوی اسلاگ متفاوتی دارد که بررسی نشده است — ابزارها از صفحات `/en/` استفاده می‌کنند که هر دو جهت را پوشش می‌دهند.
- فرم جست‌وجوی خود سایت به `/` پست می‌کند — هیچ API جست‌وجویی وجود ندارد؛ جست‌وجو URL صفحهٔ واژه را مستقیم می‌سازد. عبارتی که فرهنگ لغت نمی‌شناسد `found: false` برمی‌گرداند، نه خطا.
- URLهای صوتی، MP3 در static.seslisozluk.net هستند؛ لهجه‌های بریتانیایی/آمریکایی/استرالیایی برای واژه‌های انگلیسی و لهجهٔ `tr` برای واژه‌های ترکی وجود دارد.
- انتقال داده با جعل TLS کروم و پشتیبان requests ساده انجام می‌شود؛ درخواست‌ها با فاصلهٔ حدود ۰٫۵ ثانیه فرستاده می‌شوند.

## توسعه

```bash
python -m venv .venv && .venv/bin/pip install -e . pytest
.venv/bin/python -m pytest tests/test_parse.py -v   # آفلاین، با نمونه‌های ضبط‌شده
.venv/bin/python -m pytest tests/test_live.py -v    # زنده، در برابر www.seslisozluk.net
.venv/bin/python tests/smoke_live.py                # بررسی روزانهٔ CI
```

## مجوز

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/) — برای استفادهٔ شخصی و غیرتجاری رایگان است؛ استفادهٔ تجاری نیازمند مجوز جداگانه است.

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
