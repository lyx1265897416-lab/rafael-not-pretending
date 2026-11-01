# 一次性迁移脚本：把 Magnus 第三视角 V1.9 的 live_common / qa_guard / relay 改成 Rafael
import re
def sub(t, a, b, n=None):
    assert a in t, a[:60]
    return t.replace(a, b) if n is None else t.replace(a, b, n)
def line(t, prefix, new):
    ls = t.split('\n'); hit = [i for i, l in enumerate(ls) if l.startswith(prefix)]
    assert len(hit) == 1, (prefix[:50], len(hit)); ls[hit[0]] = new; return '\n'.join(ls)

# ---------- live_common
t = open('live_common.py').read()
t = line(t, '"""Magnus｜午夜车库', '"""Rafael｜这次，不是演的 · 开放式实时版 · 第三视角（观众看着两个人，画面里同时有男女主）：公共设置与提示词组装。')
t = line(t, '第三视角版（2026-10-27）', '从 output/magnus-third-live-v1（V1.9）复制改写：流程、PE 规则和 Magnus 第三视角一致，角色、世界观和时间换成 Rafael 内容包。')
t = line(t, 'SELENE_URL = ', "import json as _json\nTU = _json.loads((Path(__file__).resolve().parent / 'masters' / 'urls.json').read_text())")
t = line(t, 'CAST = {', """CAST = {
    'Evan': ('Evan：二十八岁男人，白皙皮肤，灰绿色眼睛，灰金色短发整齐侧分后梳，干净无胡须，窄长脸，高颧骨，瘦高体型；灰蓝色短袖细针织 polo 衫，深色阔腿长裤。长相和衣着以他的身份母版为准。', TU['evan']),
    'Maya': ('Maya：二十六岁女人，暖棕色皮肤，深棕色杏眼，黑色及锁骨的自然卷发、侧分，一对小银圈耳环；黑白格纹短款衬衫，黑色罗纹袖口和下摆，牛仔裤。长相和衣着以她的身份母版为准。', TU['maya']),
    'Cole': ('Cole：三十一岁男人，健壮，方圆脸，晒过的浅麦色皮肤，灰蓝色眼睛，沙棕色短发和修剪整齐的短胡子；深烟草色麂皮短夹克敞开，里面象牙色棉衬衫。长相和衣着以他的身份母版为准。', TU['cole']),
    'Ryan': ('Ryan：二十二岁男人，瘦削，浅象牙色皮肤，鼻梁有淡雀斑，榛色眼睛，蓬松的铜棕色短发，干净无胡须；敞开的深靛蓝短袖工装衬衫，黑色领边，黑色圆领内搭。长相和衣着以他的身份母版为准。', TU['ryan']),
}""")
i = t.index("MAG = ('Magnus"); j = t.index("HER_FP = ")
t = t[:i] + """RAF = ('Rafael：二十六岁男人，一米八七，肩背宽阔，皮肤光滑干净没有胡茬，瘦长脸、两颊微凹、下颌线干净利落，浓黑平直的粗眉压在深邃的眼睛上，深棕色眼睛，直鼻，饱满的嘴唇，凌乱翘起的黑色短发、几缕垂在额前；右侧颈部黑色荆棘纹身，一条粗银链，两条小臂满臂纹身。'
       '日常穿着：褪色炭灰色圆领 T 恤，浅色水洗蓝牛仔裤；手指上空无一物。他的长相和服装全程不变，以参考的身份母版为准。')
""" + t[j:]
t = re.sub(r'\bMAG\b', 'RAF', t)
t = line(t, 'HER_FP = ', "HER_FP = '她的手外形全程固定：纤细白皙的女性双手，指甲短而圆、裸色素甲，手指和手腕上空无一物，袖口是奶油色开衫的长袖。'")
i = t.index("HER = ('她："); j = t.index("WOLF = (")
t = t[:i] + """HER = ('她：二十多岁的成年女人，白皙皮肤，成熟精致的脸，高颧骨、窄下颌、细直的鼻子，灰蓝色眼睛，柔和的灰褐色眼妆，鼻梁上淡淡的雀斑，豆沙玫瑰色的饱满嘴唇，不显幼态；很长的冷调灰金层次长发、发根略深、脸旁有碎发；'
       '奶油色长袖开衫，里面奶油色和黑色条纹的针织上衣，奶油白阔腿长裤，条纹系带腰带，黑色平底鞋；'
       '指甲短而圆、裸色素甲，手指和手腕上空无一物。她的长相、发型和服装全程不变，严格以她的身份母版（正面头像、全身正面、多角度）为准。她的表情自然克制，情绪在眼神里。')
""" + t[j:]
i = t.index("WOLF = ("); j = t.index("SEAM = ")
t = t[:i] + "WOLF = ''\n" + t[j:]
t = line(t, "ACT = ", "ACT = '表演自然：Rafael 放松时带一点懒散的笑意，认真时笑意收住、目光聚焦，说话轻缓，不压嗓、不耳语；她说话轻而清楚；情绪在眼神和嘴角。'")
i = t.index("STYLE = ("); j = t.index("STAGING = {")
t = t[:i] + """STYLE = ('画面和角色参考图是同一种渲染和画质：高级半写实 2.5D 三维角色渲染，皮肤细节自然，眼睛和睫毛清晰，发丝分明，织物质感清楚，对比干净；不雾、不柔焦、脸上不发光、不磨皮、不塑料感、不动漫，标准焦段，五官比例自然，画风全程统一；时间和光线按这个地点写的来，肤色保持参考图的颜色，不偏橙不偏黄。'
         '镜头之间一律硬切，不用叠化、溶镜、淡入淡出、闪白或闪黑；同一地点所有镜头的光线、色温和色调完全一致，跟随这个地点的主光源，不突然变冷变暖、变亮变暗。')


""" + t[j:]
i = t.index("STAGING = {"); j = t.index("FRAMING = {")
t = t[:i] + """STAGING = {
    'face': '站位：两人面对面站着，相距一臂到半臂，Rafael 在画面左侧、她在画面右侧，两人都是三分之四侧脸朝着对方。',
    'side': '站位：两人并排坐着（沙发、餐桌同一侧、吧台或长椅），Rafael 在画面左侧、她在画面右侧，上身侧过来朝向对方；不是面对面坐。',
    'bed': '站位：两人在同一张床上，Rafael 坐在床沿、在画面左侧，上身侧过来朝向她；她靠坐在床头、被子盖到腰、在画面右侧，三分之四侧脸朝着他；房间里只有一张床。',
}


def stage_text(st, place):
    return STAGING[st]


""" + t[j:]
t = sub(t, "voice = 'Magnus 是低沉略哑的美式英语男声，她是轻柔清亮的美式英语女声' + ('，Selene 是冷淡优雅的英式女声' if 'Selene' in cast else '')", "voice = 'Rafael 是二十多岁偏低、松弛、带一点颗粒和笑意的美式英语男声，她是轻柔清亮的美式英语女声'")
t = sub(t, '门、墙面、旗帘、纸张和衣服都是素面的。', '门、墙面、纸张都是素面的，衣服上没有文字和标志。')
t = sub(t, "    if '车门' in t and '黑' not in t: t = t.replace('车门', '黑色 Maybach 的车门', 1)  # v0.15 10+10 第 2 段车门插入特写拍成了白车\n", '')
t = sub(t, "for w in ('契约', '婚约书', '文书', '协议'):  # V0.17c：纸写成没有字的素面厚纸", "for w in ('工单', '账单', '文件', '协议'):  # V0.17c：纸写成没有可读文字的纸")
t = sub(t, '（一张没有任何字迹的素面厚纸，只有一枚红色火漆印）', '（一张没有任何可读文字的纸）')
t = t.replace('他低声说', '他说')
t = sub(t, "JACKET = '他的黑色西装外套'", "JACKET = '他的外套'")
t = sub(t, "(True, True): '（这个镜头里：她肩上披着他的黑外套，盖在她的灰褐色长大衣外面，近景和特写里也看得到；全片只有这一件黑外套，他身上没有外套，只穿黑马甲和黑衬衫）'", "(True, True): '（这个镜头里：她肩上披着他的外套，盖在她的奶油色开衫外面，近景和特写里也看得到；全片只有这一件外套，他只穿炭灰色 T 恤）'")
t = sub(t, "(True, False): '（这个镜头里：只有他的黑外套从她肩上拿下来，她自己的灰褐色长大衣一直穿在身上，不脱）'", "(True, False): '（这个镜头里：只有他的外套从她肩上拿下来，她自己的开衫一直穿在身上，不脱）'")
t = sub(t, "(False, True): '（这个镜头里：他身上的黑外套脱下来披到她肩上，盖在她的灰褐色长大衣外面，她的大衣不脱；全片只有这一件黑外套，从这一刻起他身上没有外套，只穿黑马甲和黑衬衫）'", "(False, True): '（这个镜头里：他的外套披到她肩上，盖在她的奶油色开衫外面；全片只有这一件外套，从这一刻起他只穿炭灰色 T 恤）'")
t = sub(t, "    her_txt = HER + (f'这一刻她身上还加了剧情里披上的：{worn}，穿在灰褐色长大衣外面，全程保持，不要去掉。' if worn else '')", "    her_txt = HER + (f'这一刻她身上还加了剧情里披上的：{worn}，穿在奶油色开衫外面，全程保持，不要去掉。' if worn else '')")
t = sub(t, """        m = RAF.replace('黑色三件套西装，黑色外套穿在身上、袖子放下，黑色马甲', '黑色马甲和黑色长裤，他的外套已经脱下、披在她肩上（服装参考图里的外套不穿回他身上），黑色衬衫袖子放下')
        assert m != RAF
        return m, her_txt + f'这一刻她肩上披着{JACKET}，盖在灰褐色长大衣外面，每个镜头里都在她肩上，全程保持，不要去掉。'""", """        return RAF, her_txt + f'这一刻她肩上披着{JACKET}，盖在奶油色开衫外面，每个镜头里都在她肩上，全程保持，不要去掉。'""")
