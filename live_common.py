"""Rafael｜这次，不是演的 · 开放式实时版 · 第三视角（观众看着两个人，画面里同时有男女主）：公共设置与提示词组装。
从 output/magnus-third-live-v1（V1.9）复制改写：流程、PE 规则和 Rafael 第三视角一致，角色、世界观和时间换成 Rafael 内容包。
规则来源 docs/互动剧实时生成规则-v0.1.md：三段（回应她的话 + 演绎 + 引出钩子）、两段并发、两段都好再连续播；
硬规则（景别锁定、表演克制、第一视角、她的手、瞳色、台词、钩子收尾）原文沿用 output/vivix-tests-20261022/live.py。
和原项目的区别：没有预设分支和结局，开场之后每一轮的视频都由观众的选择或输入实时生成，一直往下演。
第 1 段的首帧 = 上一轮第 2 段的最后一帧（第 1 轮用开场最后一帧）；第 2 段用参考图（同一张画面 + 男主脸）。"""
import re, os, sys
from pathlib import Path
ROOT = Path('/Users/vicky/Interactive storyline')
for line in (ROOT / '.env.vivix').read_text(encoding='utf-8').splitlines():
    k, s, v = line.strip().partition('=')
    if s and k.strip() in ('VIVIX_API_KEY', 'VIVIX_CA_BUNDLE'): os.environ.setdefault(k.strip(), v.strip().strip('"\''))
os.environ['PATH'] = str(ROOT / '.media-runtime/vivix-bin') + os.pathsep + os.environ.get('PATH', '')
sys.path.insert(0, str(ROOT))
from vivix_w1 import W1Client, JobFailed, PollTimeout, VivixError, MODEL  # noqa: E402
import vivix_w1 as _vw  # noqa: E402
_vw.MODEL = MODEL = 'vivix-w1-ultrafast'  # 2026-10-29 Vicky：先切 Fast，V1.5 提速方案一再切 ultrafast（实测 5 秒段提交到出片 10–12 秒；只改这个进程，vivix_w1.py 默认仍是普通档）

D = Path(__file__).resolve().parent
FFMPEG = str(ROOT / '.media-runtime/vivix-bin/ffmpeg')
SEG2_FIRST = False  # 两段都用首帧的写法试过（2026-10-24 S0603061c1）：没有身份母版，4 轮就变老、瞳色发橙，还拍出了女主正脸；保留开关但不用
SEG1_REF = True  # v0.15：第 1 段也用参考图（上一刻画面 + 身份母版 + 服装母版）。首帧续接没有母版，脸一轮轮变老、西装换成米色外套（v0.15 自测第 4、6、7、8 轮）
MODES = {'5+10': (5, 10), '5+15': (5, 15), '10+10': (10, 10)}  # V1.7：5+15 用于自动分流
SEG1_LOCK = ('10+10',)  # V0.17：10+10 第 1 段改成首尾帧都锁成上一刻画面（咪的修复验证 4/4 无硬错误）。Vivix 首尾帧和参考图不能混用，所以这一段没有身份母版；它的末帧不传给下一轮，漂移不累积

# v0.7（2026-10-24）：按 Seedance/Vivix 的多镜头写法重写。提示词压短、只写要出现的东西，约束放在最后一句；
# 反向描述（“不出现她的头发、肩膀”“没有警徽”）会把这些东西招出来，全部删掉。旧版见 live_common.v5.py。
import json as _json
TU = _json.loads((Path(__file__).resolve().parent / 'masters' / 'urls.json').read_text())
CAST = {
    'Evan': ('Evan：二十八岁男人，白皙皮肤，灰绿色眼睛，灰金色短发整齐侧分后梳，干净无胡须，窄长脸，高颧骨，瘦高体型；灰蓝色短袖细针织 polo 衫，深色阔腿长裤。长相和衣着以他的身份母版为准。', TU['evan']),
    'Maya': ('Maya：二十六岁女人，暖棕色皮肤，深棕色杏眼，黑色及锁骨的自然卷发、侧分，一对小银圈耳环；黑白格纹短款衬衫，黑色罗纹袖口和下摆，牛仔裤。长相和衣着以她的身份母版为准。', TU['maya']),
    'Cole': ('Cole：三十一岁男人，健壮，方圆脸，晒过的浅麦色皮肤，灰蓝色眼睛，沙棕色短发和修剪整齐的短胡子；深烟草色麂皮短夹克敞开，里面象牙色棉衬衫。长相和衣着以他的身份母版为准。', TU['cole']),
    'Ryan': ('Ryan：二十二岁男人，瘦削，浅象牙色皮肤，鼻梁有淡雀斑，榛色眼睛，蓬松的铜棕色短发，干净无胡须；敞开的深靛蓝短袖工装衬衫，黑色领边，黑色圆领内搭。长相和衣着以他的身份母版为准。', TU['ryan']),
}
RAF = ('Rafael：二十六岁男人，一米八七，肩背宽阔，皮肤光滑干净没有胡茬，瘦长脸、两颊微凹、下颌线干净利落，浓黑平直的粗眉压在深邃的眼睛上，深棕色眼睛，直鼻，饱满的嘴唇，凌乱翘起的黑色短发、几缕垂在额前；右侧颈部黑色荆棘纹身，一条粗银链，两条小臂满臂纹身。'
       '日常穿着：褪色炭灰色圆领 T 恤，浅色水洗蓝牛仔裤；手指上空无一物。他的长相和服装全程不变，以参考的身份母版为准。')
