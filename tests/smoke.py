"""冒烟测试：新开 auto 会话，按给定输入逐轮生成，等下一轮首帧后再发，存两段视频。用法：python3 tests/smoke.py"""
import json, time, sys
from pathlib import Path
from urllib import request as U
D = Path(__file__).resolve().parent.parent; K = (D / 'token.txt').read_text().strip(); API = 'http://127.0.0.1:8901'
op = U.build_opener(U.ProxyHandler({}))
def call(p, b=None):
    q = U.Request(API + p, data=json.dumps(dict(b, k=K)).encode() if b is not None else None, headers={'Content-Type': 'application/json'}, method='POST' if b is not None else 'GET')
    with op.open(q, timeout=60) as r: return json.loads(r.read())
STEPS = [('option', 'A'), ('free', '嗯'), ('free', '带我去你店里看看'), ('free', '吻我')]
s = call('/api/session', {'mode': 'auto'}); sid = s['sid']; print(sid, json.dumps(s['next'], ensure_ascii=False)[:200], flush=True)
out = D / 'tests' / sid; out.mkdir(exist_ok=True); rows = []
for n, (kind, v) in enumerate(STEPS, 1):
    b = {'sid': sid, 'kind': kind, 'choice': v} if kind == 'option' else {'sid': sid, 'kind': kind, 'input': v}
    t0 = time.time(); rid = call('/api/round', b)['id']
    while True:
        r = call(f'/api/round/{rid}?k={K}')
        if r['status'] in ('done', 'error'): break
        time.sleep(1)
    row = dict(n=n, rid=rid, input=r['input'], status=r['status'], mode=r.get('mode'), director=r.get('director_wait'), sec=round(time.time() - t0, 1), segs=[(x.get('dur'), x.get('mode'), x.get('status'), x.get('url'), x.get('ref_fallback'), x.get('err')) for x in r.get('segs', [])], lines=r.get('lines'), next=r.get('next'), err=r.get('err'), location=r.get('location'), kiss=(r.get('spec') or {}).get('kiss'))
    rows.append(row); print(json.dumps({k: row[k] for k in ('n', 'input', 'status', 'mode', 'director', 'sec', 'location', 'err')}, ensure_ascii=False), [x[1:3] + (x[4],) for x in row['segs']], flush=True)
    if r['status'] != 'done': break
    for i, x in enumerate(r['segs']):
        with op.open(x['url'], timeout=120) as f: (out / f'{n}_{i + 1}.mp4').write_bytes(f.read())
    time.sleep(20)  # 模拟她看视频、末帧后台准备
(out / 'rows.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1)); print('DONE', sid)
