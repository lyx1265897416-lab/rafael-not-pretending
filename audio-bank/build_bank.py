"""给歌声做响度和字幕时间，传到 GCS，写 masters/audio_bank.json。歌词是我们写的，时间用本地 faster-whisper 对齐。"""
import glob, json, re, subprocess, sys
from pathlib import Path
D = Path(__file__).resolve().parent; R = D.parent; ROOT = R.parent.parent
FF = str(ROOT / '.media-runtime/vivix-bin/ffmpeg'); FP = str(ROOT / '.media-runtime/vivix-bin/ffprobe')
OLD = ROOT / 'outputs/rafael-bgm-sfx-20261026/audio'
SONGS = {'SONG_HE_MORNING': ('he', 'morning', '慢、温柔，适合清晨和室内', [('Stay a little longer in the morning light.', '再多留一会儿，在这晨光里。'), ("I don't need an answer, just you by my side.", '我不要答案，只要你在身边。')]),
         'SONG_HE_ROAD': ('he', 'road', '轻松、自由，适合路上和海边', [('Wind on the coast road, hold on to me.', '海边公路的风里，抓紧我。'), ('Nowhere to be now, just you and the sea.', '哪儿也不用去，只有你和海。')]),
         'SONG_SHE_MORNING': ('她', 'morning', '轻快、带点调侃，适合室内和安静的时候', [("You said it was acting, I knew it wasn't true.", '你说是在演，我知道不是。'), ("So I'm singing it out loud now, it was always you.", '所以我大声唱出来，一直都是你。')]),
         'SONG_SHE_ROAD': ('她', 'road', '明亮、开心，适合路上和海边', [("Take me down the coast road, don't slow down for me.", '带我沿着海边走，别为我减速。'), ("Hold my hand and sing along, it's just you and me.", '牵着我的手一起唱，只有你和我。')])}
BGM = {'home': (OLD / 'MUS_RAF_HOME_V1.mp3', '日常、轻松的合租生活'), 'trust': (OLD / 'MUS_RAF_TRUST_V1.mp3', '谈开之后的理解和安心'), 'proximity': (OLD / 'MUS_RAF_PROXIMITY_V1.mp3', '靠近、心动、吻和日落'), 'tension': (OLD / 'MUS_RAF_TENSION_V1.mp3', '误会、紧张'), 'work': (OLD / 'MUS_RAF_WORK_V1.mp3', '修车店里专注做事'), 'ride': (D / 'MUS_RAF_RIDE.mp3', '骑车兜风，自由开心')}
def sh(*a, t=200): return subprocess.run(a, capture_output=True, text=True, timeout=t)
def persist(p):
    for _ in range(5):
        try: r = sh('waku', 'persist', str(p), t=150)
        except subprocess.TimeoutExpired: continue
        m = re.search(r'"url":\s*"([^"]+)"', r.stdout)
        if m: return m.group(1)
    raise SystemExit(f'persist failed {p}')
def dur(p): return float(sh(FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)).stdout)
snap = sorted(glob.glob(str(Path.home() / '.cache/huggingface/hub/models--Systran--faster-whisper-small.en/snapshots/*')))[-1]
ASR = str(Path.home() / 'Documents/waku内容/off-script/tools/asr-env/bin/python')
TR = """import sys,json
from faster_whisper import WhisperModel
m=WhisperModel(sys.argv[1],device='cpu',compute_type='int8')
out={}
for f in sys.argv[2:]:
    segs,_=m.transcribe(f,word_timestamps=True,language='en')
    out[f]=[{'w':w.word.strip(),'s':round(w.start,2),'e':round(w.end,2)} for s in segs for w in s.words]
print(json.dumps(out))"""
norm = {}
for n in SONGS:
    o = D / f'{n}.norm.mp3'
    # 去掉开头结尾静音，响度统一
    sh(FF, '-y', '-v', 'error', '-i', str(D / f'{n}.mp3'), '-af', 'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.2,areverse,loudnorm=I=-16:TP=-1.5:LRA=7', '-ar', '44100', '-b:a', '128k', str(o))
    norm[n] = o
words = json.loads(sh(ASR, '-c', TR, snap, *[str(x) for x in norm.values()], t=280).stdout.strip().splitlines()[-1])
bank = {'bgm': {}, 'songs': {}}
for n, (who, mood, desc, lines) in SONGS.items():
    o = norm[n]; w = words[str(o)]; d = dur(o); print(n, round(d, 1), ' '.join(x['w'] for x in w)[:150], flush=True)
    nw = [len(l[0].split()) for l in lines]; i = 0; rows = []
    for (en, zh), k in zip(lines, nw):
        part = w[i:i + k] or w[-1:]; i += k
        rows.append({'en': en, 'zh': zh, 's': part[0]['s'], 'e': part[-1]['e'] + .3})
    if len(w) < sum(nw) - 2: rows = [{'en': l[0], 'zh': l[1], 's': round(d * j / len(lines), 2), 'e': round(d * (j + 1) / len(lines), 2)} for j, l in enumerate(lines)]; print('  whisper 对不上，按时长均分')
    bank['songs'][n.lower()] = {'who': who, 'mood': mood, 'desc': desc, 'dur': round(d, 1), 'url': persist(o), 'lines': rows}
for k, (p, desc) in BGM.items():
    o = D / f'bgm_{k}.mp3'
    sh(FF, '-y', '-v', 'error', '-i', str(p), '-af', 'loudnorm=I=-20:TP=-2', '-ar', '44100', '-b:a', '128k', str(o))
    bank['bgm'][k] = {'desc': desc, 'url': persist(o)}; print(k, round(dur(o), 1), flush=True)
(R / 'masters/audio_bank.json').write_text(json.dumps(bank, ensure_ascii=False, indent=1))