HER_FP = '她的手外形全程固定：纤细白皙的女性双手，指甲短而圆、裸色素甲，手指和手腕上空无一物，袖口是奶油色开衫的长袖。'
HER = ('她：二十多岁的成年女人，白皙皮肤，成熟精致的脸，高颧骨、窄下颌、细直的鼻子，灰蓝色眼睛，柔和的灰褐色眼妆，鼻梁上淡淡的雀斑，豆沙玫瑰色的饱满嘴唇，不显幼态；很长的冷调灰金层次长发、发根略深、脸旁有碎发；'
       '奶油色长袖开衫，里面奶油色和黑色条纹的针织上衣，奶油白阔腿长裤，条纹系带腰带，黑色平底鞋；'
       '指甲短而圆、裸色素甲，手指和手腕上空无一物。她的长相、发型和服装全程不变，严格以她的身份母版（正面头像、全身正面、多角度）为准。她的表情自然克制，情绪在眼神里。')
WOLF = ''
SEAM = '第一个镜头接着上一刻往下演：两个人的姿势、手的位置和道具的状态都和上一刻一样，不把上一刻已经做完的动作再做一遍；换景别时同时换机位，不在同一个机位上突然放大缩小。'  # V1.2：评分里接缝跳回首帧、同轴跳切扣分最多
KISS = '吻戏的拍法（V1.4）：靠近只用一个干脆的动作，不慢慢凑近；从嘴唇贴上开始，到动作里写明分开之前，是同一次连续的吻，正常速度，动作一直在细微地变化（头部角度微调、他的手在她背上收紧、她的手指攥紧他的衣领），不慢动作、不定格、不僵住；切镜之后的镜头一开始两人就已经在接吻，接着上一镜继续，不重新靠近，不中途分开再吻；手的特写里手一定在动。两人的五官、发型、服装和男左女右在吻中保持不变：每个接吻镜头里 Rafael 的脸都在画面左半边、脸朝画面右侧，她的脸都在画面右半边、脸朝画面左侧，近景和侧面近景也不对调（V1.4 便携包自测第 1 轮最后一个接吻近景两人左右对调）。'
ACT = '表演自然：Rafael 放松时带一点懒散的笑意，认真时笑意收住、目光聚焦，说话轻缓，不压嗓、不耳语；她说话轻而清楚；情绪在眼神和嘴角。'
STYLE = ('画面和角色参考图是同一种渲染和画质：高级半写实 2.5D 三维角色渲染，皮肤细节自然，眼睛和睫毛清晰，发丝分明，织物质感清楚，对比干净；不雾、不柔焦、脸上不发光、不磨皮、不塑料感、不动漫，标准焦段，五官比例自然，画风全程统一；时间和光线按这个地点写的来，肤色保持参考图的颜色，不偏橙不偏黄。'
         '镜头之间一律硬切，不用叠化、溶镜、淡入淡出、闪白或闪黑；同一地点所有镜头的光线、色温和色调完全一致，跟随这个地点的主光源，不突然变冷变暖、变亮变暗。')


STAGING = {
    'face': '站位：两人面对面站着，相距一臂到半臂，Rafael 在画面左侧、她在画面右侧，两人都是三分之四侧脸朝着对方。',
    'side': '站位：两人并排坐着（沙发、餐桌同一侧、吧台或长椅），Rafael 在画面左侧、她在画面右侧，上身侧过来朝向对方；不是面对面坐。',
    'bed': '站位：两人在同一张床上，Rafael 坐在床沿、在画面左侧，上身侧过来朝向她；她靠坐在床头、被子盖到腰、在画面右侧，三分之四侧脸朝着他；房间里只有一张床。',
}


def stage_text(st, place):
    return STAGING[st]


FRAMING = {'特写': '特写（只拍眼睛、手或物件）', '近景': '近景（胸部以上）', '中近景': '中近景（腰部以上）', '插入特写': '插入特写（只拍手或物件）', '中景': '中景（膝盖以上）', '全景': '全景（人物全身和周围空间）',
           '空镜': '空镜（这个地点的环境，画面里没有任何人）',
           '双人全景': '双人全景（两人全身和周围空间都在画面里，男左女右）', '双人中景': '双人中景（两人膝盖以上同框，男左女右）',
           '双人中近景': '双人中近景（两人腰部以上同框，男左女右）', '双人近景': '双人近景（两人胸部以上同框，男左女右，两张脸都清楚）',
           '单人中近景': '单人中近景（一个人腰部以上）', '单人近景': '单人近景（一个人胸部以上）'}
