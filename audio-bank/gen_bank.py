"""预生成歌声和骑行配乐：实时轮不再多一次调用，播放时叠上去，不影响生成速度。编号先落盘，重跑只取结果。"""
import json, re, subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
D = Path(__file__).resolve().parent
A = ("Solo unaccompanied vocal, a cappella, absolutely no instruments, no drums, no backing vocals, dry intimate close microphone. {who}, singing casually and tenderly to one person right next to them, relaxed and a little imperfect, slow gentle tempo. English. Sing exactly these lyrics once, then stop: {lyr}")
HE = 'A young man in his twenties with a low, relaxed, slightly grainy warm voice'
SHE = 'A young woman in her twenties with a soft, light, clear voice'
JOBS = {
 'SONG_HE_MORNING': dict(prompt=A.format(who=HE, lyr="Stay a little longer in the morning light. I don't need an answer, just you by my side."), force_instrumental=False, music_length_ms=14000),
 'SONG_HE_ROAD': dict(prompt=A.format(who=HE, lyr="Wind on the coast road, hold on to me. Nowhere to be now, just you and the sea."), force_instrumental=False, music_length_ms=14000),
 'SONG_SHE_MORNING': dict(prompt=A.format(who=SHE, lyr="You said it was acting, I knew it wasn't true. So I'm singing it out loud now, it was always you."), force_instrumental=False, music_length_ms=14000),
 'SONG_SHE_ROAD': dict(prompt=A.format(who=SHE, lyr="Take me down the coast road, don't slow down for me. Hold my hand and sing along, it's just you and me."), force_instrumental=False, music_length_ms=14000),
 'MUS_RAF_RIDE': dict(prompt="Warm indie instrumental for a couple riding a motorcycle along a sunny coast road: fingerpicked electric guitar, soft brushed drums, gentle driving rhythm, free and happy, no vocals, seamless loop, medium tempo, modern romance film underscore, leaves room for dialogue.", force_instrumental=True, music_length_ms=44000),
}
def sh(a, t): return subprocess.run(a, capture_output=True, text=True, timeout=t)
def parse(s): return json.loads(re.search(r'\{.*\}', s, re.S).group(0))
def one(it):
    n, p = it; out, jf = D / f'{n}.mp3', D / f'{n}.job'
    if out.exists(): return n, 'exists'
    if jf.exists(): j = {'job_id': jf.read_text().strip()}
    else:
        r = sh(['waku', 'gen', 'run', 'elevenlabs/music-v2.5', '--capability', 'multimodal.generate.audio', '--params', json.dumps(dict(p, output_format='mp3_48000_192'))], 280)
        try: j = parse(r.stdout)
        except Exception: return n, 'FAIL ' + (r.stdout[-300:] + r.stderr[-300:])
        if j.get('job_id'): jf.write_text(j['job_id'])
    for _ in range(6):
        if j.get('asset_url') or not j.get('job_id'): break
        r = sh(['waku', 'gen', 'result', j['job_id'], '--wait', '--timeout', '200'], 260)
        try: j = dict(parse(r.stdout), job_id=j['job_id'])
        except Exception: pass
    if not j.get('asset_url'): return n, 'FAIL ' + json.dumps(j)[:300]
    sh(['curl', '-s', '--noproxy', '*', '-o', str(out), j['asset_url']], 120)
    return n, 'ok'
with ThreadPoolExecutor(5) as ex:
    for n, s in ex.map(one, JOBS.items()): print(n, s, flush=True)
