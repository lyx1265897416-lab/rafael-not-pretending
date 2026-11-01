"""把 pe/third-pe*.xml 推到飞书《通用 PE》里自己的一节「realtime 生成 PE · 观众第三视角版」（放在「realtime 生成 PE」之后、「约束 PE」之前），历史版本全部保留。
- 这一节还没有：在「约束 PE」前一块后面插入 h2 + 说明 + h3「版本（最新）」+ ①–④。
- 版本号相同：原地替换最新版的四个代码块。
- 版本号变了：旧的“（最新）”改成“（历史版本）”并折叠，再在说明后面插入新版本。
只动这一节，不碰第一视角版和其他 PE。用法：python3 pe/push_feishu_third.py（会先跑 build_feishu_third.py）。"""
import json, re, subprocess, sys
from pathlib import Path

D = Path(__file__).resolve().parent.parent
F = 'https://japy03oxab.feishu.cn/wiki/LCW0wI6IviEuvmkH6WSchU8znFQ'
DOC = 'UvsOdh0znoOz3cx69iicVPu9nwg'
H2 = 'realtime 生成 PE · 观众第三视角版'


def cli(*a):
    r = subprocess.run(['lark-cli', *a, '--as', 'user'], capture_output=True, text=True, cwd=D)
    return r.stdout + r.stderr


def doc(): return cli('docs', '+fetch', '--doc', F, '--detail', 'with-ids').replace('\\"', '"')


def section(s):
    a = s.index(f'>{H2}</h2>'); b = s.index('>约束 PE</h2>', a)
    return s[a:b]


def update(cmd, block, content=None):
    a = ['docs', '+update', '--doc', F, '--command', cmd, '--block-id', block]
    if content is not None: a += ['--content', content]
    out = cli(*a)
    if '"result": "success"' not in out: sys.exit(f'{cmd} {block} 失败：{out[:300]}')


def fold(block):
    out = cli('api', 'PATCH', f'/open-apis/docx/v1/documents/{DOC}/blocks/{block}', '--params', '{"document_revision_id":-1}',
              '--data', json.dumps({'update_text_style': {'style': {'folded': True}, 'fields': [3]}}))
    if '"folded": true' not in out and '"ok": true' not in out: sys.exit(f'折叠 {block} 失败：{out[:300]}')


subprocess.run(['python3', str(D / 'pe' / 'build_feishu_third.py')], check=True, stdout=subprocess.DEVNULL)
ver_h3 = re.search(r"VER = '([^']+)'", (D / 'pe' / 'build_feishu_third.py').read_text()).group(1) + '（最新）'
body = (D / 'pe' / 'third-pe-body.xml').read_text(encoding='utf-8'); intro = (D / 'pe' / 'third-pe-intro.xml').read_text(encoding='utf-8')
pres = re.findall(r'<h4>.*?</h4>(<pre .*?</pre>)', body, re.S)
s = doc()
if f'>{H2}</h2>' not in s:  # 第一次：插在「约束 PE」前面那一块后面
    c = s.index('>约束 PE</h2>')
    anchor = re.findall(r'<(?:pre|p|h[1-6]|ul|ol|li|table|callout)[^>]*?\sid="([^"]+)"', s[:c])[-2]  # [-1] 是「约束 PE」标题本身
    update('block_insert_after', anchor, f'<h2>{H2}</h2>' + intro + f'<h3>{ver_h3}</h3>' + body); print('已新建一节', H2, ver_h3)
else:
    seg = section(s)
    latest = re.search(r'<h3 id="([^"]+)">([^<]*（最新）)</h3>', seg)
    if latest and latest.group(2) == ver_h3:
        after = seg[latest.end():]; nxt = re.search(r'<h3 id=', after)
        ids = re.findall(r'<pre[^>]*?id="([^"]+)"', after[:nxt.start()] if nxt else after)[:4]
        for i, pid in enumerate(ids): update('block_replace', pid, pres[i])
        print('同版本更新', ver_h3, len(ids), '块')
    else:
        if latest:
            old = latest.group(2).replace('（最新）', '（历史版本）')
            update('block_replace', latest.group(1), f'<h3>{old}</h3>')
            seg = section(doc()); h = re.search(r'<h3 id="([^"]+)">' + re.escape(old) + '</h3>', seg)
            fold(h.group(1)); print('已折叠', old)
        seg = section(doc())
        p1 = re.search(r'<p id="([^"]+)"', seg).group(1)
        update('block_insert_after', p1, f'<h3>{ver_h3}</h3>' + body); print('已插入新版本', ver_h3)
    seg = section(doc()); p1 = re.search(r'<p id="([^"]+)"', seg).group(1); update('block_replace', p1, intro)
seg = section(doc())
print('这一节的版本：', re.findall(r'<h3 id="[^"]+">([^<]+)</h3>', seg))