FRAMING_KEYS = ('双人全景', '双人中景', '双人中近景', '双人近景', '单人中近景', '单人近景', '插入特写', '空镜', '中近景', '中景', '全景', '近景', '特写')


def framing(shot):
    """景别后面补上构图范围。V1.1 起景别按剧情灵活用（全景交代空间、中景看动作、近景看判断、特写看细节）。"""
    for k in FRAMING_KEYS:
        if shot.startswith(k): return FRAMING[k] + shot[len(k):]
    return shot


def pov(cast):
    who = 'Rafael（画面左侧）和她（画面右侧）两个人' if not cast else 'Rafael（画面左侧）、她（画面右侧）和 ' + '、'.join(cast) + ' 三个人'
    return (f'第三人称电影镜头：观众站在旁边看着他们，不是任何人的主观视角。主要人物是{who}。'
            '景别和机位按每个镜头写的来（全景、中景、近景、特写、空镜交替，可以略俯、略仰），他比她高一个头；两人同在画面里时 Rafael 永远在画面左侧、她永远在画面右侧，不越轴，两人都不背对镜头。')


EVENT_SOUND = ('车停', '停车', '车轮', '刹车', '敲门', '脚步', '狼嚎', '来电', '铃', '门开', '开门', '喊', '叫', '人声', '说话声')


def steady(amb):
    """环境声里去掉事件声（车停、敲门、脚步、狼嚎……）：事件只在写到它的那一拍发生。"""
    parts = [x for x in re.split('[，,、；;]', amb) if x and not any(w in x for w in EVENT_SOUND)]
    return '，'.join(parts) or '安静的室内环境声'


def tail(amb, cast):
    voice = 'Rafael 是二十多岁偏低、松弛、带一点颗粒和笑意的美式英语男声，她是轻柔清亮的美式英语女声'
    return (f'只说上面写出的英文台词，每句只说一遍；{voice}；说话的人口型同步，不说话的人闭着嘴。保留{amb}，没有背景音乐。'
            '画面里的东西只因看得见的动作出现和改变，同一样东西同一时刻只有一个，不悬空、不穿进身体；画面里的手只长在 Rafael 和她身上，每人最多两只，两人的手不粘连。门、墙面、纸张都是素面的，衣服上没有文字和标志。每一秒都是铺满整个竖屏的完整画面，从头到尾亮度和色调不变；不出现画中画、相框、边框、黑边、暗角、四周压暗或变模糊、中间一块亮框，也不突然变色、变暗、变亮。约束：无字幕，无文字，无标志，无旁白，除写到的人物外没有其他人。')


CAM_WORDS = [('看着她', '看着镜头'), ('看向她', '看向镜头'), ('盯着她', '盯着镜头'), ('朝她', '朝镜头'), ('向她', '向镜头'), ('对她', '对着镜头'),
             ('离她', '离镜头'), ('她面前', '镜头前'), ('她脸侧', '镜头前'), ('她脸边', '镜头前'), ('她身边', '镜头旁'), ('她身侧', '镜头旁'), ('她身旁', '镜头旁'),
             ('她左侧', '镜头左侧'), ('她右侧', '镜头右侧'), ('她左边', '镜头左侧'), ('她右边', '镜头右侧'), ('和她', '和镜头'), ('与她', '与镜头'), ('她的脸', '镜头'),
             ('等她', '等着'), ('给她', '给镜头'), ('她', '镜头')]


def cam(t):
    """第三视角：她在画面里，分镜里的“她”照写；只保留物件写法的修正。"""
    for w in ('工单', '账单', '文件', '协议'):  # V0.17c：纸写成没有可读文字的纸
        if w in t and '素面' not in t: t = t.replace(w, w + '（一张没有任何可读文字的纸）', 1); break
    return t


def side_of(shot, act, speaker=''):
    """第三视角：双人镜头写“Rafael 在画面左侧、她在画面右侧”；单人近景写清是谁、在画面哪一侧、看向哪边，另一个人在画外。
    第三视角 v1 第 4 轮车里的双人近景拍成了反打（她到了左边），第 5、6 轮的过肩镜头也换了边。"""
    shot = str(shot)
    if shot.startswith('空镜'): return ''
    if shot.startswith('双人'): return 'Rafael 在画面左侧、她在画面右侧（从这一镜的第一秒起就是这样），'  # V1.3：MD-B 越轴都发生在段落开头几秒
    if shot.startswith('单人'):
        her = speaker == '她' or (speaker != 'Rafael' and re.match(r'(切到)?(她|她的)', act or '') is not None)
        return ('画面里只有她一个人，她在画面右半边、看向画面左侧的他（他在画外），' if her
                else '画面里只有 Rafael 一个人，他在画面左半边、看向画面右侧的她（她在画外），')
    return ''


