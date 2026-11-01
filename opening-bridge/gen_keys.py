"""空镜首尾帧 + 选择点男主正面近景的候选图。编号先落盘，超时后用编号取结果，不重复提交。"""
import json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
D = Path(__file__).resolve().parent; OUT = D / 'keys'; OUT.mkdir(exist_ok=True)
CAST = Path('/Users/vicky/Interactive storyline/outputs/rafael-cast-complete-20261023/images')
CACHE = D / 'refs_urls.json'; URLS = json.loads(CACHE.read_text()) if CACHE.exists() else {}
def sh(a, t): return subprocess.run(a, capture_output=True, text=True, timeout=t)
def persist(p):
    if str(p) in URLS: return URLS[str(p)]
    for _ in range(5):
        try: r = sh(['waku', 'persist', str(p)], 150)
        except subprocess.TimeoutExpired: print('persist timeout, retry', p.name, flush=True); continue
        m = re.search(r'"url":\s*"([^"]+)"', r.stdout)
        if m: URLS[str(p)] = m.group(1); CACHE.write_text(json.dumps(URLS, indent=1)); return m.group(1)
    raise SystemExit(f'persist failed {p}')
def parse(s): return json.loads(re.search(r'\{.*\}', s, re.S).group(0))
def one(it):
    name, prompt, imgs = it
    out, jf = OUT / f'{name}.jpg', OUT / f'{name}.job'
    if out.exists(): return name, 'exists'
    if jf.exists(): j = {'job_id': jf.read_text().strip()}
    else:
        r = sh(['waku', 'gen', 'run', 'google/nano-banana-2.1/edit', '--capability', 'multimodal.generate.image', '--params', json.dumps({'prompt': prompt, 'images': imgs, 'aspect_ratio': '9:16', 'resolution': '2k', 'output_format': 'jpeg'})], 300)
        try: j = parse(r.stdout)
        except Exception: return name, 'FAIL ' + (r.stdout[-300:] + r.stderr[-300:])
        if j.get('job_id'): jf.write_text(j['job_id'])
    for _ in range(5):
        if j.get('asset_url') or not j.get('job_id'): break
        r = sh(['waku', 'gen', 'result', j['job_id'], '--wait', '--timeout', '200'], 260)
        try: j = dict(parse(r.stdout), job_id=j['job_id'])
        except Exception: pass
    if not j.get('asset_url'): return name, 'FAIL ' + json.dumps(j, ensure_ascii=False)[:300]
    sh(['curl', '-s', '--noproxy', '*', '-o', str(out), j['asset_url']], 120)
    return name, 'ok'
CU = D / 'v20_27.jpg'; WIDE = D / 'v20_0.5.jpg'
cu, wide = persist(CU), persist(WIDE)
rp, rf = persist(CAST / '01-rafael-portrait-v3.png'), persist(CAST / '01-rafael-face-three-v1.png')
print('refs ok', flush=True)
STYLE = "Keep the exact rendering and quality of image 1: the same semi-realistic high-detail look, same skin texture, same soft morning daylight and color temperature. No haze, no glossy HDR, no plastic skin, no anime. No text, no logo, no watermark."
FACE = ("Image 1 is the current shot in the same bedroom. Keep everything about the shot: the same man, same messy black hair, same faded charcoal T-shirt, thin silver chain, thorn tattoo on the side of his neck below the ear at the left of the frame, same room, same window with cream curtains and the sea on the right, same picture on the wall. Images 2 and 3 confirm his identity: same face proportions, not elongated, clean-shaven. "
        "Change only the head and body direction: he now faces the camera straight on, a frontal close-up from the chest up with both shoulders square to the camera and both eyes and both ears symmetrical in frame, his eyes looking just past the lens at the woman he has just asked out. Lips closed, no smile, a serious, slightly nervous, waiting expression, chin level. His face sits between 18% and 50% from the top of the frame. Exactly one person in frame, no hands in frame. ")
WIN = ("Empty shot with no people. Images 1 and 2 show this bedroom. Show the window of this same room from inside: sheer cream curtains parted, a white window frame, the sea horizon and a little coastal greenery outside, a small green potted plant on the sill at the lower left, a corner of the wooden headboard and white pillow at the lower edge. ")
jobs = [(f'cu{i}', FACE + STYLE, [cu, rp, rf]) for i in (1, 2, 3)] + \
       [(f'win{i}', WIN + "Soft clear early-morning daylight, the same daylight as in the images, gentle sun on the curtains. " + STYLE, [cu, wide]) for i in (1, 2)]
with ThreadPoolExecutor(5) as ex:
    for n, u in ex.map(one, jobs): print(n, u[:200], flush=True)
