"""末帧质检与修复（第三视角：画面里同时有 Rafael 和她，两人都对照身份母版）：上一轮的末帧要当下一轮的首帧，一旦走样（多了人、换装、换脸）就会一路传下去。
check(jpg) 用视觉模型按锁定项检查，返回 {ok, issues:[...]}；fix(url, issues) 用 nano-banana-pro/edit 参考身份母版把这一帧修干净，返回新图地址。
都在观众看视频、做选择的时候后台完成，不增加等待。"""
import base64, json, re, subprocess, time
from urllib import request as U
import director, live_common as _L

VLM = 'anthropic/claude-sonnet-5.5'
FACE_URL = _L.TU['face']  # 白底正面头像身份母版
OUTFIT_URL = _L.TU['outfit']  # 裁成上半身（全身站姿的母版会把画面往全身拉）

HER_URL = _L.TU['her']  # 她：正面头像 + 全身正面 + 多角度合图

CHECK = """图片1是一部观众第三视角互动剧的一帧画面：画面里应该同时有男主 Rafael 和女主（她），Rafael 在画面左侧、她在画面右侧。图片2是男主的身份母版，图片3是女主的身份母版（判断是不是同一个人以它们为准）。下一段视频会从这一帧接着生成，所以这一帧必须干净。请按下面的锁定项检查，只报你在画面上确实看到的问题：
1. 画面里除了男主、女主{allowed}还有没有其他人（路人、背影、人影、半透明人头）？同一个人出现两次也算。
2. 女主在不在画面里、脸能不能看清？女主长相和图片3比是不是明显换了人（脸型、五官、眼睛、年龄、变得幼态）？她应为：白皙皮肤、灰蓝色眼睛、鼻梁淡雀斑、很长的冷调灰金层次长发；奶油色长袖开衫，里面奶油色和黑色条纹针织上衣，下身奶油白阔腿长裤（在床上时可能盖在被子里）。发色变成金黄或深棕、头发变短变卷、开衫换成别的款式颜色、条纹上衣换了、裤子换了，都算问题（kind=her）。
3. 男主服装：应为褪色炭灰色圆领 T 恤、浅色水洗蓝牛仔裤。换成别的衣服或颜色算问题。
4. 男主标志：右侧颈部黑色荆棘纹身、粗银链、两条小臂满臂纹身。能看到这些部位时纹身或银链不见了、换了样子，算问题（kind=accessory）。有没有多出戒指、手表、手套？
5. 男主瞳色：应为深棕色。变成金色、灰色、发光算问题。（看不到眼睛就不报）
6. 男主长相：和图片2比，是不是明显换了人（脸型、五官、年龄、肤色不同）、变老、长出胡茬、头发变长或变整齐？
7. 有没有可读的文字、乱码、手机界面、图标、招牌字样？门、墙面、纸张、衣服上有没有徽章、品牌标志、字母？
8. 有没有明显崩坏（手指粘连、多指、两人肢体粘连穿插、肢体变形、皮肤异常老化起皱、画面撕裂）？
9. 光线：人物肤色明显偏橙、偏黄或发灰，画面过曝发白，算问题（kind=light，level=low）。
10. 女主的手（能看到时）：纤细白皙、短而圆的裸色素甲、手上没有任何首饰。有没有涂指甲油、美甲、长尖指甲、戒指、手链、手表？
10b. 画面里有没有不合常理的道具：悬空的物件、拿反的杯子、东西放在不合理的位置（人身上、半空）、同一件东西重复出现？（kind=prop）
11. 配角（只在画面里有配角时检查）：长相和衣着是不是和这个人平时的样子明显不同？
12. 背景：人物身后是不是变成了灰色或白色影棚幕布、平整的纯色背景，没有任何景物？是就算问题（kind=scene）。背景虚化、但还看得出灯光、窗户、家具的不算。
13. 站位：Rafael 是不是跑到了画面右侧、她在左侧（左右对调）？是就算问题（kind=staging）。
14. 构图：两人里有没有谁的脸被画面边缘切掉一部分、或只露出后脑勺和背影？是就算问题（kind=framing）。
{side_rule}每个问题标类别 kind：people（多了人）、her（女主不在画面、换了人、发型服装不对）、outfit（男主服装）、accessory（男主纹身银链、多了配饰）、face（男主换了人、明显变老、发型变了）、herhand（她的手：指甲油、美甲、首饰）、cast（配角不对）、eyes（瞳色、发光）、skin（皮肤粗糙、皱纹、油亮）、text（文字、手机界面）、broken（崩坏）、light（肤色和光线不对）、scene（背景变成影棚或纯色）、staging（左右对调、并排坐时正对镜头）、framing（有人的脸被画面边缘切掉、只露背影）、prop（道具不合常理）。
每个问题标级别：high = 第 1、2、3、7、8、10、11、12、13、14 项里的任何一条、明显换了人；low = 瞳色只是略偏、几缕头发略乱、她的表情略僵、光线略偏之类的小偏差。
另外报告：能不能看到男主的脸（face）、女主在不在画面里且能看到她的脸（her），以及男主脸部（额头到下巴、两耳之间）在画面里的位置 face_box = [左, 上, 右, 下]，用 0–1 的比例（看不到脸写 null）。
只输出一个 JSON：{"ok": true/false, "face": true/false, "her": true/false, "face_box": [0.1, 0.2, 0.35, 0.4], "issues": [{"text": "简短中文描述，可直接写进修图指令", "kind": "类别", "level": "high" 或 "low"}, ...]}；没有问题就 {"ok": true, "face": ..., "her": ..., "issues": []}。"""


