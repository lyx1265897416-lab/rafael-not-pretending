"""Rafael 第三视角实时版 → 实时生成测试记录页（projects/realtime-drama-test-log）的“RAFAEL · 观众第三视角”剧集。
复用 Magnus 第三视角 make_log_third.py / build_third_log.py 的拼接和卡片写法，只换开场、命名和参数；写 dramas/rafael-third.json，再按 id 合并进 data.js。
四个标记里“时延”自动算，另外三个来自审片记录 tests/review-<会话>.json。
用法：python3 build_log.py S0102325ab"""
import json, shutil, statistics as ST, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'magnus-third-live-v1'))
import make_log_third as ML

D = Path(__file__).resolve().parent
ML.D = D
SITE = ML.LOG
DID = 'rafael-third'
OK_LAT = 90
TITLE = '你的人工测试 · 第 1 次 · ultrafast · 5+15'
TAG = 'full-manual1-uf-5-15'


def M(ok, label, note): return [1 if ok else 0, label, note]


def seed_clips(sid, rs):
    """审片时 sheets.py 已下载过的片段直接拿来用，不再下载一次。"""
    (D / 'review' / 'clips').mkdir(parents=True, exist_ok=True)
    for n, r in enumerate(rs, 1):
        for i in (1, 2):
            a, b = D / 'review' / sid / f'R{n:02d}_{i}.mp4', D / 'review' / 'clips' / f"{r['id']}_{i}.mp4"
            if a.exists() and not b.exists(): shutil.copyfile(a, b)


def build_film(rs):
    open_mp4 = D / 'site' / 'media' / 'OPEN.mp4'
    items, cues, chapters = [('v', open_mp4, ML.dur(open_mp4))], [], [['ep', '开场', 0.0]]
    for c in json.loads((D / 'site' / 'open_cues.json').read_text(encoding='utf-8')):
        cues.append((c['s'], c['e'], f"{c['zh']}\n{c['en']}"))
    t = items[0][2]; prev_last = D / 'masters' / 'idle-key.jpg'
    for n, r in enumerate(rs, 1):
        files = ML.seg_files(r); mode = r['mode']
        chapters.append(['rt', f'第 {n} 轮', round(t, 2)])
        items.append(('img', prev_last, ML.HOLD)); cues.append((t + 0.2, t + ML.HOLD, f"她：{r['input']}\n（实时生成 · {mode} · 第 {n} 轮）")); t += ML.HOLD
        for i, f in enumerate(files):
            d = ML.dur(f); items.append(('v', f, d)); cues += ML.seg_cues(r, i, t, d); t += d
        v, p = SITE / 'v' / f"{DID}-{r['id']}.mp4", SITE / 'v' / f"{DID}-{r['id']}.jpg"
        if not v.exists(): ML.encode([('v', f, ML.dur(f)) for f in files], v, crf='28')
        if not p.exists(): subprocess.run([ML.FF, '-v', 'error', '-y', '-ss', '1.5', '-i', str(files[0]), '-frames:v', '1', '-vf', 'scale=360:-2', '-q:v', '4', str(p)], check=True)
        prev_last = D / 'review' / 'clips' / f"{r['id']}_end.jpg"
        if not prev_last.exists(): subprocess.run([ML.FF, '-v', 'error', '-y', '-sseof', '-0.1', '-i', str(files[1]), '-frames:v', '1', '-q:v', '2', str(prev_last)], check=True)
    out = SITE / 'film' / f'{DID}-{TAG}.mp4'
    if not out.exists(): ML.encode(items, out)
    (SITE / 'film' / f'{DID}-{TAG}.vtt').write_text('\n'.join(['WEBVTT', ''] + [f'{ML.ts(a)} --> {ML.ts(b)}\n{x}\n' for a, b, x in sorted(cues)]), encoding='utf-8')
    subprocess.run([ML.FF, '-v', 'error', '-y', '-i', str(D / 'docs' / 'media' / 'poster.jpg'), '-vf', 'scale=480:-2', '-q:v', '3', str(SITE / 'film' / f'{DID}-{TAG}.jpg')], check=True)
    return dict(video=f'film/{DID}-{TAG}.mp4', poster=f'film/{DID}-{TAG}.jpg', vtt=f'film/{DID}-{TAG}.vtt', duration=round(ML.dur(out), 1), chapters=chapters)


