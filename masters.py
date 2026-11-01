"""母版：身份图上传 Vivix；她的三视合图、他的上半身服装；起始关键帧（masters/open-key.jpg，接开场末帧，两张脸都看得到）和站位母版用 nano-banana 生成。用法：python3 masters.py base | key | staging"""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image
import live_common as L
D = Path(__file__).resolve().parent; M = D / 'masters'; F = M / 'urls.json'
CAST = Path('/Users/vicky/Interactive storyline/outputs/rafael-cast-complete-20261023/images')
U = json.loads(F.read_text()) if F.exists() else {}
c = L.W1Client()
def up(key, path):
    U[key] = c.upload(path)['url']; F.write_text(json.dumps(U, indent=1)); print(key, U[key])
def persist(path):
    for _ in range(4):  # waku 上传偶尔 500
        r = subprocess.run(['waku', 'persist', str(path)], capture_output=True, text=True, timeout=90)
        m = re.search(r'"url":\s*"([^"]+)"', r.stdout)
        if m: return m.group(1)
    raise SystemExit(r.stdout[-300:] + r.stderr[-300:])
def edit(prompt, images, out):
    r = subprocess.run(['waku', 'gen', 'run', 'google/nano-banana-2.1/edit', '--capability', 'multimodal.generate.image', '--params', json.dumps({'prompt': prompt, 'images': images, 'aspect_ratio': '9:16', 'resolution': '1k', 'output_format': 'jpeg'})], capture_output=True, text=True, timeout=300)
    j = json.loads(re.search(r'\{.*\}', r.stdout, re.S).group(0))
    if j.get('job_id'): (M / f'{Path(out).stem}.job').write_text(j['job_id'])  # 编号先落盘：等待超时后用它取结果，不重复提交
    for _ in range(4):
        if j.get('asset_url') or not j.get('job_id'): break
        r = subprocess.run(['waku', 'gen', 'result', j['job_id'], '--wait', '--timeout', '200'], capture_output=True, text=True, timeout=260)
        j = dict(json.loads(re.search(r'\{.*\}', r.stdout, re.S).group(0)), job_id=j['job_id'])
    if not j.get('asset_url'): raise SystemExit(r.stdout[-400:] + r.stderr[-400:])
    subprocess.run(['curl', '-s', '--noproxy', '*', '-o', str(out), j['asset_url']], check=True); print(out, j['asset_url'], j.get('credits') or j.get('cost'))
    return j['asset_url']
RAF = ("RAFAEL = exactly the man in his reference images, 26 years old: smooth clean-shaven young skin, lean long face with hollow cheeks and a clean narrow jawline, heavy thick straight black brows, deep-set hooded eyes, straight nose, full lips, "
       "messy spiky black hair with strands on the forehead, black thorn tattoo up the right side of the neck, thick silver chain, tattoo sleeves on both forearms, broad shoulders, faded charcoal crew-neck T-shirt, light washed blue jeans.")
HER = ("HEROINE = exactly the woman in her reference images, an adult woman with a mature refined face: high cheekbones, slim tapered jaw, slim straight nose, grey-blue eyes, soft smudged taupe eye makeup, faint freckles across the nose, full mauve-rose lips, "
       "very long layered cool ash-blonde hair with darker roots and face-framing strands; cream cardigan over a cream-and-black striped knit top.")
LOOK = ("Same rendering and quality as the character reference images: high-detail skin, sharp eyes and lashes, individual hair strands, crisp fabric. No haze, no soft focus, no plastic skin, no anime. Adult characters. No text, no watermark, nobody else in frame.")
what = sys.argv[1]
if what == 'base':
    for k, f in {'face': '01-rafael-portrait-v3.png', 'evan': '04-evan-portrait-v2.png', 'maya': '05-maya-portrait-v3.png', 'cole': '06-cole-portrait-v2.png', 'ryan': '03-ryan-portrait-v1.png'}.items(): up(k, CAST / f)
    a = Image.open(CAST / '01-rafael-full-v16.png').convert('RGB'); W, H = a.size; a.crop((0, 0, W, int(H * 0.62))).save(M / 'outfit-upper.jpg', quality=92); up('outfit', M / 'outfit-upper.jpg')
    p, fu, an = [Image.open(CAST / f).convert('RGB') for f in ('02-user-portrait-v3.png', '02-user-full-v9.png', '02-user-angles-v1.png')]
    h = 1100; ims = [x.resize((int(x.width * h / x.height), h), Image.LANCZOS) for x in (p, fu, an)]
    s = Image.new('RGB', (sum(i.width for i in ims), h), 'white'); x = 0
    for i in ims: s.paste(i, (x, 0)); x += i.width
    s.save(M / 'her-sheet.jpg', quality=92); up('her', M / 'her-sheet.jpg')
elif what == 'key':
    imgs = [persist(M / 'open-last.jpg'), persist(CAST / '01-rafael-portrait-v3.png'), persist(CAST / '01-rafael-angles-v1.png'), persist(CAST / '02-user-portrait-v3.png'), persist(CAST / '02-user-angles-v1.png')]
    p = ("Image 1 is the current moment in the room: keep the same bedroom, the same one bed, the same framed coastal picture, wooden headboard, white duvet, pillows, olive throw at the foot, and the same soft early-morning daylight from the left. "
         "Move the camera a little closer and slightly to the side so both faces are visible in one two-shot from the waist up. " + RAF + " " + HER +
         " Images 2 and 3 are Rafael's identity, images 4 and 5 are her identity. RAFAEL on the LEFT of the frame, sitting on the near edge of the mattress, his upper body turned toward her in three-quarter view so his face is clearly visible in profile-three-quarter, looking at her, serious and a little nervous, the joke gone from his face, his tattooed forearm resting on his knee. "
         "HEROINE on the RIGHT of the frame, half-sitting propped against the pillows at the headboard, white duvet up to her waist, three-quarter view facing him, looking at him, lips closed, hands on the duvet. Both heads complete with headroom. Exactly two people, exactly one bed. " + LOOK)
    u = edit(p, imgs, M / 'open-key.jpg'); U['open_key_gcs'] = u; F.write_text(json.dumps(U, indent=1)); up('open_key', M / 'open-key.jpg')
elif what == 'staging':
    imgs = [persist(CAST / '01-rafael-full-v16.png'), persist(CAST / '02-user-full-v9.png')]
    p = ("Full-body two-shot on a plain mid-grey studio background. " + RAF + " " + HER + " She also wears cream wide-leg trousers with a striped tie belt. Image 1 is Rafael's identity and outfit, image 2 is hers. RAFAEL on the LEFT of the frame, HEROINE on the RIGHT, standing facing each other at half an arm's distance, both in three-quarter view, both faces clear, he is a head taller. Hands relaxed at their sides. " + LOOK)
    u = edit(p, imgs, M / 'staging.jpg'); up('staging', M / 'staging.jpg')