def shots(beats, dur, start=0, first=1, marks=None):
    """每一拍写成一个镜头：镜头N（起–止秒）【景别，运镜】动作 他说："台词"；镜头之间用“切到”。"""
    kiss = any('吻' in str(b[0]) for b in beats)
    w = [(0.7 if str(b[2] if len(b) > 2 else '').startswith(('插入特写', '特写')) else 1.6 if '仍在接吻' in str(b[0]) or ('吻' in str(b[0]) and '分开' not in str(b[0])) else 1.0) if kiss else 1.0 for b in beats]  # V1.4：吻戏里接吻的拍子长、手的特写短（V1.3 等分，吻 2.5 秒、静止的手 3 秒）
    cut = [start + (dur - start) * sum(w[:i]) / sum(w) for i in range(len(beats) + 1)]
    out = []; here = ''
    for k, b in enumerate(beats):
        a, l = cam(b[0]), b[1]; shot = framing(b[2] if len(b) > 2 and b[2] else '近景，固定')
        m = re.match(r'切到([^：:，,。]{2,12})[：:，,]', a)
        if m and not re.search(r'景|特写|镜头|他|她|Rafael|两人', m.group(1).replace('的空镜', '')): here = m.group(1).replace('的空镜', '')  # 第三视角常写“切到她的单人近景”：那是切镜不是换地点
        elif here: a = f'（仍在{here}）' + a  # 换场之后的每一拍都写明地点：参考图还是上一个地点，不写模型会切回去（v0.15 第 3 轮车里的戏最后回到了车库）
        who = b[3] if len(b) > 3 and b[3] else 'Rafael'
        if not l: say = ''
        elif who.startswith('画外'): say = f'，画外传来{who.split(":", 1)[-1].split("：", 1)[-1] or "门外的人"}的声音："{l}"，画面里的 Rafael 和她都闭着嘴在听，这句话不是他们说的，只用眼神回应'
        elif who == 'Rafael':
            a = re.sub(r'[，,]?\s*(低声|轻声|沉声)?(开口|回应|回答)?(说|道)?(镜头|她)?$', '', a) if re.search(r'(说|开口|回应|回答)(镜头|她)?$', a) else a  # 避免“低声说，他说”
            say = f'，他说："{l}"' if a.strip('，, ') not in ('', '他') else f'他说："{l}"'
            if not say.startswith('，'): a = ''  # v0.8 写成“Rafael 低声说”后出现了烧录字幕，改回
        elif who == '她': say = f'，她轻声说（女声，只有她的嘴在动，Rafael 闭着嘴听）："{l}"'
        else: say = f'，{who} 说："{l}"'
        sh = b[2] if len(b) > 2 else ''
        a = re.sub(r'^切(到|回)(他|她|Rafael|两人)?的?(单人|双人)?(中近景|近景|特写)[，,：:]\s*', '', a)  # 景别已经写在【】里
        if '门' in a and not any(c in a for c in CAST) and not who.startswith('画外'): a += '（门口和门外空无一人）'  # 第三视角 v1 第 8 轮：拍到门，门口背景里多出一个西装男人
        sd = side_of(sh, b[0], who if l else '')
        mm = re.match(r'(切到[^：:，,。]{2,12}[：:，,])', a)
        if k > 0 and '她在画面右侧' in sd and '空镜' not in str(sh): sd += '机位和上一个镜头在两人的同一侧，只是景别变了，不是反打，不绕到两人另一边；'  # kisstest
        a = (mm.group(1) + sd + a[mm.end():]) if mm else sd + a  # 换场那一拍：先写“切到新地点：”，再写站边  # 第三视角 v1 第 4–6 轮越轴：每个镜头都写明谁在画面哪一侧
        t = f'镜头{first + k}（{round(cut[k])}–{round(cut[k + 1])}秒）【{shot}】{a}' + say + (marks[k] if marks else '')
        out.append(t if k == 0 else '切到' + t)
    return '。'.join(out) + '。' + (KISS if kiss else '')


def take(beats, dur):
    """V0.17：首尾帧锁的一镜到底。几拍是同一个固定镜头里先后发生的动作，只写时间轴，不写景别、不写“切到”。"""
    step = dur / len(beats); out = []
    for k, b in enumerate(beats):
        a, l = cam(b[0]), b[1]; who = b[3] if len(b) > 3 and b[3] else 'Rafael'
        a = re.sub(r'[，,]?\s*(低声|轻声|沉声)?(开口|回应|回答)?(说|道)?(镜头|她)?$', '', a) if re.search(r'(说|开口|回应|回答)(镜头|她)?$', a) else a
        if not l: say = ''
        elif who.startswith('画外'): say = f'，画外传来{who.split(":", 1)[-1].split("：", 1)[-1] or "门外的人"}的声音："{l}"，画面里的 Rafael 和她都闭着嘴在听，这句话不是他们说的，只用眼神回应'
        elif who == '她': say = f'，她轻声说（女声，只有她的嘴在动，Rafael 闭着嘴听）："{l}"'
        else: say = f'，他说："{l}"'
        out.append(f'（{round(k * step)}–{round((k + 1) * step)}秒）{a}' + say)
    return '。'.join(out) + '。'


