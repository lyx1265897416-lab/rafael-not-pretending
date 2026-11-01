"""V2.0 实测：按 S0102325ab 的方向连着跑一组，只看结果。用法：python3 tests/run_v20.py"""
import json, time, urllib.request as U, sys
from pathlib import Path
D = Path(__file__).resolve().parent.parent; K = (D / 'token.txt').read_text().strip(); API = 'http://127.0.0.1:8901'
op = U.build_opener(U.ProxyHandler({}))
def post(p, b):
    b = dict(b, k=K); r = U.Request(API + p, data=json.dumps(b).encode(), headers={'Content-Type': 'application/json'})
    return json.loads(op.open(r, timeout=60).read())
def get(p): return json.loads(op.open(API + p + ('&' if '?' in p else '?') + 'k=' + K, timeout=60).read())
INP = sys.argv[1:] or ['带我去你店里看看', '你骑车带我去兜风吧。', '我从后面抱住他的腰', '停车吧，我们去沙滩上走走', '我踢起一脚水花泼向他', '衣服湿了，把衣服脱了吧。', '我踮起脚，吻上他', '我顺势把他扑倒在沙滩上，继续吻。']
sid = post('/api/session', {'mode': 'auto'})['sid']; print('SID', sid, flush=True)
for n, t in enumerate(INP, 1):
    t0 = time.time(); rid = post('/api/round', {'sid': sid, 'kind': 'free', 'input': t})['id']
    while True:
        r = get(f'/api/round/{rid}')
        if r.get('status') in ('done', 'error'): break
        time.sleep(2)
    sp = r.get('spec') or {}
    print(f"R{n} {t} | {r.get('status')} {r.get('mode')} {time.time() - t0:.0f}s key={sp.get('use_key')} {r.get('key_sec')}s dir={r.get('director_sec')} {r.get('err') or ''}", flush=True)
    print('   posture', sp.get('posture_end'), '| wardrobe', sp.get('wardrobe_end'), flush=True)
    if r.get('status') == 'error': break
    time.sleep(28)  # 给后台抽末帧和质检留时间，和真人点得差不多
