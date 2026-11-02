"""V2.4 实测：按 S184319582 的路线连着跑（披萨数量、海边、跨坐、脱衣、翻身、离开穿回、骑车、夜宵）。用法：python3 tests/run_v24.py [输入...]"""
import json, time, urllib.request as U, sys
from pathlib import Path
D = Path(__file__).resolve().parent.parent; K = (D / 'token.txt').read_text().strip(); API = 'http://127.0.0.1:8901'
op = U.build_opener(U.ProxyHandler({}))
def post(p, b):
    b = dict(b, k=K); r = U.Request(API + p, data=json.dumps(b).encode(), headers={'Content-Type': 'application/json'})
    return json.loads(op.open(r, timeout=60).read())
def get(p): return json.loads(op.open(API + p + ('&' if '?' in p else '?') + 'k=' + K, timeout=60).read())
INP = sys.argv[1:] or ['我想吃榴莲披萨', '我和他吃同一块披萨，并逗他', '我们去海边散步吧', '我拉他坐到沙地上', '我捧住他的脸，吻上去', '我跨坐在他身上，边吻边脱衣服', '把他的衣服也脱了，边吻边摸他腹肌', '我翻身把他压在沙滩上继续吻', '我们去看日落吧', '骑车去追日落', '我让他停车，带他去吃夜宵']
sid = post('/api/session', {'mode': 'auto'})['sid']; print('SID', sid, flush=True)
(D / 'tests' / 'last_sid').write_text(sid)
for n, t in enumerate(INP, 1):
    t0 = time.time(); rid = post('/api/round', {'sid': sid, 'kind': 'free', 'input': t})['id']
    while True:
        r = get(f'/api/round/{rid}')
        if r.get('status') in ('done', 'error'): break
        time.sleep(2)
    sp = r.get('spec') or {}
    print(f"R{n} {t} | {r.get('status')} {r.get('mode')} {time.time() - t0:.0f}s key={sp.get('use_key')} {r.get('key_sec')}s dir={r.get('director_sec')} try={sp.get('director_attempts')} modes={[s.get('mode') for s in r.get('segs') or []]} {r.get('err') or ''}", flush=True)
    print('   posture', sp.get('posture_end'), '| wardrobe', sp.get('wardrobe_end'), '| redress', sp.get('redressed'), flush=True)
    print('   items', sp.get('holding_end'), '| left', {k: [x['name'] for x in v] for k, v in (sp.get('left_end') or {}).items()}, flush=True)
    for k in ('seg1', 'seg2'):
        for b in sp.get(k) or []: print('     ', k[-1], str(b[2])[:9], '|', str(b[0])[:60], flush=True)
    if r.get('status') == 'error':
        print('ERR', r.get('err'), flush=True); break
    time.sleep(20)
print('END', sid, flush=True)