def card(n, r, rv):
    sp = r['spec']; mode = r['mode']; ready = [(s['ready_at'] - r['at']) / 1000 for s in r['segs']]; lat = max(ready)
    note = rv.get(str(n), {}); v = r.get('view') or {}
    play = (v['play_at'] - r['at']) / 1000 if v.get('play_at') else None
    marks = [M(note.get('err_ok', 1), '画面硬错误', note.get('err', '无')),
             M(note.get('free_ok', 1), '左右她', note.get('free', '跟着她的话走，没有替她做决定')),
             M(lat <= OK_LAT, '时延', f'发送到两段都就绪 {lat:.1f} 秒'),
             M(note.get('land_ok', 1), '那一下', note.get('land', sp.get('did') or ''))]
    stats = [['方案', mode], ['导演层', f"{r.get('director_sec') or 0:.1f}s" + ('（预先写好）' if r.get('director') == 'prefetched' else '')],
             ['第 1 段就绪', f'{ready[0]:.1f}s'], ['第 2 段就绪', f'{ready[1]:.1f}s']]
    if play is not None: stats += [['发送到开播', f'{play:.1f}s'], ['接缝停顿', f"{v.get('stall') or 0:.1f}s"]]
    stats += [['判定', {'direction': '明确引导', 'question': '问答', 'vague': '模糊'}.get(sp.get('input_type'), '—')],
              ['关键剧情', '、'.join(sp.get('cards_done') or []) or '—'], ['地点', r.get('location') or '—']]
    lines = [b for k in ('seg1', 'seg2') for b in sp[k] if b[1]]
    zh = [z for k in ('seg1', 'seg2') for z in (sp.get('zh') or {}).get(k, []) if z]
    beats = [f"{b[2]}｜{b[0]}" for k in ('seg1', 'seg2') for b in sp[k]]
    nx = r.get('next') or sp.get('next') or {}
    c = dict(n=n, label=f"第 {n} 轮 · {'自由输入' if r['kind'] == 'free' else '点选项'} · {mode}", video=f"v/{DID}-{r['id']}.mp4", poster=f"v/{DID}-{r['id']}.jpg",
             her=r['input'], he=' '.join(b[1] for b in lines), he_zh=' '.join(zh), beat='；'.join(beats),
             rule=f"下一轮选项：A {nx.get('A', {}).get('zh', '')} ／ B {nx.get('B', {}).get('zh', '')}",
             stats=stats, marks=marks, job=' / '.join(s.get('job_id', '') for s in r['segs']))
    return c, lat, play, marks