t = sub(t, "ONE = '他的黑外套全片只有一件：写到披到她肩上的那个镜头之后，他身上就不再有外套，后面每个镜头他都只穿黑马甲和黑衬衫。'", "ONE = '他的外套全片只有一件：写到披到她肩上的那个镜头之后，他身上就不再有外套，后面每个镜头他都只穿炭灰色 T 恤。'")
t = sub(t, "amb = sp.get('amb') or '地下车库的空调低鸣和远处的回声'", "amb = sp.get('amb') or '安静的室内环境声和窗外远处的海风'")
t = sub(t, '最后停在两人同框的镜头上（男左女右，两张脸都看得到，他人形），留出悬念。', '最后停在两人同框的镜头上（男左女右，两张脸都看得到），留出悬念。')
t = sub(t, "HE_DEFAULT = '黑色三件套西装，外套穿在身上，黑色马甲，黑色敞领衬衫，松开的黑色领带'", "HE_DEFAULT = '褪色炭灰色圆领 T 恤，浅色水洗蓝牛仔裤'")
t = sub(t, "SHE_DEFAULT = '灰褐色长大衣敞开穿在身上，里面灰蓝色罗纹针织无袖短裙，灰褐色粗跟短靴'", "SHE_DEFAULT = '奶油色长袖开衫，奶油色和黑色条纹针织上衣，奶油白阔腿长裤'")
t = sub(t, "_HE_RE = re.compile(r'一身全黑：.*?以参考的身份母版为准。', re.S)", "_HE_RE = re.compile(r'日常穿着：.*?以参考的身份母版为准。', re.S)")
t = sub(t, "_SHE_RE = re.compile(r'灰褐色（燕麦灰）羊毛长大衣.*?灰褐色粗跟短靴；', re.S)", "_SHE_RE = re.compile(r'奶油色长袖开衫.*?黑色平底鞋；', re.S)")
t = sub(t, "_SHE_END = '她的长相、发型和服装全程不变，严格以她的身份母版（正面头像、全身正面、侧面）为准。'", "_SHE_END = '她的长相、发型和服装全程不变，严格以她的身份母版（正面头像、全身正面、多角度）为准。'")
t = sub(t, "就按这个样子，不自己穿回去；左手腕一只银色钢带手表，十根手指上空无一物。他的长相全程不变。", "就按这个样子，不自己穿回去；颈部纹身、银链和小臂纹身不变，手指上空无一物。他的长相全程不变。")
t = t.replace('身份母版（正面头像、全身正面、侧面）', '身份母版（正面头像、全身正面、多角度）')
t = t.replace('Magnus', 'Rafael')
open('live_common.py', 'w').write(t)

