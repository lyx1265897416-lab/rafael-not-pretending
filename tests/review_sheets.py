"""把一个会话的每轮拼成审片联系表：第 1 段、第 2 段都按 0.5 秒抽帧，上方标轮次和秒数。用法：python3 tests/review_sheets.py <sid>"""
import glob, json, os, subprocess, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sid = sys.argv[1]; D = Path(__file__).resolve().parent.parent; O = D / 'tests' / sid; (O / 'sheets').mkdir(parents=True, exist_ok=True)
FF = '/Users/vicky/Interactive storyline/.media-runtime/vivix-bin/ffmpeg'
rs = [json.load(open(f)) for f in glob.glob(str(D / 'rounds/*.json'))]
rs = sorted([r for r in rs if r.get('sid') == sid], key=lambda r: r['round'])
def job(r):
    n = r['round']; out = []
    for i, s in enumerate(r.get('segs') or []):
        v = O / f'R{n:02d}_{i+1}.mp4'
        if not v.exists(): subprocess.run(['curl', '-s', '--noproxy', '*', '-m', '120', '-o', str(v), s['url']])
        out.append(v)
    a = str(O / f'sheets/R{n:02d}_1.jpg'); b = str(O / f'sheets/R{n:02d}_2.jpg')
    for v, o, rows in ((out[0], a, 1), (out[1], b, 3)):
        subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(v), '-vf', f'fps=2,scale=150:-2,tile=12x{rows}', '-frames:v', '1', '-q:v', '4', '-strict', 'unofficial', '-update', '1', o])
    return n
with ThreadPoolExecutor(6) as ex: print(list(ex.map(job, rs)))
L = []
for r in rs:
    sp = r.get('spec') or {}
    L.append(f"\n## R{r['round']} [{r.get('kind')}] {r.get('mode')} 输入：{r.get('input')}\n时间 at={r.get('at')} 地点前={r.get('place_before')} 判定={sp.get('route') or sp.get('kind')}\nspec: " + json.dumps({k: v for k, v in sp.items() if k not in ('options',)}, ensure_ascii=False)[:2600])
(O / 'specs.md').write_text('\n'.join(L), encoding='utf8')
