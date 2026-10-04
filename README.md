# neal-iptv

Neal 的 CarTV 精选直播源,70 个频道(CCTV / 卫视 / 香港 / 日本 / 美国)。

| 文件 | 说明 |
|---|---|
| `neal-tv-v2.m3u` | **推荐。** v2,63 台,2026-10-04 从国内直连逐台实测通过;只能走代理的 9 台单独放在"🌐 需代理"组 |
| `neal-tv-v2-backup.m3u` | v2 备用源,26 台,与主列表同频道、不同服务器,主源卡顿时切换 |
| `neal-tv.m3u` | v1 原版 70 台(国内直连只有 31 台能播,保留作对照) |
| `neal-tv-plain.m3u` | v1 严格兼容版,去掉注释和 emoji |

## 在 CarTV 里添加片源

国内直连推荐用 jsDelivr 地址(v2 主列表 + 备用源):

```
https://cdn.jsdelivr.net/gh/golduty2/neal-iptv@main/neal-tv-v2.m3u
https://cdn.jsdelivr.net/gh/golduty2/neal-iptv@main/neal-tv-v2-backup.m3u
```

GitHub 原始地址(需要能访问 raw.githubusercontent.com):

```
https://raw.githubusercontent.com/golduty2/neal-iptv/main/neal-tv-v2.m3u
```

## 重测所有源

`tools/check_m3u.py` 对每台做三级检查(播放列表 → 码率变体 → 首个视频分片),直连不走代理。判断国内可用性要在国内服务器上跑:

```
python3 tools/check_m3u.py neal-tv-v2.m3u result.json
```

## 更新

改完 `.m3u` 直接 push 到 `main`。jsDelivr 对分支地址最多缓存 12 小时,想立刻生效就访问一次:

```
https://purge.jsdelivr.net/gh/golduty2/neal-iptv@main/neal-tv.m3u
```
