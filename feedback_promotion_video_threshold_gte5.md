---
name: 有效播放定义 play_duration >= 5s
description: 项目通用定义：视频"有效播放" = play_duration >= 5（秒）。所有视频相关指标都按此口径过滤 video_play 事件。
type: feedback
originSessionId: 3e756202-bbec-4d6e-8001-c75b8270d6b9
---
项目通用定义：**视频"有效播放" = `play_duration >= 5`（秒）**。所有视频相关指标（人均/平均/总量/完播分母/推广行为里的"有效观影"等）在过滤 `video_behavior_key='video_play'` 事件时都要叠加 `play_duration >= 5`。注意是 `>= 5`，不是 `> 5`。

**Why:** 2026-05-11 用户明确说"目前碰到的情况，基本都要用这个，>=5s 的被称为有效播放"，是项目级"有效播放"的标准定义；早期只把它当成 `dws_user_promotion_behavior_d/h` 校验阈值，范围太窄。

**How to apply:**
- 任何 `video_behavior_key='video_play'` 的计数 / 聚合（不论是 ads/dws/dwm/dwd 层）默认都加 `play_duration >= 5` 过滤
- "当天观看人数"、"播放视频数"、"播放时长"等分母分子都用这个口径
- 例外：`video_behavior_key='video_complete'`（完播）不需要叠加 duration 过滤；点击曝光类事件 (`video_show` 等) 也无关
- 校验 `dws_user_promotion_behavior_d/h` 时 `CASE WHEN max_play >= 5` 同此口径
- 若业务方明确要"宽口径"（点开即算），让用户书面声明再不加；否则默认 >=5
