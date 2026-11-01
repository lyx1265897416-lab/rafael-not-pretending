"""开场 = 文档里的吻戏 V7 + 开场 V20：统一 720×1280、24fps、响度 -16 LUFS，中间不加转场（V7 自带淡出到黑，正好是“昨晚→今早”的时间切）。
字幕按 V7 时长偏移合并，写 site/open_cues.json，末帧写 masters/open-last.jpg。"""
import json, re, subprocess
from pathlib import Path
R = Path('/Users/vicky/Interactive storyline'); D = Path(__file__).resolve().parent
FF = str(R / '.media-runtime/vivix-bin/ffmpeg'); FP = str(R / '.media-runtime/vivix-bin/ffprobe')
A = R / 'outputs/rafael-videos-20261029/first-kiss-flashback-v5/delivery/RAF_PEAK_FIRST_KISS_V7_1080p.mp4'
B = R / 'outputs/rafael-videos-20261029/opening-v20-clean-edge/delivery/RAF_OPENING_01_V20.mp4'
out = D / 'site/media/OPEN.mp4'
dur = lambda p: float(subprocess.run([FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)], capture_output=True, text=True).stdout)
fc = ('[0:v]scale=720:1280:flags=lanczos,fps=24,setsar=1,format=yuv420p[a];[1:v]scale=720:1280:flags=lanczos,fps=24,setsar=1,format=yuv420p[b];'
      '[0:a]aresample=48000,volume=1.0dB[x];[1:a]aresample=48000,volume=5.8dB,alimiter=limit=0.95[y];[a][x][b][y]concat=n=2:v=1:a=1[v][m]')
if not out.exists(): subprocess.run([FF, '-v', 'error', '-y', '-i', str(A), '-i', str(B), '-filter_complex', fc, '-map', '[v]', '-map', '[m]', '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-maxrate', '3500k', '-bufsize', '7000k', '-bf', '0', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(out)], check=True)
subprocess.run([FF, '-v', 'error', '-y', '-sseof', '-0.5', '-i', str(out), '-frames:v', '1', '-strict', 'unofficial', '-q:v', '2', str(D / 'masters/open-last.jpg')], check=True)
subprocess.run([FF, '-v', 'error', '-y', '-ss', '62', '-i', str(out), '-frames:v', '1', '-strict', 'unofficial', '-q:v', '3', str(D / 'site/media/poster.jpg')], check=True)
def vtt(p, off, who):
    rows = []
    for blk in re.split(r'\n\s*\n', Path(p).read_text(encoding='utf-8'))[1:]:
        ls = blk.strip().splitlines()
        if len(ls) < 3: continue
        s, e = [sum(float(x) * m for x, m in zip(t.strip().split(':'), (3600, 60, 1))) for t in ls[0].split('-->')]
        rows.append({'s': round(s + off, 2), 'e': round(e + off, 2), 'zh': ls[1], 'en': ls[2], 'who': who(ls[2])})
    return rows
HER = ("No. I'm good", 'Rafa.', 'This is my boyfriend', 'Kiss me', 'Make him believe', 'Yeah.')
EVAN = ('Come on. You can', "Let's go", 'Since when')
wa = lambda t: 'Her' if t.startswith(HER) else 'Evan' if t.startswith(EVAN) else 'Rafael'
d = dur(A)
cues = vtt(A.with_name('RAF_PEAK_FIRST_KISS_V7.zh-en.vtt'), 0, wa) + vtt(B.with_name('RAF_OPENING_01_V20.zh-en.vtt'), d, lambda t: 'Rafael')
(D / 'site/open_cues.json').write_text(json.dumps(cues, ensure_ascii=False))
print('V7', d, 'V20', dur(B), 'OPEN', dur(out), 'MB', round(out.stat().st_size / 1e6, 1), 'cues', len(cues))
