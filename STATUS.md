# Rafael 第三视角实时版（2026-10-31）

开场 = 文档里的吻戏 V7 + 窗边清晨空镜（opening-bridge/）+ 开场 V20（stitch.py，site/media/OPEN.mp4，101.5 秒，720p），播完停在 Rafael 正面近景待机（masters/idle-key.jpg、gen_idle.py）；第 1 轮实时仍从双人关键帧 masters/open-key.jpg 起。封面 = docs/media/poster.jpg。之后全部实时：auto 优先 5+15，轻量 5+10，Vivix ultrafast。
代码从 output/magnus-third-live-v1（V1.9）复制，迁移脚本 port_common.py、port_director.py；PE 规则和流程不变，只换角色、世界观、地点、时间（从清晨往后走，不写死深夜）。
资料包 pack/build_pack.py（飞书内容包 2️⃣ 整理；内容包没有预设成片，K 卡是按事件表排的兜底）。母版 masters.py，地址在 masters/urls.json。
中转 raf_third_relay.py，端口 8901，launchd：com.vicky.realtime.rafael-third、rafael-third-tunnel；日志 logs/relay-public.log、tunnel-public.log；隧道地址 public_url.txt（重启会变）。
测试：tests/smoke.py，首轮 S201238d4d（4 轮）、页面 S2017556a0（1 轮）。人工测试 S0102325ab（13 轮）已进测试记录页（剧集 rafael-third，build_log.py）；还没进 APP。
公开仓库 lyx1265897416-lab/rafael-not-pretending，Pages 从 docs/ 发布（site 是指向 docs 的本地软链，relay 仍读 site）。长期链接带 ?k= 才能实时生成；隧道重启后 sync_relay.py（launchd com.vicky.realtime.rafael-third-sync，日志 logs/sync.log）约 1 分钟内把新地址写进 docs/relay.json 并推送。

## V2.0（2026-11-01，复盘 Vicky 13 轮 S0102325ab）
改动在 director.py（意图、状态连续、state_issues、settle_state）、live_common.py（_mark_shots、key_prompt、bridge/ref）、qa_guard.py（key_frame、seg_state、fix_state）、raf_third_relay.py（关键帧、头像参考、状态质检）。实测会话 S014642140、S010948770、S0118574ba。备份 backup-v19pre/。播放控件 tools/realtime-player/rt-player.js，`apply.py` 同步到其他剧集。

## V2.1（2026-11-01，共用 PE）
director.py、live_common.py、qa_guard.py、raf_third_relay.py 现在由 tools/realtime-third/render.py 从通用模板和本目录 drama_slots.py 合成，不要手改；launchd 重启中转前会自动合成一次。改规则改 tools/realtime-third/templates/，改这部剧的内容改 drama_slots.py。备份 backup-v20pre/。隔离回归 output/rafael-third-v20test（S01541465d、S020104975）。


## V2.4（2026-11-02，复盘 Vicky 22 轮 S184319582）
物品台账、穿脱、动作按字面、穿着参考图、回正不动姿态、关键帧换模型对冲。回归 S193607ba7、S200051ab6、S2218500d2；规则在 tools/realtime-third，决策 D31。