timed = shots  # 旧名字，replay/make_log 里可能还在用


def moved(sp, set_start):
    """这一轮第 2 段换到了新地点（和 prompts 里的判断一致）。"""
    s0 = (set_start or sp.get('set') or '').rstrip('。'); s1 = (sp.get('set') or '').rstrip('。')
    return bool(sp.get('scene_changed') and s1 and s1 != s0)


TOUCH = re.compile(r'她的手|她的双手|她(?:的指尖|伸手|拉|握|牵|攥|抚|碰|摸|按|贴|拽|扯|捧)|拉着他|握着他|牵着他|攥着他')


def touches(beats):
    return any(TOUCH.search(b[0]) for b in beats)


def her_seg(hh):
    """her_hands 里写了“第1段/第2段”时，她的手只进那一段的提示词（v0.14 第 7 轮两段都写进去，第 2 段又冒出她的手）。"""
    a, b = any(w in hh for w in ('第1段', '第 1 段', '第一段')), any(w in hh for w in ('第2段', '第 2 段', '第二段'))
    return (True, True) if a == b else (a, b)


JACKET = '他的外套'  # kisstest：他把外套给她之后，RAF 里“外套穿在身上”和服装母版会把外套画回他身上（S2343380d6 第 12、13 轮）
JACKET_ON = re.compile(r'(披|搭|裹)(到|在|上|住)[^。；]*(她|肩)|披着|裹着')
JACKET_OFF = re.compile(r'还给|还他|递还|递回|递出|递给他|穿回|重新穿|穿上|(取下|脱下)[^。；]*(还|递)')
JACKET_MARK = {(True, True): '（这个镜头里：她肩上披着他的外套，盖在她的奶油色开衫外面，近景和特写里也看得到；全片只有这一件外套，他只穿炭灰色 T 恤）',
               (True, False): '（这个镜头里：只有他的外套从她肩上拿下来，她自己的开衫一直穿在身上，不脱）',
               (False, True): '（这个镜头里：他的外套披到她肩上，盖在她的奶油色开衫外面；全片只有这一件外套，从这一刻起他只穿炭灰色 T 恤）'}


def jacket_step(on, a):
    """kisstest：这一拍之后，他的外套是否在她身上。按整拍判断，不按小句。"""
    a = str(a)
    if '外套' not in a: return on
    if not on and re.search('脱|滑下|滑落|褪|推|拨开|扯下|扔|手搭', a) and '她肩' not in a: return on  # V1.8：脱他的外套不等于披到她身上（第 6 轮“她的双手搭上他外套的衣领往肩后推开”被当成披到她肩上）
    if on and JACKET_OFF.search(a): return False
    if JACKET_ON.search(a): return True
    return on


def jacket_marks(beats, on):
    """kisstest：逐拍写明外套在谁身上（S003402461：只在开头写一次，吻戏近景里外套就丢了；交接那一拍她把自己的大衣也脱了）。"""
    marks = []
    for b in beats:
        after = jacket_step(on, b[0])
        empty = '空镜' in str(b[2] if len(b) > 2 else '') or '空镜' in str(b[0])
        marks.append('' if empty else JACKET_MARK.get((on, after), ''))
        on = after
    return marks, on


