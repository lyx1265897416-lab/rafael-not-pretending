# Rafael 第三视角实时版（2026-10-31）

开场 = 文档里的吻戏 V7 + 窗边清晨空镜（opening-bridge/）+ 开场 V20（stitch.py，site/media/OPEN.mp4，101.5 秒，720p），播完停在 Rafael 正面近景待机（masters/idle-key.jpg、gen_idle.py）；第 1 轮实时仍从双人关键帧 masters/open-key.jpg 起。封面 = docs/media/poster.jpg。之后全部实时：auto 优先 5+15，轻量 5+10，Vivix ultrafast。
代码从 output/magnus-third-live-v1（V1.9）复制，迁移脚本 port_common.py、port_director.py；PE 规则和流程不变，只换角色、世界观、地点、时间（从清晨往后走，不写死深夜）。
资料包 pack/build_pack.py（飞书内容包 2️⃣ 整理；内容包没有预设成片，K 卡是按事件表排的兜底）。母版 masters.py，地址在 masters/urls.json。
中转 raf_third_relay.py，端口 8901，launchd：com.vicky.realtime.rafael-third、rafael-third-tunnel；日志 logs/relay-public.log、tunnel-public.log；隧道地址 public_url.txt（重启会变）。
测试：tests/smoke.py，首轮 S201238d4d（4 轮）、页面 S2017556a0（1 轮）。没进测试记录页和 APP。
公开仓库 lyx1265897416-lab/rafael-not-pretending，Pages 从 docs/ 发布（site 是指向 docs 的本地软链，relay 仍读 site）。长期链接带 ?k= 才能实时生成；隧道重启后 sync_relay.py（launchd com.vicky.realtime.rafael-third-sync，日志 logs/sync.log）约 1 分钟内把新地址写进 docs/relay.json 并推送。
