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


## V2.6（2026-11-02，复盘 Vicky 10 轮 S2305031e8）
不拍换衣服过程、不裸露、穿着要求当轮换成、泳装款式写死。回归 S00020492f、S001112a3b、S002018f31、S002348c50、S0027432bd；决策 D32。


## V2.7（2026-11-02，Vicky 截图：两个 Rafael、人飞过画面）
开播前 hard_check，视频参考图不再带全身穿着图，第 2 段查过才开播。回归 S013731a45、S015219bb0；决策 D33。

## 网页播放卡（2026-11-05，同三真四假的修法）
- 结论：Pages 实测开场 101.55 秒用 101.6 秒播完，0 次停顿；实时一轮 15+15（L020822e81）第 1 段 15.04 秒、第 2 段同一刻接上，两段都 0 次停顿，中转记 stall 0。
- 改动（照搬三真四假）：docs/index.html 加 enough/bufEta/warm/pick/srcOf——开场缓冲够前面 8 秒才播；实时段一到就静音、0.0625 倍速在后台“播”（warm），浏览器才会一直下到结尾，开播时退回 0 秒、用回播放器倍速；每段真的缓冲到结尾才开播（不信 readyState 4）；开播时机算上浏览器下载第 2 段的时间。bufEta 比三真四假多一步：速度取“从开始加载算的平均速度（含首包等待）”和“最近测得的速度”里较慢的那个（Meet-me 实测 Vivix CDN 先快后慢，只看后者会提前开播，两段之间停 11.5 秒）。rt-player.js 不改 warm 视频的速度（共用源 tools/realtime-player/rt-player.js 已同步，备份 rt-player.before-warm.js）。改前备份在 backup-antistall/。
- 开场：Pages 上走 HLS 分段（hls.js），原分段 2.08 Mbps，接近 Pages 实测网速 2.2 Mbps → 用压到 1.13 Mbps 的版本重切成 docs/media/open/i2.m3u8 + i2.m4s（改名防缓存混用，旧 i.* 原样留着给缓存里的旧页面）；hls.js 预载从 20 秒改 60 秒——第一次实测 Pages 网速掉到 0.4–0.7 Mbps 持续半分钟，84 秒处停了 0.5 秒，改后（绕开浏览器缓存）分段在 48 秒前全部下完、0 停顿。整部 OPEN.mp4（iPhone 无 MSE 时的退路）也换成 1.13 Mbps 版，GCS 新地址写进 CDN 和 cdn.json。
- 这轮出片慢（第 1 段 145 秒才出），发送到开播 148 秒，是 Vivix 生成慢，不是播放问题。