def _prompts(sp, mode, hands_in_frame=False, set_start=None, seg2_first=False, stage_start=None, worn=None, jacket_start=False):
    """第三视角：返回 [(时长, 提示词, 模式)]。模式 True=首帧续接、False=参考图、'lock'=首尾帧锁（10+10 第 1 段）。
    参考图顺序：不换场 [上一刻画面, Rafael 脸, Rafael 服装, 她, (Selene)]；换场的第 2 段 [两人站位母版, Rafael 脸, Rafael 服装, 她, (Selene)]。
    第 1 段永远在原地点、原站位；新地点和新站位只写进第 2 段。"""
    d1, d2 = MODES[mode]
    her_txt = HER + (f'这一刻她身上还加了剧情里披上的：{worn}，穿在奶油色开衫外面，全程保持，不要去掉。' if worn else '')  # V1.1 第 8–10 轮：他把外套披到她肩上，下一轮按固定外形写又把外套去掉了
    def dress(on):  # 每段开头按这一段开始时外套在谁身上写，这一轮中途交接由逐拍的状态句写
        if not on: return RAF, her_txt
        return RAF, her_txt + f'这一刻她肩上披着{JACKET}，盖在奶油色开衫外面，每个镜头里都在她肩上，全程保持，不要去掉。'
    marks1, on2 = jacket_marks(sp['seg1'], bool(jacket_start))
    marks2, _ = jacket_marks(sp['seg2'], on2)
    mag1, her1 = dress(bool(jacket_start)); mag2, her2 = dress(on2)
    ONE = '他的外套全片只有一件：写到披到她肩上的那个镜头之后，他身上就不再有外套，后面每个镜头他都只穿炭灰色 T 恤。'
    if not jacket_start and on2: mag1 += ONE
    if not on2 and any(jacket_step(False, b[0]) for b in sp['seg2']): mag2 += ONE
    wolf = WOLF if sp.get('wolf') else ''
    st1 = sp.get('staging') or 'face'
    st0 = stage_start if stage_start in STAGING else st1
    cast_all = [c for c in (sp.get('cast') or []) if c in CAST]
    def seg_cast(beats): return [c for c in cast_all if any(c in b[0] or (len(b) > 3 and b[3] == c) for b in beats)]
    c1, c2 = seg_cast(sp['seg1']), seg_cast(sp['seg2'])
    amb = sp.get('amb') or '安静的室内环境声和窗外远处的海风'
    amb1 = steady(amb)
    s0 = (set_start or sp.get('set') or '').rstrip('。'); s1 = (sp.get('set') or '').rstrip('。')
    moved = bool(sp.get('scene_changed') and s1 and s1 != s0)
    if not moved: st0 = st1
    else: amb1 = '安静的环境低鸣'  # 换场那一轮第 1 段还在原地点，不用新地点的环境声（第三视角 v1 干跑：车里配上了大宅的壁钟声）
    T0, T1 = stage_text(st0, s0), stage_text(st1, s1 + (sp.get('location') or ''))
    place1 = (f'地点：{s0}。' if s0 else '') + T0
    place2 = ((f'开头的地点：{s0}。' if s0 else '') + T0.replace('站位：', '开头的站位：') + f'切到新地点后：{s1}。' + T1.replace('站位：', '新地点的站位：')) if moved else place1
    people = 'Rafael 和她的长相、服装以这些图为准，它们的影棚背景不进画面'
    if moved:
        refs = '图片1是两人的站位参考：Rafael 在画面左侧、她在画面右侧（只参考左右站位和两人的样子），图片2是 Rafael 的脸，图片3是他的服装，图片4是她（女主）的身份母版（正面头像、全身正面、多角度）' + ''.join(f'，图片{5 + i}是 {c}' for i, c in enumerate(c2)) + f'，{people}；每个镜头的背景按下面写的地点。'
    else:
        refs = '图片2是 Rafael 的脸，图片3是他的服装，图片4是她（女主）的身份母版（正面头像、全身正面、多角度）' + ''.join(f'，图片{5 + i}是 {c}' for i, c in enumerate(c2)) + f'，{people}；图片1是上一刻的场景，每个镜头的背景、光线和色调都和图片1一致。'
    lead = '这一段紧接图片1那一刻：地点、背景、光线、两个人的位置、朝向和距离都和图片1一致，这一段不离开这个地点。'
    end = '最后停在两人同框的镜头上（男左女右，两张脸都看得到），留出悬念。'
    if mode in SEG1_LOCK and not seg2_first:  # 首尾帧锁，一镜到底，最后回到首帧
        lock = ('固定机位，一镜到底：镜头像架在三脚架上，全程不移动、不推近、不拉远、不切镜；两个人在画面里的大小和位置全程和首帧一样，'
                '画面上半部分的背景全程保持首帧的样子和位置。')
        lead = '首帧和尾帧是同一张画面（上一刻）：开头的场景、光线、两个人的长相、服装、位置、朝向和距离都与首帧一致，这一段不离开这个地点。两人的皮肤质感、他的瞳色和两人的发型全程和首帧完全一样。'
        p1 = (lock + pov(c1) + place1 + lead + mag1 + her1 + take(sp['seg1'], d1)
              + '最后 2 秒两人回到首帧的位置、姿势、表情和距离停住，画面和首帧一致。' + ACT + STYLE + tail(amb1, c1))
        hold2 = '图片1的画面（两人在原位的双人镜头）' if not moved else sp['hold'].rstrip('。')
        p2 = (refs + pov(c2) + place2 + mag2 + her2 + ''.join(CAST[c][0] for c in c2) + wolf
              + f'这一段从上一刻切过来，上一刻是：{hold2}。' + ('换场之前，' if moved else '') + '地点、背景、光线、两个人的位置和朝向与上一刻一致。' + SEAM
              + shots(sp['seg2'], d2, marks=marks2) + (f"最后停在{sp.get('location') or '新地点'}里，" if moved else '') + end + ACT + STYLE + tail(amb, c2))
        return [(d1, p1, 'lock'), (d2, p2, False)]
    lead = '这一段从首帧那一刻接着演：地点、背景、光线、两个人的长相、服装、位置、朝向和距离都和首帧一致，这一段不离开这个地点。'  # 第 1 段用首帧续接，和上一轮无缝接上；5 秒漂移小，末帧也不传给下一轮
    p1 = (pov(c1) + place1 + lead + mag1 + her1 + ''.join(CAST[c][0] for c in c1) + wolf
          + shots(sp['seg1'], d1, marks=marks1) + f'最后停在：{sp["hold"].rstrip("。")}。' + ACT + STYLE + tail(amb1, c1))
    p2 = (refs + pov(c2) + place2 + mag2 + her2 + ''.join(CAST[c][0] for c in c2) + wolf
          + f'这一段从上一刻切过来，上一刻是：{sp["hold"].rstrip("。")}。' + ('换场之前，' if moved else '') + '地点、背景、光线、两个人的位置和朝向与上一刻一致。' + SEAM
          + shots(sp['seg2'], d2, marks=marks2) + (f"最后停在{sp.get('location') or '新地点'}里，" if moved else '') + end + ACT + STYLE + tail(amb, c2))
    return [(d1, p1, True), (d2, p2, False)]


