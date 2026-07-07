#!/usr/bin/env python3
"""docs/data/spots.json (정본) → docs/data/spots.js (앱 로드용) 생성."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "data" / "spots.json"
DST = ROOT / "docs" / "data" / "spots.js"


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    n = len(data.get("spots", []))
    langs = {"je", "ko", "en", "zh", "ja", "es"}
    for s in data["spots"]:
        missing = langs - set(s.get("i18n", {}).keys())
        if missing:
            raise SystemExit(f"스팟 '{s.get('slug')}'에 언어 누락: {sorted(missing)}")
    js = ("/* 자동 생성 파일 — 수정은 spots.json에서 하고 tools/build_spots_js.py 실행 */\n"
          "window.SPOTS_DATA = "
          + json.dumps(data, ensure_ascii=False, indent=2)
          + ";\n")
    DST.write_text(js, encoding="utf-8")
    print(f"✓ {DST.relative_to(ROOT)} 생성 (스팟 {n}개)")


if __name__ == "__main__":
    main()
