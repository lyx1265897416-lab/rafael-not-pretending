"""同样的剧情位置和输入，比不同导演层模型的耗时和硬校验结果。只跑导演层，不生成视频。用法：DIRECTOR_MODEL=<模型> python3 tests/dry_model.py"""
import glob, json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
D = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(D))
import director
rs = sorted([r for r in (json.load(open(f)) for f in glob.glob(str(D / 'rounds/*.json'))) if r.get('sid') == 'S013219b4c'], key=lambda r: r['at'])
def hist(r):
    sp = r['spec']
    return {'input': r['input'], 'kind': r['kind'], 'lines': r['lines']['seg1'] + r['lines']['seg2'], 'did': sp.get('did'), 'ask': sp.get('ask'), 'delivered': bool(sp.get('delivered')), 'hook_type': sp.get('hook_type'), 'intimacy': sp.get('intimacy') or 0, 'place': sp.get('location'), 'set': sp.get('set'), 'extras': sp.get('extras') or [], 'input_type': sp.get('input_type'), 'kiss': sp.get('kiss'), 'opts': []}
def one(n):
    r = rs[n - 1]; psp = rs[n - 2]['spec']
    sp, sec = director.direct([hist(x) for x in rs[:n - 1]], psp.get('state'), r['input'], r.get('director_kind') or r['kind'], 'auto', place=psp.get('location'), place_rounds=1, done=(), stall=0, set_now=psp.get('set'), wardrobe=psp.get('wardrobe_end') or {}, cont={'posture': psp.get('posture_end') or '', 'holding': psp.get('holding_end') or '', 'looks': psp.get('looks') or {}})
    return n, r['input'], sec, sp
print(director.MODEL, flush=True)
with ThreadPoolExecutor(3) as ex:
    for n, t, sec, sp in ex.map(one, [5, 9, 14]):
        print(f'R{n} {t} | {sec}s attempts={sp.get("director_attempts")} {sp.get("dur_mode")} {sp.get("staging")} | intent: {sp.get("intent")}', flush=True)
        print('   w', sp.get('wardrobe_end'), '| p', sp.get('posture_end'))
        for k in ('seg1', 'seg2'):
            for b in sp[k]: print('    ', k[-1], str(b[2])[:10], '|', str(b[0])[:56], '|', b[1])
        print('   left', [x[:50] for x in sp.get('lint_left') or []], 'tokens', (sp.get('usage') or {}).get('completion_tokens'), flush=True)
