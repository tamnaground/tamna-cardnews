"""Generate scene.html for the 'Jeju samchons talk about rain' video from timeline.json."""
import json, math, os, random

os.chdir(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open('timeline.json'))
TOTAL = T['total']
OUTRO = T['outro_start']

# ---- per-line CSS: bubbles, subtitles, mouth talk animations ----
bubble_css, bubble_html, sub_css, sub_html = [], [], [], []
talk_anims = {'halmang': [], 'harbang': []}
bob_anims = {'halmang': [], 'harbang': []}

for L in T['lines']:
    i, spk, start, dur = L['i'], L['speaker'], L['start'], L['dur']
    end = start + dur + 0.55
    side = 'left' if spk == 'halmang' else 'right'
    bubble_css.append(f"""
  #b{i} {{ animation: bubbleIn 0.45s {start - 0.25:.2f}s cubic-bezier(.2,1.5,.4,1) both,
           bubbleOut 0.4s {end:.2f}s ease-in forwards; }}""")
    bubble_html.append(
        f'<div class="bubble {side}" id="b{i}"><span>{L["jeju"]}</span><div class="tail"></div></div>')
    sub_css.append(f"""
  #sub{i} {{ animation: fadeUp 0.4s {start - 0.1:.2f}s ease-out both, bubbleOut 0.35s {end:.2f}s ease-in forwards; }}""")
    sub_html.append(f'<div class="subtitle" id="sub{i}">{L["std"]}</div>')
    reps = max(int(math.ceil(dur / 0.30)), 3)
    talk_anims[spk].append(f'talk 0.30s {start:.2f}s {reps}')
    bob_anims[spk].append(f'bob 0.6s {start:.2f}s {max(int(math.ceil(dur / 0.6)), 2)}')

talk_css = "\n".join(
    f'  #{spk} .mouth {{ animation: {", ".join(a)}; transform-origin: center; }}\n'
    f'  #{spk} .figure {{ animation: {", ".join(bob_anims[spk])}; transform-origin: 50% 100%; }}'
    for spk, a in talk_anims.items())

# ---- rain drops (deterministic) ----
rng = random.Random(42)
drops = []
for k in range(90):
    x = rng.uniform(0, 1080)
    d = rng.uniform(0.75, 1.35)          # fall duration
    delay = -rng.uniform(0, 1.35)        # negative → already mid-fall at t=0
    h = rng.uniform(46, 90)
    op = rng.uniform(0.25, 0.55)
    w = 5 if rng.random() < 0.25 else 4
    drops.append(f'<i style="left:{x:.0f}px;height:{h:.0f}px;width:{w}px;opacity:{op:.2f};'
                 f'animation-duration:{d:.2f}s;animation-delay:{delay:.2f}s"></i>')
rain_html = "\n".join(drops)

html = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<style>
  @font-face {{ font-family: 'Noto Sans KR'; src: url('NotoSansKR.ttf') format('truetype'); font-weight: 100 900; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:1080px; height:1920px; overflow:hidden; }}
  body {{ font-family:'Noto Sans KR', sans-serif; background:linear-gradient(#5B6B7E 0%, #77879B 46%, #8B99A9 62%); position:relative; }}

  /* ---------- environment ---------- */
  .cloud {{ position:absolute; background:#4E5D6F; border-radius:999px; filter:blur(2px); }}
  .cloud.c1 {{ width:620px; height:150px; left:-80px; top:120px; animation: drift 9s ease-in-out infinite alternate; }}
  .cloud.c2 {{ width:540px; height:130px; right:-100px; top:280px; opacity:.8; animation: drift 11s ease-in-out infinite alternate-reverse; }}
  .cloud.c3 {{ width:380px; height:100px; left:240px; top:420px; opacity:.65; animation: drift 13s ease-in-out infinite alternate; }}
  @keyframes drift {{ from {{ transform: translateX(0); }} to {{ transform: translateX(60px); }} }}

  .ground {{ position:absolute; left:0; right:0; bottom:0; height:340px; background:#4E5A46; }}

  /* thatched house */
  .house {{ position:absolute; left:110px; bottom:300px; width:860px; height:560px; }}
  .roof {{ position:absolute; left:0; top:0; width:860px; height:300px; background:#B99457; border-radius:50% 50% 6% 6% / 90% 90% 6% 6%; box-shadow: inset 0 -26px 0 #A5834C; }}
  .roofline {{ position:absolute; top:150px; left:60px; right:60px; height:0; border-top:5px solid rgba(90,70,40,.35); border-radius:50%; }}
  .wall {{ position:absolute; left:70px; top:290px; width:720px; height:270px; background:#8A7A63; }}
  .door {{ position:absolute; left:300px; top:340px; width:180px; height:220px; background:#5C4A33; border-radius:10px 10px 0 0; box-shadow: inset 0 0 0 10px #4A3B28; }}
  .stone {{ position:absolute; border-radius:46%; background:#4B4F55; }}

  /* rain */
  .rain {{ position:absolute; inset:0; overflow:hidden; }}
  .rain i {{ position:absolute; top:-100px; background:linear-gradient(rgba(220,235,255,0), rgba(220,235,255,.9)); border-radius:3px; animation-name: fall; animation-iteration-count: infinite; animation-timing-function: linear; }}
  @keyframes fall {{ to {{ transform: translateY(2120px); }} }}

  /* ---------- characters ---------- */
  .who {{ position:absolute; bottom:150px; width:420px; height:560px; }}
  #halmang {{ left:100px; }}
  #harbang {{ right:100px; }}
  .figure {{ width:100%; height:100%; }}
  @keyframes talk {{ 0%,100% {{ transform: scaleY(0.25); }} 50% {{ transform: scaleY(1); }} }}
  @keyframes bob  {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px); }} }}
{talk_css}
  .blink {{ animation: blink 3.7s linear infinite; transform-origin: center; }}
  #harbang .blink {{ animation-delay: 1.8s; }}
  @keyframes blink {{ 0%, 92%, 100% {{ transform: scaleY(1); }} 95% {{ transform: scaleY(0.08); }} }}

  /* ---------- speech bubbles / subtitles ---------- */
  .bubble {{ position:absolute; bottom:760px; max-width:660px; background:#FFFDF6; border-radius:36px; padding:34px 44px; box-shadow:0 12px 34px rgba(20,30,45,.35); }}
  .bubble span {{ font-size:56px; font-weight:800; color:#2B3327; letter-spacing:-1px; line-height:1.35; }}
  .bubble .tail {{ position:absolute; bottom:-26px; width:0; height:0; border-left:24px solid transparent; border-right:24px solid transparent; border-top:30px solid #FFFDF6; }}
  .bubble.left {{ left:80px; }} .bubble.left .tail {{ left:120px; }}
  .bubble.right {{ right:80px; }} .bubble.right .tail {{ right:120px; }}
  @keyframes bubbleIn {{ from {{ opacity:0; transform:scale(.4) translateY(40px); }} to {{ opacity:1; transform:scale(1) translateY(0); }} }}
  @keyframes bubbleOut {{ from {{ opacity:1; }} to {{ opacity:0; }} }}
{"".join(bubble_css)}

  .subtitle {{ position:absolute; bottom:56px; left:50%; transform:translateX(-50%); white-space:nowrap; background:rgba(20,28,38,.72); color:#EAF0F6; font-size:44px; font-weight:500; padding:18px 46px; border-radius:ars 999px; border-radius:999px; }}
{"".join(sub_css)}
  @keyframes fadeUp {{ from {{ opacity:0; transform:translateX(-50%) translateY(30px); }} to {{ opacity:1; transform:translateX(-50%) translateY(0); }} }}

  /* ---------- intro / outro ---------- */
  .card {{ position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; }}
  #intro {{ background:rgba(30,40,52,.55); animation: introVis {TOTAL}s linear both; }}
  @keyframes introVis {{ 0%,{(T['intro'] - 0.6) / TOTAL * 100:.2f}% {{ opacity:1; }} {T['intro'] / TOTAL * 100:.2f}%,100% {{ opacity:0; }} }}
  #intro .t1 {{ font-size:120px; font-weight:900; color:#fff; letter-spacing:-2px; text-shadow:0 6px 24px rgba(0,0,0,.4); animation: fadeUp2 .8s .2s both; }}
  #intro .t2 {{ font-size:52px; font-weight:500; color:#D7E3F0; margin-top:34px; animation: fadeUp2 .8s .55s both; }}
  #outro {{ background:rgba(24,34,46,.78); animation: outroVis {TOTAL}s linear both; }}
  @keyframes outroVis {{ 0%,{OUTRO / TOTAL * 100:.2f}% {{ opacity:0; }} {(OUTRO + 0.8) / TOTAL * 100:.2f}%,100% {{ opacity:1; }} }}
  #outro .t1 {{ font-size:96px; font-weight:900; color:#fff; letter-spacing:-2px; animation: fadeUp2 .8s {OUTRO + 0.5:.2f}s both; }}
  #outro .t2 {{ font-size:64px; font-weight:700; color:#FFCC5C; margin-top:40px; animation: fadeUp2 .8s {OUTRO + 0.9:.2f}s both; }}
  #outro .t3 {{ font-size:46px; font-weight:500; color:#B9C7D6; margin-top:60px; animation: fadeUp2 .8s {OUTRO + 1.3:.2f}s both; }}
  @keyframes fadeUp2 {{ from {{ opacity:0; transform:translateY(46px); }} to {{ opacity:1; transform:translateY(0); }} }}
</style></head>
<body>
  <div class="cloud c1"></div><div class="cloud c2"></div><div class="cloud c3"></div>

  <div class="house">
    <div class="wall"></div><div class="door"></div>
    <div class="roof"></div><div class="roofline"></div>
  </div>
  <div class="ground"></div>
  <div id="stones"></div>

  <!-- halmang (grandma) -->
  <div class="who" id="halmang"><svg class="figure" viewBox="0 0 420 560">
    <ellipse cx="210" cy="548" rx="150" ry="12" fill="rgba(0,0,0,.25)"/>
    <path d="M110 560 L110 380 Q110 320 210 320 Q310 320 310 380 L310 560 Z" fill="#8A6FA8"/>
    <circle cx="160" cy="430" r="9" fill="#F2A9C4"/><circle cx="250" cy="470" r="9" fill="#F2A9C4"/><circle cx="205" cy="510" r="9" fill="#F7C873"/>
    <circle cx="210" cy="210" r="118" fill="#F6D7B8"/>
    <path d="M100 180 Q110 90 210 90 Q310 90 320 180 Q290 150 210 150 Q130 150 100 180 Z" fill="#C9CDD3"/>
    <circle cx="210" cy="78" r="34" fill="#C9CDD3"/>
    <g class="blink"><circle cx="168" cy="205" r="11" fill="#333"/><circle cx="252" cy="205" r="11" fill="#333"/></g>
    <circle cx="140" cy="245" r="16" fill="#F2A9C4" opacity=".75"/><circle cx="280" cy="245" r="16" fill="#F2A9C4" opacity=".75"/>
    <ellipse class="mouth" cx="210" cy="262" rx="20" ry="14" fill="#B0483F"/>
  </svg></div>

  <!-- harbang (grandpa) -->
  <div class="who" id="harbang"><svg class="figure" viewBox="0 0 420 560">
    <ellipse cx="210" cy="548" rx="150" ry="12" fill="rgba(0,0,0,.25)"/>
    <path d="M110 560 L110 380 Q110 320 210 320 Q310 320 310 380 L310 560 Z" fill="#4A5A6A"/>
    <rect x="196" y="330" width="28" height="150" fill="#3C4B59"/>
    <circle cx="210" cy="215" r="112" fill="#EFC9A5"/>
    <path d="M92 190 Q100 96 210 96 Q320 96 328 190 L328 204 Q210 176 92 204 Z" fill="#7A6A55"/>
    <rect x="80" y="188" width="260" height="26" rx="13" fill="#6B5D4A"/>
    <g class="blink"><circle cx="170" cy="218" r="11" fill="#333"/><circle cx="250" cy="218" r="11" fill="#333"/></g>
    <path d="M160 262 Q210 246 260 262 Q210 274 160 262 Z" fill="#D8DCE0"/>
    <ellipse class="mouth" cx="210" cy="286" rx="18" ry="12" fill="#8E4038"/>
  </svg></div>

  <div class="rain">
{rain_html}
  </div>

{"".join(bubble_html)}
{"".join(sub_html)}

  <div class="card" id="intro"><div class="t1">비 오는 날,<br>제주 삼춘들</div><div class="t2">제주어로 듣는 일상 대화</div></div>
  <div class="card" id="outro"><div class="t1">제주어, 같이 지켜요</div><div class="t2">탐라그라운드</div><div class="t3">@tamnaground</div></div>

<script>
  // stone wall (doldam)
  const rng = (function(){{ let s = 7; return () => (s = (s * 16807) % 2147483647) / 2147483647; }})();
  const st = document.getElementById('stones');
  for (let r = 0; r < 2; r++) for (let k = 0; k < 9; k++) {{
    const d = document.createElement('div');
    d.className = 'stone';
    const w = 96 + rng() * 44, h = 62 + rng() * 22;
    d.style.width = w + 'px'; d.style.height = h + 'px';
    d.style.left = (k * 122 + (r % 2) * 52 - 30 + rng() * 14) + 'px';
    d.style.bottom = (250 + r * 62) + 'px';
    d.style.background = ['#565D66','#616870','#4B525A'][Math.floor(rng() * 3)];
    document.body.insertBefore(d, document.querySelector('.rain'));
  }}
  window.seek = function (ms) {{
    document.getAnimations().forEach(a => {{ a.pause(); a.currentTime = ms; }});
  }};
  window.seek(0);
</script>
</body></html>
"""
with open('scene.html', 'w') as f:
    f.write(html)
print('scene.html written, total =', TOTAL)
