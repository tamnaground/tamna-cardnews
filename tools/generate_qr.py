#!/usr/bin/env python3
"""성읍민속마을 안내 웹앱 — 스팟별 QR 코드 + 인쇄용 시트 생성.

사용법:
    python3 tools/generate_qr.py [--base-url URL]

docs/data/spots.js에서 스팟 목록을 읽어 docs/qr/<slug>.png 와
인쇄용 docs/qr/qr-sheet.html 을 생성한다.
"""
import argparse
import json
import sys
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_Q

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
QR_DIR = DOCS / "qr"
DEFAULT_BASE_URL = "https://tamnaground.github.io/tamna-cardnews/"

BRAND = {
    "cream": "#F5EDDF",
    "orange": "#E8622D",
    "ink": "#3E3226",
}


def load_spots():
    """정본 데이터 docs/data/spots.json에서 스팟 목록을 읽는다."""
    src = DOCS / "data" / "spots.json"
    if not src.exists():
        sys.exit("docs/data/spots.json이 없습니다")
    data = json.loads(src.read_text(encoding="utf-8"))
    return sorted(data["spots"], key=lambda s: s.get("order", 0))


def make_qr(url: str, path: Path):
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, box_size=12, border=3)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=BRAND["ink"], back_color="white")
    img.save(path)


def make_sheet(entries, base_url):
    cards = "\n".join(
        f"""  <div class="card">
    <img src="{e['slug']}.png" alt="QR: {e['name_ko']}">
    <div class="name">{e['name_ko']}</div>
    <div class="name-en">{e['name_en']}</div>
    <div class="url">{e['url']}</div>
  </div>"""
        for e in entries
    )
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>성읍민속마을 QR 시트 — 탐라그라운드</title>
<style>
  body {{ font-family: "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
         background: {BRAND['cream']}; color: {BRAND['ink']}; margin: 24px; }}
  h1 {{ text-align: center; font-size: 20px; }}
  .sub {{ text-align: center; font-size: 12px; color: #6B5D4C; margin-bottom: 20px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }}
  .card {{ background: #fff; border: 2px dashed {BRAND['orange']}; border-radius: 14px;
          padding: 14px; text-align: center; page-break-inside: avoid; }}
  .card img {{ width: 100%; max-width: 200px; }}
  .name {{ font-weight: 700; font-size: 15px; margin-top: 6px; }}
  .name-en {{ font-size: 11px; color: #6B5D4C; }}
  .url {{ font-size: 9px; color: #999; word-break: break-all; margin-top: 4px; }}
  @media print {{ body {{ background: #fff; }} }}
</style>
</head>
<body>
<h1>🏝️ 성읍민속마을 다국어 안내 QR</h1>
<div class="sub">기준 URL: {base_url} · 제주어, 같이 지켜요 — 탐라그라운드 @tamnaground</div>
<div class="grid">
{cards}
</div>
</body>
</html>
"""
    (QR_DIR / "qr-sheet.html").write_text(html, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL,
                    help="배포된 웹앱의 기준 URL (끝에 / 포함)")
    args = ap.parse_args()
    base = args.base_url if args.base_url.endswith("/") else args.base_url + "/"

    QR_DIR.mkdir(parents=True, exist_ok=True)
    spots = load_spots()
    entries = []
    for s in spots:
        url = f"{base}?spot={s['slug']}"
        png = QR_DIR / f"{s['slug']}.png"
        make_qr(url, png)
        entries.append({
            "slug": s["slug"],
            "url": url,
            "name_ko": s["i18n"]["ko"]["name"],
            "name_en": s["i18n"].get("en", {}).get("name", s["slug"]),
        })
        print(f"  ✓ {png.relative_to(ROOT)}  →  {url}")

    make_sheet(entries, base)
    print(f"  ✓ {(QR_DIR / 'qr-sheet.html').relative_to(ROOT)}")
    print(f"총 {len(entries)}개 QR 생성 완료")


if __name__ == "__main__":
    main()
