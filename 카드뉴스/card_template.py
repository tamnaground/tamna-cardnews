"""카드 1장의 HTML 문서를 만드는 템플릿 함수들 (1080x1350, 브랜드 팔레트).

card_1~5.png(오늘의 제주어: 고장)의 레이아웃을 따른다:
표지 → [뜻 → 제주어 예문 → 표준어 예문] × 단어 수 → 마무리
"""
import html as html_mod
import os

PALETTE = {
    'cream': '#F5EDDF', 'orange': '#E8622D', 'yellow': '#FFCC5C', 'yellow2': '#F7C873',
    'green': '#2F7A3D', 'green2': '#BCD9A0', 'blue': '#1D5BB8', 'blue2': '#2563AC',
    'pink': '#F2A9C4', 'text': '#3E3226',
}
# 예문 카드용 옅은 배경
PALE = {'green': '#EAF1E2', 'blue': '#E7EDF5', 'cream': PALETTE['cream']}

FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '샘플영상', 'NotoSansKR.ttf')

# 밝은 배경 → 갈색 글자, 어두운 배경 → 흰 글자 (임의 판단 금지)
LIGHT_BG = {'cream', 'yellow', 'yellow2', 'green2', 'pink'} | set(PALE)


def text_color(bg_key):
    return PALETTE['text'] if bg_key in LIGHT_BG else '#FFFFFF'


def flower(color_key, size=110, x='0', y='0'):
    """6잎 꽃 모티프 (브랜드 규칙)."""
    c = PALETTE[color_key]
    petals = ''.join(
        f'<circle cx="{50 + 30 * __import__("math").cos(__import__("math").radians(a)):.1f}" '
        f'cy="{50 + 30 * __import__("math").sin(__import__("math").radians(a)):.1f}" r="22" fill="{c}"/>'
        for a in range(0, 360, 60))
    return (f'<svg style="position:absolute;left:{x};top:{y};" width="{size}" height="{size}" viewBox="0 0 100 100">'
            f'{petals}<circle cx="50" cy="50" r="14" fill="{PALETTE["orange"]}"/></svg>')


def _doc(bg, body, dotted=True, dot_color='rgba(140,120,90,.35)'):
    font = os.path.abspath(FONT_PATH)
    assert os.path.exists(font), f'폰트 없음: {font} (SKILL.md 환경 준비 참고)'
    dots = (f'<div style="position:absolute;inset:44px;border-radius:8px;'
            f'border:14px dotted {dot_color};"></div>') if dotted else ''
    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<style>
  @font-face {{ font-family: 'Noto Sans KR'; src: url('file://{font}') format('truetype'); font-weight: 100 900; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:1080px; height:1350px; overflow:hidden; }}
  body {{ font-family:'Noto Sans KR', sans-serif; background:{bg}; position:relative;
         word-break:keep-all; overflow-wrap:break-word; }}
  .pill {{ display:inline-block; padding:16px 52px; border-radius:999px; font-size:46px; font-weight:700; }}
  .center {{ position:absolute; inset:0; display:flex; flex-direction:column; align-items:center;
             justify-content:center; text-align:center; }}
  .footer {{ position:absolute; bottom:64px; left:0; right:0; text-align:center; }}
  .pager {{ font-size:38px; font-weight:500; opacity:.55; }}
  .handle {{ font-size:44px; font-weight:800; opacity:.65; }}