def seg2_cast_refs(sp):
    """第 2 段需要追加的配角身份母版（按出现顺序）。"""
    return [CAST[c][1] for c in (sp.get('cast') or []) if c in CAST and any(c in b[0] or (len(b) > 3 and b[3] == c) for b in sp['seg2'])]


def prompts(sp, mode, hands_in_frame=False, set_start=None, seg2_first=False, stage_start=None, worn=None, jacket_start=False):
    """第三视角不需要第一视角那套“并排坐时改写成三分之四侧脸”的补丁：站位句本身写清了男左女右。"""
    return _prompts(sp, mode, hands_in_frame, set_start, seg2_first, stage_start, worn, jacket_start)


# V1.5（Vicky：剧情需要时其他角色可以出现）：extras 写进提示词开头，末尾的“手只长在两人身上”放开；不多调用任何东西
_prompts_v14 = prompts


def prompts(sp, mode, *a, **kw):
    out = _prompts_v14(sp, mode, *a, **kw)
    xs = [x for x in (sp.get('extras') or []) if isinstance(x, dict) and x.get('name')]
    if not xs: return out
    res = []
    for k, (d, p, f) in enumerate(out):
        beats = sp['seg1' if k == 0 else 'seg2']
        here = [x for x in xs if any(x['name'] in str(b[0]) or (len(b) > 3 and b[3] == x['name']) for b in beats)]
        if here:
            names = '、'.join(x['name'] for x in here)
            p = '这一段还有：' + '；'.join(f"{x['name']}（{x.get('look') or ''}）" for x in here) + '。长相和衣服全程不变，只在写到的镜头里出现，说话时口型同步。' + p
            p = p.replace('画面里的手只长在 Rafael 和她身上', f'画面里的手只长在 Rafael、她和{names}身上')
        res.append((d, p, f))
    return res


# V1.8：穿着状态、末尾约束、字幕时间。都是拼字符串，不多调用
HE_DEFAULT = '褪色炭灰色圆领 T 恤，浅色水洗蓝牛仔裤'
SHE_DEFAULT = '奶油色长袖开衫，奶油色和黑色条纹针织上衣，奶油白阔腿长裤'
_HE_RE = re.compile(r'日常穿着：.*?以参考的身份母版为准。', re.S)
_SHE_RE = re.compile(r'奶油色长袖开衫.*?黑色平底鞋；', re.S)
_SHE_END = '她的长相、发型和服装全程不变，严格以她的身份母版（正面头像、全身正面、多角度）为准。'
_NIGHT = '时间是深夜，室内暖灯，窗外是夜色；在室外时天空是黑色的夜空，只有灯光和月光，没有白天的天光、蓝天和白云。'
TAIL_V18 = '每个人只有两只手、两条胳膊，没有悬空、不连着身体的手臂和袖子；同一件衣服只有一件，衣服不穿进身体，脱下来的衣服落下后留在原处。'
TAIL_INTIMATE = '两人都是成年人，这是含蓄的爱情戏：镜头停在脸、肩和手上，床上的镜头两人盖着被子。'  # 写身体部位的否定句本身会触发 Vivix 内容审核（S040307dee 第 1 轮连牵手的第 1 段都被拦）


def _dress(p, w):
    he, she = w.get('he'), w.get('she')
    if he: p = _HE_RE.sub(lambda m: f'此刻他的穿着：{he}，就按这个样子，不自己穿回去；颈部纹身、银链和小臂纹身不变，手指上空无一物。他的长相全程不变。', p)
    if she:
        p = _SHE_RE.sub(lambda m: f'此刻她的穿着：{she}，就按这个样子，不自己穿回去；', p)
        p = p.replace(_SHE_END, '她的长相和发型全程不变，以她的身份母版为准；身份母版里的衣服不用看，穿着按这里写的。')
    return p


_WEAR_RE = re.compile('脱|解开|解下|褪|滑下|滑落|拨开|敞开|掀开|扯开|推|穿上|穿回|披上|系上|扣上|扣好|换上')


def _wear_note(w):
    t = []
    if w.get('he'): t.append(f"Rafael：{w['he']}")
    if w.get('she'): t.append(f"她：{w['she']}")
    return '（这个镜头的穿着，' + '；'.join(t) + '）' if t else ''


