"""카드뉴스 PNG 세트 생성: python3 build_cards.py [words.json 경로]

words.json → (표지 + 단어당 [뜻/제주어 예문/표준어 예문] + 마무리) HTML → Playwright 스크린샷.
출력: output/<set_id>_<n>.png  (루트의 card_1~5.png 원본 레퍼런스는 건드리지 않는다)
"""
import json
import os
import subprocess
import sys

import card_template as T

os.chdir(os.path.dirname(os.path.abspath(__file__)))

data = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'words.json'))
set_id = data['set_id']

for c in data['cards']:
    for key in ('word', 'meaning', 'example_jeju', 'example_std'):
        assert c.get(key), f"카드에 {key} 누락: {c}"
    if len(c['example_jeju']) > 40 or len(c['example_std']) > 40:
        print(f"경고: 예문이 40자를 넘어 폰트를 줄입니다 — {c['word']}")

n_total = 2 + 3 * len(data['cards'])
pages = [T.cover_html(data['cover'], n_total)]
idx = 2
for c in data['cards']:
    pages.append(T.meaning_html(c, idx, n_total)); idx += 1
    pages.append(T.example_jeju_html(c, idx, n_total)); idx += 1
    pages.append(T.example_std_html(c, idx, n_total)); idx += 1
pages.append(T.outro_html(data.get('outro', {}), n_total))

os.makedirs('output', exist_ok=True)
jobs = []
for n, doc in enumerate(pages, 1):
    html_path = os.path.abspath(f'tmp_card_{n}.html')
    with open(html_path, 'w') as f:
        f.write(doc)
    jobs.append({'html': html_path, 'png': os.path.abspath(f'output/{set_id}_{n}.png')})

with open('tmp_card_jobs.json', 'w') as f:
    json.dump(jobs, f)
subprocess.run(['node', 'shoot.js', 'tmp_card_jobs.json'], check=True)

for job in jobs:
    os.remove(job['html'])
os.remove('tmp_card_jobs.json')
print(f"완료: output/{set_id}_1..{len(pages)}.png ({len(pages)}장)")