</style></head>
<body>
{dots}
{body}
</body></html>"""


def cover_html(cover, n_total):
    word = html_mod.escape(cover['word'])
    title = html_mod.escape(cover['title'])
    hint = html_mod.escape(cover.get('hint', '이게 무슨 뜻일까?'))
    body = f"""
  <div style="position:absolute;top:0;left:0;right:0;height:130px;background:{PALETTE['orange']};
       display:flex;align-items:center;justify-content:center;">
    <span style="font-size:54px;font-weight:800;color:#fff;">{title}</span></div>
  {flower('pink', 130, '120px', '260px')}{flower('yellow2', 110, '830px', '300px')}{flower('green2', 90, '500px', '210px')}
  <div class="center">
    <span style="font-size:230px;font-weight:900;color:{PALETTE['yellow']};
      text-shadow:-6px -6px 0 {PALETTE['text']},6px -6px 0 {PALETTE['text']},-6px 6px 0 {PALETTE['text']},6px 6px 0 {PALETTE['text']};
      border-bottom:16px solid {PALETTE['orange']};padding:0 30px 10px;">{word}</span></div>
  <div style="position:absolute;bottom:220px;left:0;right:0;text-align:center;
       font-size:52px;font-weight:600;color:{PALETTE['text']};">{hint}</div>
  <div style="position:absolute;bottom:0;left:0;right:0;height:130px;background:{PALETTE['green']};
       display:flex;align-items:center;justify-content:center;">
    <span style="font-size:46px;font-weight:800;color:#fff;">@tamnaground</span></div>"""
    return _doc(PALETTE['cream'], body, dotted=False)


def meaning_html(card, idx, n_total):
    word = html_mod.escape(card['word'])
    meaning = html_mod.escape(card['meaning'])
    body = f"""
  {flower('pink', 120, '130px', '150px')}{flower('green2', 100, '500px', '130px')}{flower('yellow2', 110, '840px', '160px')}
  <div style="position:absolute;top:310px;left:0;right:0;text-align:center;">
    <span class="pill" style="background:{PALETTE['blue']};color:#fff;">뜻</span></div>
  <div class="center">
    <div style="font-size:170px;font-weight:900;color:{PALETTE['orange']};">{word}</div>
    <div style="font-size:120px;font-weight:800;color:{PALETTE['text']};margin-top:40px;">= {meaning}</div></div>
  <div class="footer" style="color:{PALETTE['text']};">
    <div class="pager">{idx} / {n_total}</div><div class="handle">@tamnaground</div></div>"""
    return _doc(PALETTE['cream'], body)


def _example_html(sentence, pill_text, pill_color, bg, idx, n_total):
    s = html_mod.escape(sentence)
    size = 66 if len(sentence) <= 22 else 56
    body = f"""
  {flower('pink', 110, '120px', '150px')}{flower('yellow2', 100, '850px', '160px')}
  <div style="position:absolute;top:300px;left:0;right:0;text-align:center;">
    <span class="pill" style="background:{pill_color};color:#fff;">{html_mod.escape(pill_text)}</span></div>
  <div class="center" style="padding:0 110px;">
    <div style="font-size:150px;font-weight:900;color:{PALETTE['green2']};
         align-self:flex-start;margin-left:40px;line-height:.4;">&ldquo;</div>
    <div style="font-size:{size}px;font-weight:800;color:{PALETTE['text']};line-height:1.5;">{s}</div></div>
  <div class="footer" style="color:{PALETTE['text']};">
    <div class="pager">{idx} / {n_total}</div><div class="handle">@tamnaground</div></div>"""
    return _doc(bg, body, dot_color='rgba(120,140,110,.35)')


def example_jeju_html(card, idx, n_total):
    return _example_html(card['example_jeju'], '제주어로 말해보기', PALETTE['green'], PALE['green'], idx, n_total)


def example_std_html(card, idx, n_total):
    return _example_html(card['example_std'], '표준어로는?', PALETTE['blue'], PALE['blue'], idx, n_total)


def outro_html(outro, n_total):
    msg = html_mod.escape(outro.get('message', '제주어, 같이 지켜요'))
    brand = html_mod.escape(outro.get('brand', '탐라그라운드'))
    cta = html_mod.escape(outro.get('cta', '팔로우하고 매주 제주어 배우기'))
    body = f"""
  {flower('yellow2', 120, '130px', '150px')}{flower('green2', 100, '500px', '140px')}{flower('pink', 120, '840px', '150px')}
  <div class="center">
    <div style="font-size:80px;font-weight:700;color:#fff;">{msg}</div>
    <div style="font-size:120px;font-weight:900;color:#fff;margin-top:36px;">{brand}</div>
    <div style="margin-top:56px;">{flower('yellow2', 80, '0', '0').replace('position:absolute;left:0;top:0;', 'vertical-align:middle;')}</div>
    <div style="margin-top:70px;"><span class="pill" style="background:#fff;color:{PALETTE['blue2']};font-size:42px;">{cta}</span></div></div>
  <div class="footer" style="color:#fff;">
    <div class="handle" style="opacity:.95;">@tamnaground</div><div class="pager" style="color:#fff;opacity:.7;">{n_total} / {n_total}</div></div>"""
    return _doc(PALETTE['blue2'], body, dot_color='rgba(255,255,255,.3)')
