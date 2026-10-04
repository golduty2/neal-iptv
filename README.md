# neal-iptv

Neal 的 CarTV 精选直播源,70 个频道(CCTV / 卫视 / 香港 / 日本 / 美国)。

| 文件 | 说明 |
|---|---|
| `neal-tv.m3u` | 完整版,分组带国旗 emoji |
| `neal-tv-plain.m3u` | 严格兼容版,去掉注释和 emoji,只保留 `#EXTINF` + URL |

## 在 CarTV 里添加片源

国内直连推荐用 jsDelivr 地址:

```
https://cdn.jsdelivr.net/gh/golduty2/neal-iptv@main/neal-tv.m3u
```

GitHub 原始地址(需要能访问 raw.githubusercontent.com):

```
https://raw.githubusercontent.com/golduty2/neal-iptv/main/neal-tv.m3u
```

如果完整版解析失败,把文件名换成 `neal-tv-plain.m3u` 再试。

## 更新

改完 `.m3u` 直接 push 到 `main`。jsDelivr 对分支地址最多缓存 12 小时,想立刻生效就访问一次:

```
https://purge.jsdelivr.net/gh/golduty2/neal-iptv@main/neal-tv.m3u
```
