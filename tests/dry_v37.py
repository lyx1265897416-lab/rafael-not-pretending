"""V3.7 干跑：用 S0306013c4 的 5 个位置只跑导演层，看打回次数、耗时、在场的人。用法：python3 tests/dry_v34.py"""
import glob, json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
D = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(D))
import director
rs = sorted([r for r in (json.load(open(f)) for f in glob.glob(str(D / 'rounds/L*.json'))) if r.get('sid') == 'S0306013c4'], key=lambda r: r['at'])
def hist(r):
    sp = r['spec']
    return {'input': r['input'], 'kind': r['kind'], 'lines': r['lines']['seg1'] + r['lines']['seg2'], 'did': sp.get('did'), 'ask': sp.get('ask'), 'delivered': bool(sp.get('delivered')), 'hook_type': sp.get('hook_type'), 'intimacy': sp.get('intimacy') or 0, 'place': sp.get('location'), 'set': sp.get('set'), 'extras': sp.get('extras') or [], 'input_type': sp.get('input_type'), 'kiss': sp.get('kiss'), 'opts': [((sp.get('next') or {}).get(k) or {}).get('zh', '') for k in ('A', 'B')]}
def one(n):
    r = rs[n - 1]; psp = rs[n - 2]['spec'] if n > 1 else {}
    sp, sec = director.direct([hist(x) for x in rs[:n - 1]], psp.get('state') or '', r['input'], r['kind'], 'auto', place=psp.get('location'), place_rounds=1, done=tuple(r.get('cards_after') or ()), stall=0, set_now=psp.get('set'), wardrobe=psp.get('wardrobe_end') or {}, cont={'posture': psp.get('posture_end') or '', 'holding': psp.get('holding_end') or '', 'looks': psp.get('looks') or {}, 'items': psp.get('items_end') or []})
    return n, r['input'], sec, sp
with ThreadPoolExecutor(4) as ex:
    for n, t, sec, sp in ex.map(one, [2, 3, 4, 5]):
        print("   persona:", sp.get("persona_beat"), "| surprise:", sp.get("surprise"), "| model:", sp.get("director_model"), "| opts:", [((sp.get("next") or {}).get(k) or {}).get("zh") for k in "AB"], flush=True)
        print(f'R{n} {t[:16]} | {sec}s try={sp.get("director_attempts")} {sp.get("dur_mode")} | first必改 {[x[:36] for x in sp.get("lint_first") or [] if x.startswith("【必改")]}', flush=True)
        for k in ('seg1', 'seg2'):
            for b in sp[k]: print('    ', k[-1], str(b[0])[:56], '|', str(b[1])[:30])