# ---------- qa_guard
t = open('qa_guard.py').read()
t = line(t, '"""末帧质检与修复', '"""末帧质检与修复（第三视角：画面里同时有 Rafael 和她，两人都对照身份母版）：上一轮的末帧要当下一轮的首帧，一旦走样（多了人、换装、换脸）就会一路传下去。')
t = sub(t, 'import director\n', 'import director, live_common as _L\n')
t = line(t, 'FACE_URL = ', "FACE_URL = _L.TU['face']  # 白底正面头像身份母版")
t = line(t, 'OUTFIT_URL = ', "OUTFIT_URL = _L.TU['outfit']  # 裁成上半身（全身站姿的母版会把画面往全身拉）")
t = line(t, 'HER_URL = ', "HER_URL = _L.TU['her']  # 她：正面头像 + 全身正面 + 多角度合图")
i = t.index('CHECK = """'); j = t.index('NO_FIX = ')
t = t[:i] + '''CHECK = """图片1是一部观众第三视角互动剧的一帧画面：画面里应该同时有男主 Rafael 和女主（她），Rafael 在画面左侧、她在画面右侧。图片2是男主的身份母版，图片3是女主的身份母版（判断是不是同一个人以它们为准）。下一段视频会从这一帧接着生成，所以这一帧必须干净。请按下面的锁定项检查，只报你在画面上确实看到的问题：
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


''' + t[j:]
t = sub(t, "SIDE_RULE = '15. 站位（这一刻两人并排坐在车里或沙发上）：两人应并排坐、身体侧过来朝向对方，Magnus 在左、她在右。", "SIDE_RULE = '15. 站位（这一刻两人并排坐着）：两人应并排坐、身体侧过来朝向对方，Rafael 在左、她在右。")
t = sub(t, "（穿在灰褐色长大衣外面，这是允许的，不算换装；披的是他的外套时，他只穿马甲衬衫、她外面是黑外套都是对的）", "（穿在奶油色开衫外面，这是允许的，不算换装）")
t = sub(t, "becomes this real location at night: ", "becomes this real location, at the time of day it describes: ")
t = sub(t, "Same realistic 3D game CG style, warm night interior light.", "Same semi-realistic 2.5D character render style as the people in Image 1.")
t = sub(t, "Use Image 2 only as the reference for the man\\'s face, hair and amber-gold eyes. His outfit: an all-black three-piece suit (black jacket, black vest, open black shirt, '\n              'loosened black tie), jacket worn on his body, sleeves down; one silver steel watch on his own left wrist; no necklace, no chain, no badge, no rings, no pocket square. '", "Use Image 2 only as the reference for the man\\'s face, messy black hair and dark brown eyes. His outfit: a faded charcoal crew-neck T-shirt and light washed blue jeans; thick silver chain, black thorn tattoo on the right side of his neck, tattoo sleeves on both forearms; no rings, no watch, clean-shaven. '")
t = sub(t, "pale skin, grey-green eyes, waist-length layered ash-brown hair with soft light-blonde highlights, tiny silver stud earrings; '\n              'she wears an open single-breasted taupe wool long coat with notch lapels over a blue-grey ribbed knit sleeveless mini dress, taupe heeled ankle boots; slender pale hands, short rounded nude nails, no rings, no bracelets, no watch. '", "pale skin, grey-blue eyes, faint freckles, very long layered cool ash-blonde hair with darker roots; '\n              'she wears a cream long-sleeved cardigan over a cream-and-black striped knit top and cream wide-leg trousers; slender pale hands, short rounded nude nails, no rings, no bracelets, no watch. '")
t = sub(t, "No readable text. Same realistic 3D game CG style.')", "No readable text. Same semi-realistic 2.5D character render style.')")
t = t.replace("the man (Magnus)", "the man (Rafael)")
i = t.index("    if any('外套' in w for w in worn):  # kisstest"); j = t.index("    return _edit(prompt, [frame_url, FACE_URL, HER_URL], timeout)\n\n\ndef scene_diff")
t = t[:i] + "    if any('外套' in w for w in worn): prompt += ' His jacket stays draped over her shoulders on top of her cardigan.'\n" + t[j:]
i = t.index('SEG_CHECK = """'); j = t.index('正确的站位：两人同在一帧时')
t = t[:i] + 'SEG_CHECK = """图片1是一段 9:16 视频按时间顺序抽出的 4 帧（左上=第1帧，右上=第2帧，左下=第3帧，右下=第4帧），来自一部观众第三视角的互动剧。图片2是男主 Rafael 的身份母版（凌乱黑发、颈部荆棘纹身、银链、炭灰色 T 恤、水洗牛仔裤）。图片3是女主的身份母版（正面头像、全身正面、多角度）：很长的冷调灰金层次长发，奶油色长袖开衫，奶油和黑色条纹针织上衣，奶油白阔腿长裤。{allowed}\n' + t[j:]
t = sub(t, '"her_outfit": "女主在这一帧的发色、大衣颜色款式、里面的衣服（看不到女主写 null）"', '"her_outfit": "女主在这一帧的发色、开衫和里面的衣服（看不到女主写 null）"')
t = sub(t, '例如 男主/女主/Selene/陌生人', '例如 男主/女主/配角/陌生人')
t = sub(t, '- her：女主和图片3明显不是同一个人；或她的大衣不是灰褐色长大衣（变成深色外套、西装、双排扣、别的颜色）、大衣脱了、里面不是灰蓝色连衣裙；或发色变成深棕、金黄、变短。', '- her：女主和图片3明显不是同一个人；或她的开衫、条纹上衣换了（剧情写了脱下的除外）；或发色变成深棕、金黄、变短。')
t = sub(t, '- face/outfit：男主不是图片2的人，或不是一身黑色三件套。', '- face/outfit：男主不是图片2的人，或不是炭灰色 T 恤和牛仔裤（剧情写了换装的除外）。')
t = sub(t, '- light：窗外或天空是白天。', '- light：同一地点的光线前后明显跳变，或肤色明显偏橙偏黄。')
t = sub(t, "。披在她身上的毯子、外套之类按剧情允许；他的外套披在她身上时，他只穿马甲衬衫、她外面是黑外套都不算错。\\n", "。披在她身上的毯子、外套之类按剧情允许。\\n")
t = sub(t, "'允许出镜的配角：Selene（深棕色长卷发、祖母绿丝缎长裙），她不是女主。' if 'Selene' in cast else ''", "('允许出镜的配角：' + '、'.join(cast) + '。') if cast else ''")
t = t.replace('Magnus', 'Rafael')
open('qa_guard.py', 'w').write(t)