NO_FIX = {'eyes', 'skin', 'face'}  # 第三视角 v1：light（白天）改成必须修好才出发——5+10 第 1 段从末帧续接，白天会直接带进下一轮（第 11→12 轮）  # face（偏老、发型乱）也交给第 2 段身份母版：5+10 测试里这类修图 3 次都因为把背景换掉被退回，白等 1–2 分钟  # 这两类交给第 2 段的身份母版纠正，不为它们修图（修图慢，还可能把背景换掉）
SCENE_DIFF_MAX = 20  # 修图前后画面四周（背景）的平均灰度差，超过就认为修图把背景、构图换掉了


SIDE_RULE = '15. 站位（这一刻两人并排坐着）：两人应并排坐、身体侧过来朝向对方，Rafael 在左、她在右。是不是变成面对面坐、或者两人都正对镜头像证件照？是就算问题（kind=staging）。\n'


def check(jpg, timeout=60, cast=(), side=False, worn=()):
    b64 = base64.b64encode(open(jpg, 'rb').read()).decode()
    body = {'model': VLM, 'max_tokens': 1200, 'reasoning': {'effort': 'low'},
            'messages': [{'role': 'user', 'content': [{'type': 'text', 'text': (('剧情里披在她身上的：' + '、'.join(worn) + '（穿在奶油色开衫外面，这是允许的，不算换装）。\n') if worn else '') + CHECK.replace('{allowed}', ('和' + '、'.join(cast) + '（允许出镜的配角）') if cast else '').replace('{side_rule}', SIDE_RULE if side else '')},
                                                      {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,' + b64}},
                                                      {'type': 'image_url', 'image_url': {'url': FACE_URL}},
                                                      {'type': 'image_url', 'image_url': {'url': HER_URL}}]}]}
    t0 = time.time()
    req = U.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                    headers={'Authorization': 'Bearer ' + director._key(), 'Content-Type': 'application/json'})
    with U.urlopen(req, timeout=timeout) as r: j = json.loads(r.read())
    txt = j['choices'][0]['message'].get('content') or ''
    m = re.search(r'\{.*\}', txt, re.S)
    res = json.loads(m.group(0)) if m else {'ok': True, 'issues': [], 'raw': txt[:200]}
    res['sec'] = round(time.time() - t0, 1)
    return res


def _edit(prompt, images, timeout):
    params = {'prompt': prompt, 'images': images, 'aspect_ratio': '9:16', 'resolution': '1k', 'output_format': 'jpeg'}
    r = subprocess.run(['waku', 'gen', 'run', 'google/nano-banana-pro/edit', '--capability', 'multimodal.generate.image', '--params', json.dumps(params)],
                       capture_output=True, text=True, timeout=timeout)
    m = re.search(r'\{.*\}', r.stdout, re.S)
    j = json.loads(m.group(0)) if m else {}
    if not j.get('asset_url') and j.get('job_id'):  # 偶尔先返回 pending：按 job_id 等结果，不重复提交
        r = subprocess.run(['waku', 'gen', 'result', j['job_id'], '--wait', '--timeout', '180'], capture_output=True, text=True, timeout=timeout)
        m = re.search(r'\{.*\}', r.stdout, re.S); j = json.loads(m.group(0)) if m else {}
    if not j.get('asset_url'): raise RuntimeError('修图没有返回地址：' + (r.stdout[-200:] or r.stderr[-200:]))
    return j['asset_url']


