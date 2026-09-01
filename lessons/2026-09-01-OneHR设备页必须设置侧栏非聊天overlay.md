---
date: 2026-09-01
tags: [onehr, punch, screenshot, telegram, settings]
severity: high
domain: ops
---

# OneHR 设备页截图必须「设置侧栏 + 设备管理」，禁止左聊天 overlay

## 背景

2026-09-01 晚签出：截图右侧是设备管理，**左侧仍是聊天列表**（初儿/机器人群…），不是主人要的「设置 → 设备管理」整页。

## 根因

`privacy → devices` 往返刷新后，Telegram 常停在 **聊天窗口 + 设备页 overlay**，不是完整 Settings 导航。旧校验只看右侧 OCR（登录设备/MacBook…），漏掉了左侧布局错误。

## 正确做法

1. 导航：`tg://settings` → 等待 → `tg://settings/devices` ×2（**不要** privacy 往返）
2. 校验 OCR 必须同时有：
   - 设置侧栏：`设置` / `设备管理` / `隐私与安全` 等
   - 设备页：`登录设备` / `当前设备` 等
3. 若 OCR 有 `聊天`/`搜索` 且无 `设置` → 拒绝上传，删图并重试一次
4. 失败重试仍走 `settings→devices`，不用 `--capture-only`

## 验证

```bash
# 早班好图 OK；09-01 22:17 坏图 FAIL
~/.dc-platform/scripts/onehr_tg_screenshot_validate \
  ~/Desktop/CH/telegram/telegram_devices_20260901_094624.png
~/.dc-platform/scripts/onehr_tg_screenshot_validate \
  ~/Desktop/CH/telegram/telegram_devices_20260901_221705.png
```

## 关联

- `onehr_telegram_devices_screenshot.sh`
- `onehr_tg_screenshot_validate.swift`
- 前序：`2026-08-31-OneHR打卡截图必须是设备管理页.md`
