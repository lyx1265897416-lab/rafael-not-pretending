"""清晨空镜：黎明前 → 早晨同一机位，Seedance 首尾帧。编号先落盘，重跑只取结果。"""
import json, re, subprocess
from pathlib import Path
D = Path(__file__).resolve().parent; K = D / 'keys'
def sh(a, t): return subprocess.run(a, capture_output=True, text=True, timeout=t)
def parse(s): return json.loads(re.search(r'\{.*\}', s, re.S).group(0))
CACHE = D / 'refs_urls.json'; URLS = json.loads(CACHE.read_text()) if CACHE.exists() else {}
def persist(p):
    if str(p) in URLS: return URLS[str(p)]
    for _ in range(5):
        try: r = sh(['waku', 'persist', str(p)], 150)
        except subprocess.TimeoutExpired: continue
        m = re.search(r'"url":\s*"([^"]+)"', r.stdout)
        if m: URLS[str(p)] = m.group(1); CACHE.write_text(json.dumps(URLS, indent=1)); return m.group(1)
    raise SystemExit(f'persist failed {p}')
def job(name, model, cap, params, out, wait=240):
    jf = D / f'{name}.job'
    if out.exists(): return
    if jf.exists(): j = {'job_id': jf.read_text().strip()}
    else:
        for _ in range(3):
            r = sh(['waku', 'gen', 'run', model, '--capability', cap, '--params', json.dumps(params)], 300)
            try: j = parse(r.stdout); break
            except Exception: j = None; print('retry', r.stderr[-200:], flush=True)
        if not j: raise SystemExit('submit failed ' + name)
        if j.get('job_id'): jf.write_text(j['job_id'])
    for _ in range(12):
        if j.get('asset_url'): break
        r = sh(['waku', 'gen', 'result', j['job_id'], '--wait', '--timeout', str(wait)], wait + 60)
        try: j = dict(parse(r.stdout), job_id=j['job_id'])
        except Exception: pass
    if not j.get('asset_url'): raise SystemExit(name + ' no result ' + json.dumps(j)[:300])
    sh(['curl', '-s', '--noproxy', '*', '-o', str(out), j['asset_url']], 180); print(name, 'ok', flush=True)
morning = persist(K / 'win1.jpg')
job('dawn', 'google/nano-banana-2.1/edit', 'multimodal.generate.image', {'prompt':
    "Keep this picture exactly: the same empty bedroom, same camera, same window, curtains, plant, headboard, pillows and bedding, every object in the same place, same rendering. Change only the time of day to the last minutes before sunrise: the room is dim with soft low blue-grey light, the sky outside is deep dusk blue fading to a thin pale peach line on the sea horizon, the sea is dark and calm, no direct sun on the walls or curtains, no lamps on. No people, no text, no watermark.",
    'images': [morning], 'aspect_ratio': '9:16', 'resolution': '2k', 'output_format': 'jpeg'}, K / 'dawn.jpg')
dawn = persist(K / 'dawn.jpg')
job('bridge', 'bytedance/seedance-2.5/image-to-video', 'multimodal.generate.video', {'image': dawn, 'last_image': morning, 'duration': 5, 'resolution': '720p', 'generate_audio': True, 'prompt':
    "An empty bedroom seen from inside, no people at all. Locked-off camera on a tripod, one continuous shot, no cuts, no zoom. Time passes gently: the blue pre-dawn light slowly warms and brightens into soft clear morning daylight, the sky outside turns pale blue, the sea begins to shimmer, sunlight slowly spreads across the sheer cream curtains and the white pillows, the curtains stir very slightly in the breeze. Every object stays in place. Same semi-realistic high-detail rendering and colors as the supplied images. No flicker, no text, no watermark. Audio: quiet distant ocean waves and one or two far-off seabirds at dawn. No music, no voices."},
    D / 'bridge_raw.mp4', 300)