def fix_scene(frame_url, set_text, timeout=240):
    """背景变成灰色影棚或纯色时，只把背景换回这个地点。第三视角：两个人都保持原样。"""
    prompt = ('Edit Image 1: replace only the background. Behind the two people, the grey studio or plain backdrop becomes this real location, at the time of day it describes: ' + set_text + '. '
              'Keep both people exactly as they are in Image 1: the man on the left and the woman on the right, the same faces, hair, clothes, poses, expressions, head sizes and positions, camera angle and crop. '
              'Use Image 2 only as the reference for the man\'s face and Image 3 only as the reference for the woman\'s face. Only these two people are in the picture. No readable text, no logos. Same semi-realistic 2.5D character render style as the people in Image 1.')
    return _edit(prompt, [frame_url, FACE_URL, HER_URL], timeout)


def fix(frame_url, issues, timeout=240, keep_hands=False, worn=()):
    """第三视角：用两人的身份母版和他的服装母版把这一帧修干净：构图、地点、光线、景别、两人的姿势都保持不变，只改掉问题。"""
    prompt = ('Edit Image 1 minimally. Fix only these problems: ' + '；'.join(issues) + '。 '
              'Keep everything else in Image 1 pixel-faithful: the same background, location, lighting, camera angle, shot size, crop, both people\'s head sizes and positions, poses and expressions. '
              'There are exactly two people: the man (Rafael) on the left side of the picture and the woman on the right side. '
              'Use Image 2 only as the reference for the man\'s face, messy black hair and dark brown eyes. His outfit: a faded charcoal crew-neck T-shirt and light washed blue jeans; thick silver chain, black thorn tattoo on the right side of his neck, tattoo sleeves on both forearms; no rings, no watch, clean-shaven. '
              'Use Image 3 only as the reference for the woman\'s face, hair and outfit: pale skin, grey-blue eyes, faint freckles, very long layered cool ash-blonde hair with darker roots; '
              'she wears a cream long-sleeved cardigan over a cream-and-black striped knit top and cream wide-leg trousers; slender pale hands, short rounded nude nails, no rings, no bracelets, no watch. '
              'Do not add anything new. Only these two people are in the picture. No readable text. Same semi-realistic 2.5D character render style.')
    if any('外套' in w for w in worn): prompt += ' His jacket stays draped over her shoulders on top of her cardigan.'
    return _edit(prompt, [frame_url, FACE_URL, HER_URL], timeout)


def scene_diff(a, b):
    """比较修图前后画面四周（上 25%、左右各 15%）的灰度差，0–255；主体在中间，所以四周代表背景和构图。"""
    from PIL import Image, ImageChops
    A = Image.open(a).convert('L').resize((72, 128)); B = Image.open(b).convert('L').resize((72, 128))
    d = ImageChops.difference(A, B).load(); tot = n = 0
    for y in range(128):
        for x in range(72):
            if y < 32 or x < 11 or x >= 61: tot += d[x, y]; n += 1
    return round(tot / n, 1)


SEG_CHECK = """图片1是一段 9:16 视频按时间顺序抽出的 4 帧（左上=第1帧，右上=第2帧，左下=第3帧，右下=第4帧），来自一部观众第三视角的互动剧。图片2是男主 Rafael 的身份母版（凌乱黑发、颈部荆棘纹身、银链、炭灰色 T 恤、水洗牛仔裤）。图片3是女主的身份母版（正面头像、全身正面、多角度）：很长的冷调灰金层次长发，奶油色长袖开衫，奶油和黑色条纹针织上衣，奶油白阔腿长裤。{allowed}
正确的站位：两人同在一帧时，男主在画面左侧、女主在画面右侧。

先逐帧写清楚看到了什么，再判断：
frames: 每帧一项 {"frame": n, "people": ["画面里的人，从左到右，例如 男主/女主/配角/陌生人"], "her_outfit": "女主在这一帧的发色、开衫和里面的衣服（看不到女主写 null）", "notes": "其他异常"}

严重问题（只报你确实看到的）：
- her：女主和图片3明显不是同一个人；或她的开衫、条纹上衣换了（剧情写了脱下的除外）；或发色变成深棕、金黄、变短。
- face/outfit：男主不是图片2的人，或不是炭灰色 T 恤和牛仔裤（剧情写了换装的除外）。
- people：除了男主、女主和允许的配角之外，画面里出现了真人（背景、门口、倒影）；墙上画里的人像不算。
- axis：两人同在一帧时，男主在画面右侧、女主在画面左侧（也就是和正确站位相反）。只有一个人、或空镜、或特写时不算。
- dissolve：某一帧是两个画面叠在一起的半透明重影。
- text：可读文字、乱码、标志。
- broken：肢体变形、多指、脸部扭曲、两人身体穿插粘连。
- light：同一地点的光线前后明显跳变，或肤色明显偏橙偏黄。
- prop：悬空的东西、拿反的杯子、凭空出现在手里的大件物品、同一件东西同时出现两个。
- hands（V1.2）：同一帧里某个人的手超过两只、多指少指、两人的手粘在一起分不清是谁的、手表在两只手之间跳；算 broken。
- set（V1.2）：背景变成纯灰影棚底、纯黑底，或和前后帧完全不是同一个地方（分镜里没写换场）。
只输出 JSON：{"frames": [...], "regen": true/false, "issues": [{"frame": 1-4, "text": "简短中文", "kind": "her/face/outfit/people/axis/dissolve/text/broken/light/prop/set"}]}；没有严重问题就 issues 为空、regen=false。"""


