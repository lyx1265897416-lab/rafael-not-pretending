"""选择点背后的待机循环：首尾帧都锁 masters/open-key.jpg，5 秒，静音循环播放。"""
import json, subprocess
import live_common as L
from pathlib import Path
D = Path(__file__).resolve().parent; TU = L.TU
P = ('固定机位，一镜到底：镜头像架在三脚架上，全程不移动、不切镜。首帧和尾帧是同一张画面，两个人的位置、姿势、表情和距离全程和首帧一样，只有很细小的动作：呼吸、眨眼、发丝微动。'
     'Rafael 在画面左侧坐在床沿看着她，她在画面右侧靠在床头看着他。两人都闭着嘴，不说话。' + L.STYLE + '约束：无字幕，无文字，无旁白，没有其他人，没有背景音乐。')
c = L.W1Client(); out = D / 'site/media/IDLE0.mp4'
r = c.run(prompt=P, duration=5, aspect_ratio='9:16', first_frame_image=TU['open_key'], last_frame_image=TU['open_key'], out=str(out))
print('ok', r['job_id'], r.get('generate_seconds'))
