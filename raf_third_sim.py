"""按测试脚本自动跑一整轮：新开会话，逐轮发送（自由输入原话，或点 A/B 选项），每轮等两段都好再发下一句。
用法：python3 raf_third_sim.py tests/vicky18.json 5+10          → 汇总写 tests/runs/<会话>.json
      python3 auto_test.py --replay <5+10 的会话> 10+10      → 用同一组实际输入（选项按原来点到的文字）重放
      python3 auto_test.py --sim 18 5+10                     → 模拟用户：每轮看完剧情，由 LLM 按 Vicky 的输入习惯决定点 A/B 还是自己打一句（v0.15 起默认用这个）
每轮打印一行：轮次、她的输入、导演层判定、关键片段、地点、选项、耗时。"""
import json, sys, time
from pathlib import Path
from urllib import request as U

D = Path(__file__).resolve().parent
K = (D / 'token.txt').read_text().strip(); API = 'http://127.0.0.1:8901'


def call(path, body=None):
    req = U.Request(API + path, data=json.dumps(dict(body, k=K)).encode() if body is not None else None,
                    headers={'Content-Type': 'application/json'}, method='POST' if body is not None else 'GET')
    with U.urlopen(req, timeout=60) as r: return json.loads(r.read())


def send(body):
    for _ in range(200):  # 上一轮还在收尾时中转会回 429，等一下再发
        try: return call('/api/round', body)['id']
        except Exception as e:
            if '429' not in str(e): raise
            time.sleep(3)
    raise RuntimeError('中转一直忙')


SIM = """你在模拟一位真实用户玩女性向互动短剧《Rafael｜这次，不是演的》第三视角实时版：画面像电视剧一样同时拍到女主和男主 Rafael（她六年的朋友、三年的室友，今早刚向她告白），她替女主做决定、替女主说话。每一轮看完视频后，她要么点 A/B 两个选项之一，要么自己打一句话。
她的习惯（来自她本人的多轮人工测试）：
- 自己打字时句子短、口语、带情绪，中文，不超过 25 个字；常见句式：反问（“你凭什么……”“什么意思？”）、拒绝或设条件（“我可以跟你进去，但你得……”）、要证明（“证明给我看”）、要见人或要看东西（“我倒要看看她到底是谁”）、要说法（“那你会选她还是选我？”）；感情起来以后也会主动表态或靠近（“好，我留下来”“过来，抱我”）。
- 她只根据画面里已经发生的事说话：不知道的信息不说（还没听说的人名、身份不提）。
- 她不只按剧情走：大约三分之一的轮次，她会提出资料包以外的事——想去别的地方（回自己房间、上天台、去吃东西、去海边、去酒吧、去他的店里），想做一件具体的事（让他给她倒杯酒、给她披件东西、陪她走走、带她去看他的书房），或者给自己编一段情节。
- 她会对上一轮的钩子做出反应（有人敲门、电话、有人出现），也会偶尔不按套路走：想离开、想去别处、要求他做一件具体的事。
- 大约一半轮次点选项、一半自己打字；不会连续三轮都是同一种。点选项时多点 A，偶尔点更大胆的 B。
只输出一个 JSON：{"kind": "free" 或 "option", "choice": "A 或 B（kind=option 时）", "input": "她打的那句话（kind=free 时）", "why": "一句话说明她为什么这么做"}"""


def sim_pick(rows, nxt, n, total):
    import director
    hist = '\n'.join(f"第{r['n']}轮 她（{'点选项' if r['kind'] == 'option' else '打字'}）：{r['input']} → 画面里：{r.get('did') or ''}；他说：{' / '.join(r.get('zh_lines') or r.get('lines') or [])}" for r in rows) or '（刚看完开场：深夜酒店地下车库，一个穿黑色三件套、琥珀金眼睛的男人从黑色 Maybach 下车，扣住女主的手腕，说别动，问她从哪里来。）'
    kinds = [r['kind'] for r in rows[-2:]]
    tip = '（她已经连续两轮是同一种，这一轮换另一种）' if len(kinds) == 2 and kinds[0] == kinds[1] else ''
    user = f"到目前为止：\n{hist}\n\n此刻局面：{(nxt.get('cue') or {}).get('zh', '') if isinstance(nxt.get('cue'), dict) else nxt.get('cue', '')}\n选项 A：{(nxt.get('A') or {}).get('zh')}\n选项 B：{(nxt.get('B') or {}).get('zh')}\n\n这是第 {n} 轮（共 {total} 轮）{tip}。她这一轮怎么做？"
    for _ in range(3):
        try:
            obj, _, _ = director._call([{'role': 'system', 'content': SIM}, {'role': 'user', 'content': user}], 40)
            if obj.get('kind') == 'option' and obj.get('choice') in ('A', 'B'): return ('option', obj['choice'], obj.get('why', ''))
            if obj.get('kind') == 'free' and obj.get('input'): return ('free', obj['input'].strip(), obj.get('why', ''))
        except Exception as e: print('模拟用户失败，重试', e, flush=True)
    return ('option', 'A', '模拟用户失败，默认点 A')