def main(sid):
    rs = ML.rounds_of(sid); seed_clips(sid, rs)
    rv = json.loads((D / 'tests' / f'review-{sid}.json').read_text(encoding='utf-8'))
    info = build_film(rs)
    rows = [card(n, r, rv) for n, r in enumerate(rs, 1)]
    lats = [x[1] for x in rows]; plays = [x[2] for x in rows]; n = len(rows); ok = [sum(x[3][k][0] for x in rows) for k in range(4)]
    opt = [x[2] for x, r in zip(rows, rs) if r['kind'] != 'free']; free = [x[2] for x, r in zip(rows, rs) if r['kind'] == 'free']
    places = []
    for r in rs:
        if r.get('location') and (not places or places[-1] != r['location']): places.append(r['location'])
    summary = [['轮数', str(n)], ['发送到两段都就绪 中位', f'{ST.median(lats):.1f} 秒'], ['范围', f'{min(lats):.1f}–{max(lats):.1f} 秒'], ['发送到开播 中位', f'{ST.median(plays):.1f} 秒'],
               ['无硬错误', f'{ok[0]}/{n}'], ['没有左右她', f'{ok[1]}/{n}'], ['那一下落到她', f'{ok[3]}/{n}'], ['演到的关键剧情', '—'], ['走过的地点', ' → '.join(places)]]
    note = (f'结论：等待和接缝都达标，发送到开播中位 {ST.median(plays):.1f} 秒（点选项 {ST.median(opt):.1f} 秒，自由输入 {ST.median(free):.1f} 秒），13 轮接缝停顿都是 0。'
            f'但画面连续性差，无硬错误只有 {ok[0]}/{n}，“那一下”落到 {ok[3]}/{n}，唯一通过的是走 5+10 的第 8 轮，5+15 的 12 轮全部有硬错误（Magnus 第三视角 ultrafast 是 2/12）。'
            '最多的是服装和配饰跳变（第 2、5–7、9–13 轮：外套换款、条纹上衣变白或消失、T 恤脱了又穿回去、多出钻戒和手表），其次是越轴（第 12、13 轮）、换脸（第 5、13 轮）、发色变银灰（第 4、5 轮）、重影出现两个他（第 11 轮）。'
            '没演到的有 3 轮：第 6、7 轮你要他骑车带你兜风，车一直没开起来，所以第 6 轮之后你又说了一次；第 13 轮扑倒在沙滩上没有演，两人一直站着。'
            '第 1、3 轮桌上和手里同时有三明治，属于道具重复。聊天、试用期、散步、泼水、吻戏都落到了，吻戏连续约 10 秒，时长够。')
    g = dict(tab=TITLE, title=f'{TITLE}（{n} 轮）', when=time.strftime('%Y-%m-%d %H:%M', time.localtime(rs[0]['at'] / 1000)) + '–' + time.strftime('%H:%M', time.localtime(max(r['segs'][1]['ready_at'] for r in rs) / 1000)), note=note,
             params=[['模型', 'vivix-w1-ultrafast'], ['比例 / 画质', '9:16 · 720p · 24fps'], ['时长', '自动分流：12 轮 5s + 15s = 20s，第 8 轮内容轻走 5s + 10s = 15s'],
                     ['开场', '吻戏 V7 + 5 秒窗边清晨空镜 + 开场 V20，共 101.5 秒，预制'],
                     ['导演层', 'OpenRouter anthropic/claude-sonnet-5.5；点选项用后台预写好的分镜，自由输入现写（约 14–17 秒）'],
                     ['PE', '从 Magnus 第三视角 V1.9 复制，流程和规则不变，只换角色、世界观和时间（从清晨往后走）'], ['输入', '你本人在公网测试页里输入和点选项'],
                     ['计时', '就绪 = 从发送起到两段可播地址都拿到；开播比两段都就绪更早']],
             summary=summary, cards=[x[0] for x in rows])
    film = dict(mode='5+15', title=f'完整成片 · {TITLE}', desc=f'固定开场 + {n} 轮实时生成，每一轮都是你本人在公网测试页里输入或点选项（第 8 轮 5+10，其余 5+15）',
                stats=[summary[1], summary[2], summary[4], summary[7], summary[8]], **info)
    drama = dict(id=DID, title='RAFAEL · 观众第三视角', sub='《这次，不是演的》开放式实时版 · 观众站在旁边看，画面里同时看到 Rafael 和她 · 开场是预制的吻戏和早晨，之后全部实时 · 界面、交互和通用 PE 与 Magnus 第三视角一致',
                 links=[], films=[film], groups=[g])
    (SITE / 'dramas' / f'{DID}.json').write_text(json.dumps(drama, ensure_ascii=False, indent=1), encoding='utf-8')
    dj = SITE / 'data.js'; s = dj.read_text(encoding='utf-8'); log = json.loads(s[s.index('{'):s.rstrip().rstrip(';').rindex('}') + 1])
    ds = [d for d in log['dramas'] if d.get('id') != DID]
    i = next((k + 1 for k, d in enumerate(ds) if d.get('id') == 'magnus-third'), len(ds))
    log['dramas'] = ds[:i] + [drama] + ds[i:]; log['updated'] = time.strftime('%Y-%m-%d')
    dj.write_text('window.LOG = ' + json.dumps(log, ensure_ascii=False, indent=1) + ';\n', encoding='utf-8')
    print(note); print(summary); print(info['duration'], len(info['chapters']))


if __name__ == '__main__':
    main(sys.argv[1])
