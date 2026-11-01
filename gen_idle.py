"""选择点背后的待机循环：首尾帧都锁 masters/idle-key.jpg（Rafael 正面近景，他问完正在等她回答），5 秒，静音循环播放。"""
import json, subprocess
import live_common as L
from pathlib import Path
D = Path(__file__).resolve().parent; TU = L.TU
P = ('固定机位，一镜到底：镜头像架在三脚架上，全程不移动、不切镜。首帧和尾帧是同一张画面，构图、姿势、表情全程和首帧一样，只有很细小的动作：呼吸、眨眼、发丝微动。'
     'Rafael 一个人在画面里，正面近景，看着镜头旁边的她，闭着嘴不说话，安静地等她回答。' + L.STYLE + '约束：无字幕，无文字，无旁白，画面里只有 Rafael 一个人，没有背景音乐。')
c = L.W1Client(); U = c.upload(D / 'masters/idle-key.jpg')['url']; print('key', U); out = D / 'site/media/IDLE0.mp4'
r = c.run(prompt=P, duration=5, aspect_ratio='9:16', first_frame_image=U, last_frame_image=U, out=str(out))
print('ok', r['job_id'], r.get('generate_seconds'))