def main():
    if sys.argv[1] == '--sim':
        total, mode = int(sys.argv[2]), sys.argv[3]; name = f'模拟用户 · 按剧情实时决定输入（{total} 轮）'
        steps = [('sim',)] * total
    elif sys.argv[1] == '--replay':
        src, mode = sys.argv[2], sys.argv[3]
        prev = json.loads((D / 'tests' / 'runs' / f'{src}.json').read_text())
        steps = [('replay', r['input'], r['kind']) for r in prev['rounds'] if r['status'] == 'done']; name = f"{prev['name']}（重放 {src}）"
    else:
        t = json.loads(Path(sys.argv[1]).read_text()); mode = sys.argv[2]; name = t['name']
        steps = [tuple(s) for s in t['steps']]
    out = []; start = 1
    if '--session' in sys.argv:  # 接着一个已有会话往下跑：--session <sid> --from <轮次>
        sid = sys.argv[sys.argv.index('--session') + 1]; start = int(sys.argv[sys.argv.index('--from') + 1])
        old = D / 'tests' / 'runs' / f'{sid}.json'
        if old.exists(): out = [r for r in json.loads(old.read_text())['rounds'] if r['n'] < start]
        nxt = {}
        if out:  # 接着跑时，下一轮的选项取上一轮存下的 next（模拟用户要看到 A/B 才能决定）
            rf = D / 'rounds' / f"{out[-1]['id']}.json"
            if rf.exists(): nxt = json.loads(rf.read_text()).get('next') or {}
    else:
        s = call('/api/session', {'mode': mode}); sid = s['sid']; nxt = s['next']
    print(f'{name} · {mode} · 会话 {sid}', flush=True)
    for i, st in enumerate(steps, 1):
        if i < start: continue
        why = ''
        if st[0] == 'sim':
            k, v, why = sim_pick(out, nxt, i, len(steps)); st = (k, v)
        if st[0] == 'free': text, kind, body = st[1], 'free', {'sid': sid, 'kind': 'free', 'input': st[1]}
        elif st[0] == 'option': text, kind, body = nxt[st[1]]['zh'], 'option', {'sid': sid, 'kind': 'option', 'choice': st[1]}
        else: text, kind, body = st[1], st[2], {'sid': sid, 'kind': 'free', 'input': st[1], 'director_kind': st[2]}
        failed = []
        for attempt in range(6):  # Vivix 服务端 generation_failed（约 305 秒后失败、中转重提一次仍失败）时，等 2 分钟重发同一句，不中断整组
            t0 = time.time(); rid = send(body)
            while True:
                time.sleep(3); r = call(f'/api/round/{rid}?k={K}')
                if r['status'] in ('done', 'error'): break
            errs = ' '.join([str(r.get('err') or '')] + [str(x.get('err') or '') for x in (r.get('segs') or [])])
            if r['status'] == 'done' or 'generation_failed' not in errs or attempt == 5: break
            failed.append(rid); print(f'第 {i} 轮 {rid} 服务端失败（generation_failed），120 秒后重发同一句（第 {attempt + 1} 次）', flush=True); time.sleep(120)
        rf = D / 'rounds' / f'{rid}.json'  # 接口不返回 spec，直接读中转存的这一轮记录
        sp = r.get('spec') or (json.loads(rf.read_text()).get('spec') if rf.exists() else None) or {}; nxt = r.get('next') or nxt
        segs = r.get('segs') or []
        row = {'n': i, 'id': rid, 'kind': kind, 'pick': st[1] if st[0] == 'option' else None, 'input': text, 'status': r['status'], 'err': r.get('err'),
               'type': sp.get('input_type'), 'cards': sp.get('cards_done'), 'location': sp.get('location'), 'changed': sp.get('scene_changed'),
               'wolf': sp.get('wolf'), 'cast': sp.get('cast'), 'tries': sp.get('director_attempts'), 'lint_first': sp.get('lint_first'),
               'director': r.get('director'), 'director_sec': r.get('director_sec'), 'wall': round(time.time() - t0, 1),
               'seg_ready': [round((x['ready_at'] - r['director_at']) / 1000, 1) for x in segs if x.get('ready_at') and r.get('director_at')],
               'lines': [l for k in ('seg1', 'seg2') for l in (r.get('lines') or {}).get(k, []) if l],
               'A': (nxt.get('A') or {}).get('zh'), 'B': (nxt.get('B') or {}).get('zh'),
               'did': sp.get('did'), 'zh_lines': [z for k in ('seg1', 'seg2') for z in (sp.get('zh') or {}).get(k, []) if z], 'why': why, 'kiss': sp.get('kiss'), 'staging': sp.get('staging'), 'vivix_failed_rounds': failed}
        out.append(row); print(json.dumps(row, ensure_ascii=False), flush=True)
        (D / 'tests' / 'runs').mkdir(parents=True, exist_ok=True)
        (D / 'tests' / 'runs' / f'{sid}.json').write_text(json.dumps({'name': name, 'mode': mode, 'session': sid, 'rounds': out}, ensure_ascii=False, indent=1))
        if r['status'] != 'done': print('这一轮失败，停止', flush=True); break
        time.sleep(8)  # 等下一轮首帧（中转里也会等末帧质检和修图）
    print('完成', sid, flush=True)


if __name__ == '__main__':
    main()
