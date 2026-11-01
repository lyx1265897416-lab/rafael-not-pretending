"""V2.0 干跑：用 S0102325ab 出过问题的剧情位置和她的原话只跑导演层，确认 spec 对了再花钱生成。"""
import glob, json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
D = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(D))
import director
rs = sorted([r for r in (json.load(open(f)) for f in glob.glob(str(D / 'rounds/*.json'))) if r.get('sid') == 'S0102325ab'], key=lambda r: r['round'])
def hist(r):
    sp = r['spec']
    return {'input': r['input'], 'kind': r['kind'], 'lines': r['lines']['seg1'] + r['lines']['seg2'], 'did': sp.get('did'), 'ask': sp.get('ask'), 'delivered': bool(sp.get('delivered')), 'hook_type': sp.get('hook_type'), 'intimacy': sp.get('intimacy') or 0, 'place': sp.get('location'), 'set': sp.get('set'), 'extras': sp.get('extras') or [], 'input_type': sp.get('input_type'), 'kiss': sp.get('kiss'), 'opts': []}
CASES = [(6, '你骑车带我去兜风吧。', {}, {}), (2, '所以，你是什么时候开始喜欢我的？', {}, {}),
         (8, '我从后面抱住他的腰', {}, {'posture': '两人骑在行驶的摩托上，他在前她在后座'}),
         (11, '衣服湿了，把衣服脱了吧。', {}, {'posture': '两人站在浪线边，面对面'}),
         (13, '我顺势把他扑倒在沙滩上，继续吻。', {'he': '赤裸上身，浅色水洗蓝牛仔裤，T 恤拎在右手', 'she': '条纹方领针织上衣，奶油白阔腿裤，开衫搭在左臂'}, {'posture': '两人站在浪线边，面对面', 'holding': '他右手拎着 T 恤，她左臂搭着开衫'})]
def one(c):
    n, text, w, cont = c
    prev = rs[n - 2]; h = [hist(r) for r in rs[:n - 1]]
    sp, sec = director.direct(h, prev['spec'].get('state'), text, 'free', 'auto', place=prev['spec'].get('location'), place_rounds=1, done=(), stall=0, set_now=prev['spec'].get('set'), wardrobe=w, cont=cont)
    return n, text, sec, sp
with ThreadPoolExecutor(5) as ex:
    for n, text, sec, sp in ex.map(one, CASES):
        print(f'\n=== R{n} {text} | {sec}s | {sp.get("dur_mode")} staging={sp.get("staging")} moved={sp.get("scene_changed")} attempts={sp.get("director_attempts")}')
        print(' intent:', sp.get('intent')); print(' wardrobe:', sp.get('wardrobe_end'), '| posture:', sp.get('posture_end'), 'chg', sp.get('posture_changed'), '| holding:', sp.get('holding_end'))
        print(' key:', sp.get('key'), '(auto)' if sp.get('key_auto') else '')
        for k in ('seg1', 'seg2'):
            for b in sp[k]: print('  ', k, b[2], '|', b[0][:80], '|', b[1], '|', b[3] if len(b) > 3 else '')
        print(' lint_first:', [x[:60] for x in sp.get('lint_first') or []]); print(' lint_left:', [x[:60] for x in sp.get('lint_left') or []]); print(' looks:', sp.get('looks'))
