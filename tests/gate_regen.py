"""V2.7：验证开播前检查的重新生成和拦下两条路径（hard_check 换成假的，Vivix 真生成）。用法：python3 tests/gate_regen.py"""
import glob, json, sys
from pathlib import Path
D = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(D))
sys.argv = ['x', 'test', '0']
import raf_third_relay as X
r0 = sorted([r for r in (json.load(open(f)) for f in glob.glob(str(D / 'rounds/L*.json'))) if r.get('sid') == 'S015219bb0'], key=lambda r: r['at'])[0]
url = r0['segs'][0]['url']; frame = (r0.get('frame_qa') or {}).get('fixed_url') or r0['key_url']
def run(name, answers):
    calls = []
    def fake(mp4, people, timeout=15):
        calls.append(people); a = answers[min(len(calls) - 1, len(answers) - 1)]
        return {'bad': a, 'kinds': ['people'] if a else [], 'sec': 0}
    X.qa_guard.hard_check = fake
    rid = 'Ltest' + name
    X.R[rid] = {'input': '测试', 'spec': {'seg1': r0['spec']['seg1'], 'seg2': r0['spec']['seg2'], 'cast': [], 'extras': []}, 'segs': [{'dur': 5, 'status': 'generating'}], 'director_at': X.now(), 'id': rid}
    X.save = lambda rid: None
    X.run_seg(rid, 0, 5, r0['prompts'][0], True, frame, X.qa_guard.FACE_URL)
    s = X.R[rid]['segs'][0]
    print(name, 'checks', len(calls), 'status', s.get('status'), 'regen', s.get('gate_regen'), 'url', bool(s.get('url')), 'err', s.get('err'), flush=True)
run('regen', [True, False])
run('block', [True, True, True])
