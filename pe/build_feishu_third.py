"""第三视角 PE 已收拢成一份（D28）：实际脚本在 tools/realtime-third/build_feishu_third.py。这里只转过去。旧版在 backup-v20pre/。"""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parents[3] / 'tools' / 'realtime-third' / 'build_feishu_third.py'), run_name='__main__')