def _mark_shots(p, beats, start, end):
    """每个镜头标当前穿着：变化那一拍（最后一个写了穿脱动作的拍子）之前按开头，之后按结束。"""
    last = max([i for i, b in enumerate(beats) if _WEAR_RE.search(str(b[0]))], default=-1) if end != start else -1
    n = [-1]
    def sub(m):
        n[0] += 1
        w = end if (end != start and n[0] > last) else start
        return m.group(0) + _wear_note(w)
    return re.sub(r'镜头\d+（[^）]*）【[^】]*】', sub, p)


_prompts_v17 = prompts


def prompts(sp, mode, *a, **kw):
    out = _prompts_v17(sp, mode, *a, **kw)
    start, end = sp.get('wardrobe_start') or {}, sp.get('wardrobe_end') or {}
    res = []
    for k, (d, p, f) in enumerate(out):
        if sp.get('wardrobe_changed'):
            p = _dress(p, start)
            if start.get('tod'): p = p.replace(_NIGHT, '时间是清晨，窗外是柔和的晨光，室内是自然的晨光。').replace('深夜，', '').replace('深夜的', '').replace('深夜', '')
            stay = not sp.get('scene_changed')  # 不换地点：第 1 段首尾锁成上一刻的画面，第 2 段的第一张参考图也是它，接缝不跳，房间和穿着也接得上（第 4、5 轮换过房间）
            if k == 0 and stay and f is True: f = 'lock'; p = p.replace('最后停在：', '最后回到和首帧一样的位置和姿势：', 1)
            if k == 1:
                i = p.find('第三人称电影镜头')
                if i > 0 and not f:
                    if stay: p = '图片1就是这一段的场景和上一刻的画面：房间、床、灯、光线、两人的穿着和位置都和图片1一样，这一段不离开这个地方；图片2只看 Rafael 的脸和头发，不看他的衣服，图片3只看她的脸和头发，不看她的衣服；两人的长相和画风以这些图为准，穿着按每个镜头写的。' + p[i:]  # 只用首帧时 4 轮就换脸（头发变棕、变真人画风），所以第 2 段仍带脸的参考图
                    else: p = '图片1是上一刻的画面：两人的长相和此刻的穿着都接着它（背景换成下面写的新地点）；图片2是 Rafael 的脸；图片3只看她的脸和头发，不看她的衣服。' + p[i:]
                if end != start:
                    p = p.replace('他的长相和服装全程不变，以参考的身份母版为准。', '他的长相全程不变，穿着按写到的动作变化。').replace(_SHE_END, '她的长相和发型全程不变，穿着按写到的动作变化。').replace('全程穿在身上；', '开头穿在身上；')
                    p += f"这一段的穿着变化：开头是（Rafael：{start.get('he', HE_DEFAULT)}；她：{start.get('she', SHE_DEFAULT)}），只在写到的那一拍变化，之后是（Rafael：{end.get('he', start.get('he', HE_DEFAULT))}；她：{end.get('she', start.get('she', SHE_DEFAULT))}），不再变回去。"
        if sp.get('wardrobe_changed'): p = _mark_shots(p, sp['seg1' if k == 0 else 'seg2'], start, end if k == 1 else start)  # V1.8：逐镜头写穿着（只写在段首时，参考图会把衣服带回去：S041550316 第 2、3 轮）
        p += TAIL_V18
        if k == 1 and int(sp.get('intimacy') or 0) >= 3: p += TAIL_INTIMATE
        res.append((d, p, f))
    return res


def line_times(sp, mode):
    """V1.8：每句台词在这一段里说的时间窗（和 shots 的分拍一致），播放页只在这个时间里显示字幕。"""
    d1, d2 = MODES[mode]; out = {}
    for k, dur in (('seg1', d1), ('seg2', d2)):
        beats = sp.get(k) or []; kiss = any('吻' in str(b[0]) for b in beats)
        w = [(0.7 if str(b[2] if len(b) > 2 else '').startswith(('插入特写', '特写')) else 1.6 if '仍在接吻' in str(b[0]) or ('吻' in str(b[0]) and '分开' not in str(b[0])) else 1.0) if kiss else 1.0 for b in beats]
        cut = [dur * sum(w[:i]) / max(sum(w), 1) for i in range(len(beats) + 1)]
        z = (sp.get('zh') or {}).get(k) or []; rows = []
        for i, b in enumerate(beats):
            if not b[1]: continue
            who = str(b[3]) if len(b) > 3 and b[3] else 'Rafael'; who = who.split(':', 1)[-1].split('：', 1)[-1]
            s = cut[i] + 0.2; e = min(cut[i + 1], s + max(1.4, len(str(b[1]).split()) * 0.45 + 0.6))
            rows.append({'en': b[1], 'zh': z[i] if i < len(z) else '', 'who': who, 's': round(s, 1), 'e': round(e, 1)})
        out[k] = rows
    return out

