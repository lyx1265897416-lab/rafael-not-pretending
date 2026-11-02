"""V2.4 干跑：用 S184319582 出过问题的位置，只跑导演层，看动作、穿脱、物品台账。用法：python3 tests/dry_v24.py [轮号...]"""
import glob, json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
D = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(D))
import director
rs = sorted([r for r in (json.load(open(f)) for f in glob.glob(str(D / 'rounds/L*.json'))) if r.get('sid') == 'S184319582'], key=lambda r: r['at'])
def hist(r):
    sp = r['spec']
    return {'input': r['input'], 'kind': r['kind'], 'lines': r['lines']['seg1'] + r['lines']['seg2'], 'did': sp.get('did'), 'ask': sp.get('ask'), 'delivered': bool(sp.get('delivered')), 'hook_type': sp.get('hook_type'), 'intimacy': sp.get('intimacy') or 0, 'place': sp.get('location'), 'set': sp.get('set'), 'extras': sp.get('extras') or [], 'input_type': sp.get('input_type'), 'kiss': sp.get('kiss'), 'opts': []}
ITEMS = {6: [{'name': '半块榴莲披萨', 'n': 1, 'at': '她右手'}], 14: [{'name': '小刻刀', 'n': 1, 'at': '她身侧的沙上'}, {'name': '开衫', 'n': 1, 'at': '她身侧的沙上'}], 17: [{'name': '小刻刀', 'n': 1, 'at': '沙地上'}, {'name': '开衫', 'n': 1, 'at': '沙地上'}, {'name': 'T恤', 'n': 1, 'at': '沙地上'}]}
def one(n):
    r = rs[n - 1]; psp = rs[n - 2]['spec']
    sp, sec = director.direct([hist(x) for x in rs[:n - 1]], psp.get('state'), r['input'], r.get('director_kind') or r['kind'], 'auto', place=psp.get('location'), place_rounds=1, done=(), stall=0, set_now=psp.get('set'), wardrobe=psp.get('wardrobe_end') or {}, cont={'posture': psp.get('posture_end') or '', 'holding': psp.get('holding_end') or '', 'looks': psp.get('looks') or {}, 'items': ITEMS.get(n, [])})
    return n, r['input'], sec, sp
want = [int(x) for x in sys.argv[1:]] or [2, 3, 6, 9, 13, 14, 16, 17, 19, 22]
with ThreadPoolExecutor(5) as ex:
    for n, t, sec, sp in ex.map(one, want):
        print(f'\n=== R{n} {t} | {sec}s try={sp.get("director_attempts")} {sp.get("dur_mode")} scene={sp.get("scene_changed")} pose_chg={sp.get("posture_changed")} redress={sp.get("redressed")} walkset={str(sp.get("set"))[-40:]}', flush=True)
        print('  wardrobe', sp.get('wardrobe_end'), '\n  posture', sp.get('posture_end'), '\n  items', sp.get('holding_end'), '| left', {k: [x['name'] for x in v] for k, v in (sp.get('left_end') or {}).items()}, '| kept', sp.get('items_kept'))
        print('  key', str(sp.get('key'))[:150])
        for k in ('seg1', 'seg2'):
            for b in sp[k]: print('    ', k[-1], str(b[2])[:9], '|', str(b[0])[:64], '|', str(b[1])[:26])
        print('  first', [x[:70] for x in sp.get('lint_first') or []][:4], '\n  left', [x[:70] for x in sp.get('lint_left') or []][:3], flush=True)
