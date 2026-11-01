#!/bin/zsh
cd "/Users/vicky/Interactive storyline/output/rafael-third-live-v1"
unset HTTPS_PROXY HTTP_PROXY https_proxy http_proxy ALL_PROXY all_proxy
python3 -u opening-bridge/gen_bridge.py
python3 -u gen_idle.py