# ---------- relay
t = open('raf_third_relay.py').read()
t = line(t, '"""Magnus｜午夜车库', '"""Rafael｜这次，不是演的 · 第三视角开放式实时版的本机中转。画面里同时看到 Rafael 和她（女主）。Vivix 和 OpenRouter 的 key 只在本机，网页只拿到口令和视频地址。')
t = sub(t, '用法：mag_third_relay.py <口令> [端口，默认 8894]"""', '用法：raf_third_relay.py <口令> [端口，默认 8901]"""')
t = sub(t, 'PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8894', 'PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8901')
t = line(t, 'TU = json.loads', "TU = L.TU")
t = line(t, 'STAGING_URL = ', "STAGING_URL = TU['staging']  # 两人站位母版（男左女右，灰底），换场那一段没有上一刻画面，靠它定左右")
t = line(t, 'OPEN_FRAME = ', "OPEN_FRAME = D / 'masters' / 'open-key.jpg'  # 开场（吻戏 V7 + 开场 V20）之后切到这一张第三视角关键帧接着演：同一间卧室，男左女右，两张脸都看得到")
t = line(t, 'OPEN_STATE = ', "OPEN_STATE = '周六清晨，合租公寓里 Rafael 的卧室，窗外柔和的晨光。Rafael 坐在床沿、在画面左侧，她靠坐在床头、被子盖到腰、在画面右侧，两人相距一臂多，没有接触；床头柜上有一杯水。昨晚在 Cole 的酒吧，为了摆脱前任 Evan 的纠缠两人假扮情侣、接过吻，他送她回家；刚才他告白了：替她挡 Evan 是演的，想吻她不是，喜欢她有一阵子了，并正式约她，一次真正的约会；她还没有回答。'")
i = t.index("OPEN_NEXT = {"); j = t.index("def log(*a)")
t = t[:i] + """OPEN_NEXT = {'cue': {'zh': '他问完了，没有催，只是等她回答。', 'en': 'He asked. Now he just waits for her answer.'},
             'A': {'zh': '那就正式约我，第一次约会你来安排。', 'en': 'Then ask me properly. You plan our first date.', 'leads_to': '他认真说出第一次约会的安排，并核对店里的预约'},
             'B': {'zh': '我需要时间。先吃早餐，答案晚点给你。', 'en': 'I need time. Breakfast first, the answer later.', 'leads_to': '厨房：他照常做早餐，不拿早餐换答案'}}


""" + t[j:]
t = sub(t, "'place': '酒店地下 VIP 车库', 'place_rounds': 0, 'cards': [], 'stall': 0, 'set': director.OPEN_SET,", "'place': 'Rafael 的卧室', 'place_rounds': 0, 'cards': [], 'stall': 0, 'set': director.OPEN_SET, 'staging': 'bed',")
t = sub(t, "s['place'] = '酒店地下 VIP 车库'; s['place_rounds'] = 0", "s['place'] = 'Rafael 的卧室'; s['place_rounds'] = 0")
t = sub(t, "s['staging'] = (r.get('spec') or {}).get('staging') or s.get('staging') or 'face'", "s['staging'] = (r.get('spec') or {}).get('staging') or s.get('staging') or 'bed'")
t = sub(t, "stage_start=s.get('staging') or 'face'", "stage_start=s.get('staging') or 'bed'")
t = sub(t, "    url_of('OPEN_LAST', D / 'open-last.jpg')\n", '')
t = sub(t, "# 修图的服装是写死的三件套和大衣，会把脱掉的衣服修回去", "# 修图的服装是写死的，会把脱掉的衣服修回去") if "# 修图的服装是写死的三件套和大衣，会把脱掉的衣服修回去" in t else t
t = t.replace('Magnus', 'Rafael')
open('raf_third_relay.py', 'w').write(t)
for f in ('raf_third_sim.py', 'replay.py'):
    t = open(f).read().replace("API = 'http://127.0.0.1:8894'", "API = 'http://127.0.0.1:8901'").replace('mag_third_sim.py', 'raf_third_sim.py'); open(f, 'w').write(t)
print('ok')
