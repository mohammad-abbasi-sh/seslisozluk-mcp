"""Daily smoke probe (CI): lookup + pronunciation + health.

Run with:  python tests/smoke_live.py
Exit 0 = site reachable, exit 1 = blocked/error (visible in CI).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from seslisozluk_mcp.server import (  # noqa: E402
    seslisozluk_health,
    seslisozluk_lookup,
    seslisozluk_pronunciation,
)


def main() -> int:
    try:
        out = json.loads(seslisozluk_lookup("merhaba"))
        assert "error" not in out, out.get("error")
        assert out["found"] is True
        tr_en = next(
            d for d in out["dictionaries"] if d["name"] == "Turkish English"
        )
        assert tr_en["entries"][0]["text"] == "hi"
        pron = json.loads(seslisozluk_pronunciation("hello"))
        assert "error" not in pron, pron.get("error")
        assert pron["hyphenation"] == "hel·lo"
        assert len(pron["audio"]) == 3
        health = json.loads(seslisozluk_health())
        assert health["status"] == "ok", health
        print(
            f"SMOKE OK: merhaba -> {tr_en['entries'][0]['text']} | "
            f"hello audio={len(pron['audio'])} accents"
        )
        return 0
    except Exception as e:  # noqa: BLE001 — smoke must report, not crash
        print(f"SMOKE FAIL: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