def grid(mp4, out):
    """按时长均匀抽帧拼图：10 秒段抽 6 帧（3×2），5 秒段抽 4 帧（2×2）。V1.1 首测：4 帧漏掉了 10+10 第 7 轮中段那个换了外套的单人镜头。"""
    import live_common as L
    dur = float(subprocess.run(['/Users/vicky/Interactive storyline/.media-runtime/vivix-bin/ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(mp4)], capture_output=True, text=True).stdout or 10)
    n, cols = (6, 3) if dur > 7 else (4, 2)
    fr = [(k + 0.5) / n for k in range(n)]
    ins = []
    for f in fr: ins += ['-ss', f'{dur * f:.2f}', '-i', str(mp4)]
    lay = '|'.join(f"{'+'.join(['w0'] * (k % cols)) or '0'}_{'+'.join(['h0'] * (k // cols)) or '0'}" for k in range(n))
    fc = ';'.join(f'[{i}:v]scale=300:-2,setsar=1[v{i}]' for i in range(n)) + ';' + ''.join(f'[v{i}]' for i in range(n)) + f'xstack=inputs={n}:layout={lay}'
    subprocess.run([L.FFMPEG, '-v', 'error', '-y', *ins, '-filter_complex', fc, '-frames:v', '1', '-q:v', '3', str(out)], check=True)
    return n


def seg_check(mp4, cast=(), timeout=60, props=()):
    """V1.1：段内快检。返回 {regen, issues, dissolves}；叠化用本地检测（dissolve.scan），其余用视觉模型看 4 帧。"""
    import dissolve
    from pathlib import Path
    res = {'regen': False, 'issues': []}
    try:
        dz = dissolve.scan(str(mp4))['dissolves']
        if dz: res['issues'].append({'frame': 0, 'text': f'叠化转场 {dz[0][0]}–{dz[0][1]} 秒', 'kind': 'dissolve'}); res['regen'] = True
    except Exception as e: res['dissolve_err'] = str(e)[:120]
    g = Path(str(mp4)).with_suffix('.grid.jpg'); n = grid(mp4, g)
    b64 = base64.b64encode(open(g, 'rb').read()).decode()
    body = {'model': VLM, 'max_tokens': 1500, 'reasoning': {'effort': 'low'},
            'messages': [{'role': 'user', 'content': [{'type': 'text', 'text': (('剧情道具（允许出现，不算换装或凭空出现）：' + '、'.join(props) + '。披在她身上的毯子、外套之类按剧情允许。\n') if props else '') + SEG_CHECK.replace('4 帧（左上=第1帧，右上=第2帧，左下=第3帧，右下=第4帧）', f'{n} 帧（从左到右、从上到下依次是第 1–{n} 帧）').replace('1-4', f'1-{n}').replace('{allowed}', ('允许出镜的配角：' + '、'.join(cast) + '。') if cast else '')},
                                                      {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,' + b64}},
                                                      {'type': 'image_url', 'image_url': {'url': FACE_URL}},
                                                      {'type': 'image_url', 'image_url': {'url': HER_URL}}]}]}
    t0 = time.time()
    req = U.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                    headers={'Authorization': 'Bearer ' + director._key(), 'Content-Type': 'application/json'})
    with U.urlopen(req, timeout=timeout) as r: j = json.loads(r.read())
    txt = j['choices'][0]['message'].get('content') or ''
    m = re.search(r'\{.*\}', txt, re.S)
    v = json.loads(m.group(0)) if m else {}
    res['issues'] += [i for i in (v.get('issues') or []) if isinstance(i, dict)]
    res['regen'] = res['regen'] or bool(v.get('regen'))
    res['sec'] = round(time.time() - t0, 1)
    return res
